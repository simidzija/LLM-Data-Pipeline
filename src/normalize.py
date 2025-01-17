"""
Core functionality to normalize Wikipedia html. 

Contains:
  - Normalizer: class for normalizing Wikipedia text
  - normalize_jsonl: function for normalizing text stored in jsonl file. 
    Can utilize multiple processors.
"""

# Standard library
import json
import re
import sys
import unicodedata
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Iterator, TextIO

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger

class Normalizer:
    """Class for normalizing Wikipedia text."""
    def __init__(self) -> None:
        # Handlers
        self.HANDLERS = [
            self.unicode_handler,
            self.whitespace_handler,
            self.quote_handler,
            self.dash_handler,
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
        """Normalize text according to the NFC Unicode normalization form."""
        text = unicodedata.normalize('NFC', text)
        return text

    def whitespace_handler(self, text: str) -> str:
        """Normalize whitespace."""
        # normalize line endings to \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # remove unwanted control characters: ASCII 0-8, 11-31, and 127
        text = re.sub(r'[\x00-\x08\x0B-\x1F\x7F]', '', text)

        # normalize special space characters to regular space or empty string
        text = re.sub(r'[\u00A0\u2002\u2003\u2009\u200A\u3000\t\f]', ' ', text)
        text = re.sub(r'\u200B', '', text)

        # replace multi-spaces with single space (except at beginning of line)
        text = re.sub(r'(?<!^)(?<!\n) {2,}', ' ', text)

        # replace \n...\n, where ... has spaces or \ns, with \n\n
        text = re.sub(r'(\n\s*)+\n', r'\n\n', text)

        # strip leading and trailing whitespace
        text = text.strip()

        return text

    def quote_handler(self, text: str) -> str:
        """Normalize quotes."""
        # replace double curly quotes with double straight quotes
        text = re.sub(r'[\u201C\u201D]', '\u0022', text)

        # replace single curly quotes with single straight quotes
        text = re.sub(r'[\u2018\u2019]', '\u0027', text)

        return text
    
    def dash_handler(self, text: str) -> str:
        """Normalize dashes."""
        # replace minus with hyphen-minus
        text = re.sub(r'\u2212', '\u002D', text)

        return text
    


# Multiprocessing functions

def get_iterable(file: TextIO, 
                 total_lines: int, 
                 len_cutoff: int) -> Iterator[int, str, int, int]:
    """Generator of worker() arguments."""
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines, len_cutoff)

def worker_init() -> None:
    """Initializes worker."""
    global normalizer
    normalizer = Normalizer()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, 
           line: str, 
           total_lines: int, 
           len_cutoff: int) -> tuple[str, list[str]]:
    """Normalizes text in jsonl entry given by line."""

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
        if len(normalized_text) >= len_cutoff:
            normalized_text_list.append(normalized_text)
    
    return url, normalized_text_list



# Main entry points

def normalize_jsonl(inpath_list: list[str] | str, 
                    outpath: str, 
                    processes: int, 
                    len_cutoff: int=-1) -> None:
    """Normalize text stored in .jsonl file"""

    normalizer = Normalizer()
    normalizer.logger.info(f"Started normalizing {inpath_list}")

    # create list of input files
    if isinstance(inpath_list, list):
        pass
    elif isinstance(inpath_list, str):
        inpath_list = [inpath_list]
    else:
        raise ValueError(f'inpath_list must be string or list but got type {type(inpath_list)}')

    # read files
    for inpath in inpath_list:
        with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
            normalizer.logger.info(f"Started normalizing {inpath}")
            total_lines = sum(1 for _ in infile)
            infile.seek(0)

            with Pool(processes=processes, initializer=worker_init) as pool:
                iterable = get_iterable(infile, total_lines, len_cutoff)
                for url, text_list in pool.starmap(worker, iterable):
                    entry = {'url': url, 'text_list': text_list}
                    json.dump(entry, outfile)
                    outfile.write('\n')
            normalizer.logger.info(f"Finished normalizing {inpath}")
        
    normalizer.logger.info(f"Finished normalizing {inpath_list}\n\n")
