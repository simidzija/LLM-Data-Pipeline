import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from deduplicate import Deduplicator

if __name__ == "__main__":
    inpath = str(ROOT/'data'/'normalize_data.jsonl')
    outpath = str(ROOT/'data'/'deduplicate_data.jsonl')

    deduplicator = Deduplicator(inpath, 
                                outpath,
                                gram_len=5,
                                signature_len=128,
                                band_size=16,
                                similarity_threshold=0.8)

    deduplicator.deduplicate()