import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from bpe_freqdict import create_freq_dict_from_jsonl

if __name__ == "__main__":
    # Corpus
    corpus_path = str(ROOT/'data'/'segment_data.jsonl')

    # Create and store word frequency dict
    freq_dict_path = str(ROOT/'data'/'freq_dict.jsonl')
    create_freq_dict_from_jsonl(corpus_path, freq_dict_path, processes=10)