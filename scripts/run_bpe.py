import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from bpe import create_vocab

if __name__ == "__main__":
    freq_dict_path = str(ROOT/'data'/'freq_dict_5.jsonl')
    vocab_path = str(ROOT/'data'/'vocab_5.json')
    create_vocab(freq_dict_path, vocab_path)


