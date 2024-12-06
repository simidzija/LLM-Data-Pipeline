import sys
import json
from pathlib import Path
from multiprocessing import Pool, current_process

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Normalizer:
    def __init__(self):
        # Handlers
        self.HANDLERS = [
            self.unicode_handler,
            self.whitespace_handler,
        ]

        # Logger
        self.logger = Logger('normalize')

    def normalize(self, text: str) -> str:
        """Normalize text."""
        for handler in self.HANDLERS:
            text = handler(text)

        return text

    ################################  Handlers  ################################

    def unicode_handler(self, text: str) -> str:
        # TODO: Implement
        return text

    def whitespace_handler(self, text: str) -> str:
        # TODO: Implement
        return text


# Multiprocessing functions

def get_iterable(file, total_lines):
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines)

def worker_init():
    global normalizer
    normalizer = Normalizer()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, line: str, total_lines: int) -> list:
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    normalizer.logger.info(f"Normalizing page {page_num} / {total_lines} : {url}")

    # normalize
    normalized_text_list = []
    for text in text_list:
        normalized_text = normalizer.normalize(text)
        normalized_text_list.append(normalized_text)
    
    return url, normalized_text_list



# Main entry point

def normalize_jsonl(inpath: str, outpath: str, processes: int):
    """Normalize text stored in .jsonl files"""
    normalizer = Normalizer()
    normalizer.logger.info(f"Started normalizing {inpath}")

    # read files
    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)

        with Pool(processes=processes, initializer=worker_init) as pool:
            iterable = get_iterable(infile, total_lines)
            for url, text_list in pool.starmap(worker, iterable):
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, outfile)
                outfile.write('\n')
    
    normalizer.logger.info(f"Finished normalizing {inpath}\n\n")
