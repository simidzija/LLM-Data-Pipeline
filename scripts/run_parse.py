import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from parse import parse_jsonl

if __name__ == "__main__":

    ############################  parse jsonl file  ############################

    # parsing parse_data_1.jsonl using 1 process takes ~14m
    # parsing parse_data_2.jsonl using 10 processes takes ~3m5s
    # parsing parse_data_3.jsonl using 10 processes takes ~2m39s
    # parsing parse_data_4.jsonl using 10 processes takes ~2m37s

    raw_path = str(ROOT/'data/crawl_data_4.jsonl')
    parsed_path = str(ROOT/'data/parse_data_4.jsonl')

    parse_jsonl(raw_path, parsed_path, processes=10)
    
    
    ############################  parse single html  ###########################

    # with open('/Users/petar/Documents/llmdata/data/crawl_data_5.jsonl', 'r') as file:
    #     for _ in range(9):
    #         line = json.loads(next(iter(file)))
    #     url = line['url']
    #     html = line['text']

    # parser = parse.Parser()
    # parser.parse(html)
