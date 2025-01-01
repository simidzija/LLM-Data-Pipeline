import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from deduplicate import Deduplicator

if __name__ == "__main__":
    inpath = str(ROOT/'data'/'normalize_data_5_fake.jsonl')
    outpath = str(ROOT/'data'/'deduplicate_data_5.jsonl')

    deduplicator = Deduplicator(inpath, 
                                outpath,
                                gram_len=5,
                                signature_len=128,
                                band_size=16,
                                similarity_threshold=0.9)

    # deduplicator.deduplicate()

    deduplicator.min_hash_jsonl()

    deduplicator.lsh_create_dicts()

    deduplicator.lsh_get_duplicate_candidates()
    print(deduplicator.lsh_duplicate_candidates)

