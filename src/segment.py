"""
Core functionality to segment text into sentences. 

Accurate sentence segmentation requires implementing many heuristics, e.g. to 
handle abbrevitions properly. To avoid getting too sidetracked with this small 
piece of the data preparation pipeline, I decided to use an external library 
(spacy) to perform the sentence segmentation. I leave the implementation of a 
sentence segmenter from scratch for a future project.

Contains:
  - Segmenter: class for segmenting text into sentences.
  - segment_jsonl: function for segmenting text stored in jsonl file. 
    Can utilize multiple processors.
"""

# Standard library
import json
import sys
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Iterator, TextIO

# Third-party
import spacy

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger


class Segmenter:
    """Class for segmenting text into sentences."""
    def __init__(self):
        # spacy NLP object
        self.nlp = spacy.load("en_core_web_sm")

        # Logger 
        self.logger = Logger('segment')

    def segment(self, text: str) -> list[str]:
        doc = self.nlp(text)
        return [str(sent) for sent in doc.sents]

# Multiprocessing functions

def get_iterable(file: TextIO, 
                 total_lines: int, 
                 omit_duplicates: bool) -> Iterator[int, str, int, bool]:
    """Generator of worker() arguments."""
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines, omit_duplicates)

def worker_init() -> None:
    """Initializes worker."""
    global segmenter
    segmenter = Segmenter()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, 
           line: str, 
           total_lines: int, 
           omit_duplicates: bool) -> tuple[str, list[list[str]]]:
    """Segments texts in jsonl entry given by line."""
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    segmenter.logger.info(f"Segmenting page {page_num} / {total_lines}: {url}")

    # segment
    segmented_text_list = []
    for text in text_list:
        if omit_duplicates and text == "<DUPLICATE_REMOVED>":
            continue
        segmented_text_list.append(segmenter.segment(text))

    return url, segmented_text_list


# Main entry point

def segment_jsonl(inpath: str, 
                  outpath: str, 
                  processes: int, 
                  omit_duplicates: bool=True) -> None:
    """Segment text stored in .jsonl file into sentences"""

    segmenter = Segmenter()
    segmenter.logger.info(f"Started segmenting {inpath}")

    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)

        with Pool(processes=processes, initializer=worker_init) as pool:
            iterable = get_iterable(infile, total_lines, omit_duplicates)
            for url, text_list in pool.starmap(worker, iterable):
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, outfile)
                outfile.write('\n')

        segmenter.logger.info(f"Finished segmenting {inpath}")
