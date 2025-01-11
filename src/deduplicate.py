import mmh3
import sys
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Deduplicator:
    def __init__(self, inpath, outpath, gram_len, signature_len, band_size, similarity_threshold):
        # arguments
        self.inpath = inpath
        self.outpath = outpath
        self.gram_len = gram_len
        self.signature_len = signature_len
        self.band_size = band_size
        self.similarity_threshold = similarity_threshold
        assert signature_len % band_size == 0, f"band_size ({band_size}) does not divide signature_len ({signature_len})"
        self.n_bands = signature_len // band_size

        # storage containers
        self.min_hashes = {}
        self.lsh_dicts = [defaultdict(set) for _ in range(self.n_bands)]
        self.lsh_duplicate_candidates = []
        self.texts_to_remove_set = set()
        self.texts_to_remove_dict = defaultdict(list)

        # hash functions
        self.min_hash_fns = [lambda x, s=s: mmh3.hash(x, s) for s in range(signature_len)]
        self.lsh_hash_fn = lambda x, s=signature_len: mmh3.hash(x, s)

        # Logger
        self.logger = Logger('deduplicate')

    def deduplicate(self):
        """Deduplicates infile and writes to outfile"""
        self.logger.info(f'Start deduplicating {self.inpath}')

        # MinHash
        self.logger.info(f'Stared MinHash with gram_len = {self.gram_len}, signature_len = {self.signature_len}')
        self.min_hash_jsonl()

        # Locality-Sensitive Hashing
        self.logger.info(f'Start Locality-Sensitive Hashing')
        self.logger.info(f'Create LSH dicts.')
        self.lsh_create_dicts()
        self.logger.info(f'Determine duplicate candidates')
        self.lsh_get_duplicate_candidates()

        # Texts to remove dict
        self.logger.info(f'Create texts-to-remove dict')
        self.get_texts_to_remove()

        # Create outfile
        self.logger.info(f'Start writing to outfile {self.outfile}')
        with open(self.inpath, 'r') as infile, open(self.outpath, 'w') as outfile:
            for line in infile:
                entry = json.loads(line)
                url = entry['url']
                if url in self.texts_to_remove_dict:
                    text_list = entry['text_list']
                    idxs = self.texts_to_remove_dict[url]
                    for i in idxs:
                        self.logger.info(f'REMOVE DUPLICATE: item {i} in {url}')
                        text_list[i] = "<DUPLICATE_REMOVED>"
                json.dump(entry, outfile)
                outfile.write('\n')
        self.logger.info(f'Finish dedupling {self.inpath}\n')
        
                    
    def min_hash_jsonl(self):
        """Creates min_hashes dict"""
        with open(self.inpath, 'r') as infile:
            total_lines = sum(1 for _ in infile)
            infile.seek(0)
            for line_num, line in enumerate(infile):
                entry = json.loads(line)
                url = entry['url']
                text_list = entry['text_list']

                self.logger.info(f'MinHash article {line_num:6d}/{total_lines}: {url}')

                self.min_hashes[url] = [self.min_hash(text) for text in text_list]

    def min_hash(self, text: str) -> list[int]:
        """Return MinHash signature of text"""
        assert len(text) >= self.gram_len, f"len(text) ({len(text)}) cannot be smaller than gram_len ({self.gram_len})"

        n_grams = set()
        for start in range(len(text) - self.gram_len + 1):
            end = start + self.gram_len
            n_gram = text[start:end]
            n_grams.add(n_gram)

        signature = [min(map(fn, n_grams)) for fn in self.min_hash_fns]

        return signature


    def lsh_create_dicts(self):
        """Creates lsh_dicts list"""
        # loop over urls
        total_lines = len(self.min_hashes)
        for line_num, (url, signatures) in enumerate(self.min_hashes.items()):
            self.logger.info(f'Updating LSH dicts with article {line_num:6d}/{total_lines}: {url}')
            # loop over signatures
            for idx, signature in enumerate(signatures):
                # loop over bands
                for b, lsh_dict in zip(range(self.n_bands), self.lsh_dicts):
                    # define band
                    start = b * self.band_size
                    end = start + self.band_size
                    band = signature[start:end]
                    band_bytes = str(band).encode()
                    
                    # compute hash val
                    hash_val = self.lsh_hash_fn(band_bytes)

                    # add to band dict
                    lsh_dict[hash_val].add((url, idx))

    def lsh_get_duplicate_candidates(self):
        """Create duplicate_candidates list"""
        total_dicts = len(self.lsh_dicts)
        for dict_num, lsh_dict in enumerate(self.lsh_dicts):
            self.logger.info(f'Updating duplicate_candates list with LSH dict {dict_num}/{total_dicts}')
            for texts in lsh_dict.values():
                if len(texts) > 1:
                    self.lsh_duplicate_candidates.append(texts)

    def get_texts_to_remove(self):
        """Convert duplicate_candidates list to dict of texts to remove"""
        for texts in self.lsh_duplicate_candidates:
            texts_lst = list(texts)
            for i1 in range(len(texts) - 1):
                text1 = texts_lst[i1]
                for i2 in range(i1 + 1, len(texts)):
                    text2 = texts_lst[i2]
                    if (text1 not in self.texts_to_remove_set and 
                        text2 not in self.texts_to_remove_set and
                        self.are_duplicates(text1, text2)):
                        self.texts_to_remove_set.add(text1)
        
        # create texts_to_remove_dict
        for url, idx in self.texts_to_remove_set:
            self.texts_to_remove_dict[url].append(idx)

    def are_duplicates(self, text1: tuple[str, int], text2: tuple[str, int]) -> bool:
        """Returns True if text1 and text2 are determined to be duplicates"""
        url1, idx1 = text1
        url2, idx2 = text2

        sig1 = self.min_hashes[url1][idx1]
        sig2 = self.min_hashes[url2][idx2]

        jaccard_sim = self.jaccard(sig1, sig2)
        print(jaccard_sim)

        return jaccard_sim > self.similarity_threshold

    def jaccard(self, sig1: list[int], sig2: list[int]) -> float:
        """Returns Jaccard similarity of signatures sig1 and sig2"""
        n_same = sum([n1 == n2 for n1, n2 in zip(sig1, sig2)])
        n_total = len(sig1)
        return n_same / n_total


    


        