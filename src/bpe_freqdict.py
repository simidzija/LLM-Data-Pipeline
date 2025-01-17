"""
Core functionality for creating the BPE word frequency dictionary. 

This consitutes part 1/3 of the byte pair encoding (BPE) tokenization pipeline:
  1. Create word frequency dict
  2. Create vocab
  3. Tokenize text

Contains:
  - FreqDictCreator: class for creating BPE word frequency dictionary.
  - create_freq_dict_from_jsonl: function for creating word frequency dict from
    text stored in jsonl file. Can utilize multiple processors.
"""

# Standard library
import json
import sys
from collections import Counter
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Iterator

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger


class FreqDictCreator:
    """Class for creating BPE word frequency dictionary."""
    def __init__(self) -> None:
        # Logger 
        self.logger = Logger('freqdict')

    def create_freq_dict(self, text: str) -> Counter[str, int]:
        """Creates word frequency dictionary from text."""
        return Counter(text.split(sep=" "))


# Multiprocessing functions

def get_iterable(file, total_lines: int) -> Iterator[int, str, int]:
    """Generator of worker() arguments."""
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines)

def worker_init() -> None:
    """Initializes worker."""
    global freq_dict_creator
    freq_dict_creator = FreqDictCreator()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, line: str, total_lines: int) -> Counter[str, int]:
    """Creates BPE word freq dict for texts in jsonl entry given by line."""
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    freq_dict_creator.logger.info(f"Getting freq dict from page {page_num} / {total_lines}: {url}")

    # Get freq dict
    freq_dict = Counter()
    for section in text_list:
        for sentence in section:
            freq_dict.update(freq_dict_creator.create_freq_dict(sentence))

    return freq_dict



# Main entry point

def create_freq_dict_from_jsonl(corpus_path: str, 
                                freq_dict_path: str, 
                                processes: int) -> None:
    """Create word frequency dict for text in jsonl file"""

    freq_dict_creator = FreqDictCreator()
    freq_dict_creator.logger.info(f"Started creating word frequency dict from corpus {corpus_path}")

    # Construct freq dict
    total_freq_dict = Counter()
    with open(corpus_path, 'r') as file:
        total_lines = sum(1 for _ in file)
        file.seek(0)

        with Pool(processes=processes, initializer=worker_init) as pool:
            iterable = get_iterable(file, total_lines)
            for freq_dict in pool.starmap(worker, iterable):
                total_freq_dict.update(freq_dict)

    # Write freq dict to file
    with open(freq_dict_path, 'w') as file:
        json.dump(total_freq_dict, file)

    freq_dict_creator.logger.info(f"Finished creating word frequency dict from corpus {corpus_path}")
