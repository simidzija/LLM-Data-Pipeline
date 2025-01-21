"""
Script to create BPE vocabulary. 

Uses the functionality of bpe_vocab.py.
"""

# Standard library
import sys
from pathlib import Path

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from bpe_vocab import increase_vocab

if __name__ == "__main__":
    freq_dict_path = str(ROOT/'data'/'freq_dict.jsonl')
    vocab_path = str(ROOT/'data'/'vocab.json')

    increase_vocab(freq_dict_path, vocab_path, size=20000, processes=10)




