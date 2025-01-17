import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from bpe_tokenize import tokenize_jsonl

if __name__ == "__main__":
    inpath = str(ROOT/'data'/'segment_data_5.jsonl')
    outpath = str(ROOT/'data'/'tokenize_data_5.jsonl')
    vocab_path = str(ROOT/'data'/'vocab_5.json')

    tokenize_jsonl(inpath, outpath, vocab_path, processes=10)

