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
        self.inpath = inpath
        self.outpath = outpath
        self.gram_len = gram_len
        self.signature_len = signature_len
        self.band_size = band_size
        self.similarity_threshold = similarity_threshold
        assert signature_len % band_size == 0, f"band_size ({band_size}) does not divide signature_len ({signature_len})"
        self.n_bands = signature_len // band_size

        self.min_hashes = {}
        self.lsh_dicts = [defaultdict(set) for _ in range(self.n_bands)]
        self.lsh_duplicate_candidates = []
        self.texts_to_remove = {}

        self.min_hash_fns = [lambda x, s=s: mmh3.hash(x, s) for s in range(signature_len)]
        self.lsh_hash_fn = lambda x, s=signature_len: mmh3.hash(x, s)

    def deduplicate(self):
        """Deduplicates infile and writes to outfile"""

        # MinHash
        self.min_hash_jsonl()

        # Locality-Sensitive Hashing
        self.lsh_create_dicts()
        self.lsh_get_duplicate_candidates()

        # Texts to remove dict
        self.get_texts_to_remove()

        # Create outfile
        with open(self.inpath, 'r') as infile, open(self.outpath, 'w') as outfile:
            for line in infile:
                entry = json.loads(line)
                url = entry['url']
                if url in self.texts_to_remove:
                    text_list = entry['text_list']
                    idxs = self.texts_to_remove[url]
                    for i in idxs:
                        text_list[i] = "<DUPLICATE_REMOVED>"
                json.dump(entry, outfile)
                outfile.write('\n')
                    
    def min_hash_jsonl(self):
        """Creates min_hashes dict"""
        with open(self.inpath, 'r') as infile:
            for line in infile:
                entry = json.loads(line)
                url = entry['url']
                text_list = entry['text_list']

                self.min_hashes[url] = [self.min_hash(text) for text in text_list]

    def min_hash(self, text: str) -> list[int]:
        """Return MinHash signature of text"""
        assert len(text) >= self.gram_len, f"len(text) ({len(text)}) cannot be smaller than gram_len ({self.gram_len})"

        n_grams = set()
        for start in range(len(text) - self.gram_len + 1):
            end = start + self.gram_len
            n_gram = text[start:end]
            n_grams.add(n_gram)

        signature = []
        for fn in self.min_hash_fns:
            min_hash_val = min(map(fn, n_grams))
            signature.append(min_hash_val)

        return signature


    def lsh_create_dicts(self):
        """Creates lsh_dicts list"""
        # loop over urls
        for url, signatures in self.min_hashes.items():
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
        for lsh_dict in self.lsh_dicts:
            for texts in lsh_dict.values():
                if len(texts) > 1:
                    self.lsh_duplicate_candidates.append(texts)

    def get_texts_to_remove(self):
        """Convert duplicate_candidates list to dict of texts to remove"""
        for texts in self.lsh_duplicate_candidates:
            pass
        


        