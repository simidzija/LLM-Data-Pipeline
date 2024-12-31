import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from deduplicate import Deduplicator

if __name__ == "__main__":
    inpath = str(ROOT/'data'/'normalize_data_5.jsonl')
    outpath = str(ROOT/'data'/'deduplicate_data_5.jsonl')

    # deduplicator = Deduplicator(inpath, outpath, gram_size, sig_len, bin_size, sim_threshold)
    # deduplicator.deduplicate()


    deduplicator.min_hash()
    print(deduplicator.min_hashes)

    # deduplicator.lsh_create_dicts()
    # print(deduplicator.lsh_dicts)

    # deduplicator.lsh_get_pars_to_remove()
    # print(deduplicator.pars_to_remove)

