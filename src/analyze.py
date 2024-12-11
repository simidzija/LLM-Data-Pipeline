import sys
import json
from pathlib import Path
from multiprocessing import current_process

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Analyzer:
    def __init__(self):
        pass

    def analyze(self, text: str, chars: list[str]) -> dict[str, int]:
        """Analyze text for characters in chars, returning freq dict."""
        pass


# Multiprocessing functions

def get_iterable(file, total_lines):
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines)

def worker_init():
    global analyzer
    analyzer = Analyzer()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, line: str, total_lines: int, chars: list[str]) -> list:
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    analyzer.logger.info(f"Analyzing page {page_num} / {total_lines} : {url}")

    # analyze
    analyzed_text_list = []
    for text in text_list:
        analyzed_text = analyzer.analyze(text, chars)
        analyzed_text_list.append(analyzed_text)
    
    return url, analyzed_text_list



# Main entry points

# def analyze_jsonl(inpath_list: list[str] | str, outpath: str, chars: list[str], processes: int) -> dict[str, int]:
#     """Analyze text stored in .jsonl file, returning freq dict for chars."""
#     analyzer = Analyzer()
#     analyzer.logger.info(f"Started analyzing {inpath_list} for {chars}")

#     # create list of input files
#     if isinstance(inpath_list, list):
#         pass
#     elif isinstance(inpath_list, str):
#         inpath_list = [inpath_list]
#     else:
#         raise ValueError(f'inpath_list must be string or list but got type {type(inpath_list)}')

#     # read files
#     for inpath in inpath_list:
#         with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
#             normalizer.logger.info(f"Started normalizing {inpath}")
#             total_lines = sum(1 for _ in infile)
#             infile.seek(0)

#             with Pool(processes=processes, initializer=worker_init) as pool:
#                 iterable = get_iterable(infile, total_lines)
#                 for url, text_list in pool.starmap(worker, iterable):
#                     entry = {'url': url, 'text_list': text_list}
#                     json.dump(entry, outfile)
#                     outfile.write('\n')
#             normalizer.logger.info(f"Finished normalizing {inpath}")
        
#     normalizer.logger.info(f"Finished normalizing {inpath_list}\n\n")


