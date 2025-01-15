import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from bpe_vocab import Vocab

if __name__ == "__main__":
    freq_dict_path = str(ROOT/'data'/'freq_dict_5.jsonl')
    vocab_path = str(ROOT/'data'/'vocab_5.json')
    vocab = Vocab(freq_dict_path, vocab_path)

    print(f'Initial vocab size: {len(vocab.vocab)}')
    vocab.increase_vocab(size=1000)



