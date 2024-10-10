import yaml
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

import crawl

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = load_config(str(ROOT/'config/settings.yaml'))
    urls = config['crawl_seeds']
    crawler = crawl.Crawler(urls)
    crawler.download_content(urls[0])

