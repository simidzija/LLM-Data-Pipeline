import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import parse


if __name__ == "__main__":
    # raw_path = str(ROOT/'data/crawl_data_5.jsonl')
    # parsed_path = str(ROOT/'data/parse_data_5.jsonl')

    # parser = parse.Parser()
    # parser.parse_jsonl(raw_path, parsed_path)
    

    with open('/Users/petar/Documents/llmdata/data/crawl_data_5.jsonl', 'r') as file:
        for _ in range(11):
            line = json.loads(next(iter(file)))
        url = line['url']
        html = line['text']

    parser = parse.Parser()
    parser.parse(html)