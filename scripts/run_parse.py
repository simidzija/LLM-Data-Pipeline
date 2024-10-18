import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import parse


if __name__ == "__main__":
    data_sample_filepath = str(ROOT/'data/crawl_data_sample.txt')
    
    

