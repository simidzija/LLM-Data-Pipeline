import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import parse


if __name__ == "__main__":
    raw_path = str(ROOT/'data/crawl_data_5.jsonl')
    parsed_path = str(ROOT/'data/parse_data_5.jsonl')

    parser = parse.Parser()
    parser.parse_jsonl(raw_path, parsed_path)


