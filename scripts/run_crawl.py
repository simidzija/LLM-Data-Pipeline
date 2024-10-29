import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import crawl
import utils


if __name__ == "__main__":
    data_filepath = str(ROOT/'data/crawl_data.jsonl')
    queue_filepath = str(ROOT/'data/crawl_queue.txt')
    

    #################   Start crawling   #################

    config = utils.load_yaml(str(ROOT/'config/config.yaml'))
    seeds = config['crawl_seeds']
    crawler = crawl.Crawler(data_filepath, queue_filepath, reset=True, seeds=seeds)
    crawler.crawl(max_pages=10)



    #################   Continue crawling   #################

    # crawler = crawl.Crawler(data_filepath, queue_filepath, reset=False)
    # crawler.crawl(max_pages=100)

    

