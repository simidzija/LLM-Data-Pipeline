import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from normalize import normalize_jsonl

if __name__ == "__main__":
    inpath = str(ROOT/'data/parse_data_5.jsonl')
    outpath = str(ROOT/'data/normalize_data_5.jsonl')
    normalize_jsonl(inpath, outpath, processes=10)
    