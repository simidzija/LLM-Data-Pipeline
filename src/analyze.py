import sys
import json
from pathlib import Path
from multiprocessing import Pool, current_process
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Analyzer:
    def __init__(self):
        self.logger = Logger('analyze')

    def analyze(self, text: str, chars: list[str] | tuple[str] | set[str]) -> Counter:
        """Analyze text, returning character Counter."""
        chars = set(chars)
        counter = Counter(c for c in text if c in chars)
        return counter


# Multiprocessing functions

def get_iterable(file, total_lines, chars):
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines, chars)

def worker_init():
    global analyzer
    analyzer = Analyzer()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, line: str, total_lines: int, chars: list[str]) -> Counter:
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    analyzer.logger.info(f"Analyzing page {page_num} / {total_lines} : {url}")

    # analyze
    counter = Counter()
    for text in text_list:
        counter.update(analyzer.analyze(text, chars))
    
    return counter



# Main entry points

def analyze_jsonl(inpath_list: list[str] | str, chars: list[str], processes: int) -> Counter:
    """Analyze text stored in .jsonl file(s), returning Counter for chars."""
    analyzer = Analyzer()
    analyzer.logger.info(f"Started analyzing {inpath_list} for {chars}")

    # create list of input files
    if isinstance(inpath_list, list):
        pass
    elif isinstance(inpath_list, str):
        inpath_list = [inpath_list]
    else:
        raise ValueError(f'inpath_list must be string or list but got type {type(inpath_list)}')
    
    # Counter
    counter = Counter()

    # read files
    for inpath in inpath_list:
        with open(inpath, 'r') as infile:
            analyzer.logger.info(f"Started analyzing {inpath} for {chars}")
            total_lines = sum(1 for _ in infile)
            infile.seek(0)

            with Pool(processes=processes, initializer=worker_init) as pool:
                iterable = get_iterable(infile, total_lines, chars)
                for article_counter in pool.starmap(worker, iterable):
                    counter.update(article_counter)
            analyzer.logger.info(f"Finished analyzing {inpath} for {chars}")
        
    analyzer.logger.info(f"Finished analyzing {inpath_list} for {chars}\n\n")

    return counter


