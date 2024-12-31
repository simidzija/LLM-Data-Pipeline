import mmh3
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Deduplicator:
    def __init__(self, inpath, outpath, gram_size, sig_len, bin_size, sim_threshold):
        self.inpath = inpath
        self.outpath = outpath
        self.gram_size = gram_size
        self.sig_len = sig_len
        self.bin_size = bin_size
        self.threshold = sim_threshold

        self.min_hashes = {}
        self.lsh_dicts = []
        self.pars_to_remove = {}

    def deduplicate(self):
        """Deduplicates infile and writes to outfile"""

        # MinHash
        self.min_hash()

        # Locality-Sensitive Hashing
        self.lsh_create_dicts()
        self.lsh_get_pars_to_remove()

        # Create outfile
        with open(self.outpath, 'r') as infile, open(self.outpath, 'w') as outfile:
            for line in infile:
                entry = json.loads(line)
                url = entry['url']
                if url in self.pars_to_remove:
                    text_list = entry['text_list']
                    idxs = self.pars_to_remove[url]
                    for i in idxs:
                        text_list[i] = "<DUPLICATE_REMOVED>"
                json.dump(entry, outfile)
                outfile.write('\n')
                    


    def min_hash(self):
        """Creates min_hashes dict"""
        pass

    def lsh_create_dicts(self):
        """Creates lsh_dicts list"""
        pass

    def lsh_get_pars_to_remove(self):
        """Create pars_to_remove dict"""
        pass


        