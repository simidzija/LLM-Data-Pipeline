import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import parse


if __name__ == "__main__":
    text_sample_filepath = str(ROOT/'data/crawl_text_sample.html')
    with open(text_sample_filepath, 'r') as file:
        html = file.read()

    parser = parse.Parser()



