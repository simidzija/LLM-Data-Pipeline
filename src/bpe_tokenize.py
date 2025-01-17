"""
Core functionality for BPE tokenization. 

This consitutes part 3/3 of the byte pair encoding (BPE) tokenization pipeline:
  1. Create word frequency dict
  2. Create vocab
  3. Tokenize text

Contains:
  - Tokenizer: class for BPE tokenization.
  - tokenize_jsonl: function for BPE tokenization of text stored in jsonl file. 
    Can utilize multiple processors.
"""

# Standard library
import json
import sys
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Iterator

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger


class Tokenizer:
    """Class for BPE tokenization."""
    def __init__(self, vocab_path: str) -> None:
        self.vocab_path = vocab_path
        self.load_vocab()
        
        # Logger 
        self.logger = Logger('tokenize')

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text."""
        # tokenized text list
        tokenized = []

        # loop over text
        start = 0
        while start < len(text):
            # find longest token
            token = ''
            end = start
            while end < len(text):
                new_token = token + text[end]
                if new_token in self.vocab:
                    token = new_token
                    end += 1
                else:
                    break

            # append token
            tokenized.append(token)

            # update start
            start = end
                
        return tokenized

    def load_vocab(self) -> None:
        """Loads vocab from file at self.vocab_path into set self.vocab."""
        with open(self.vocab_path, 'r') as f:
            self.vocab = set(json.load(f))

# Multiprocessing functions

def worker_init(vocab_path: str) -> None:
    """Initializes worker."""
    # Print current process
    process = current_process()
    print(f'Initialized {process.name}')

    # Create tokenizer for this process
    global tokenizer
    tokenizer = Tokenizer(vocab_path)
    
def get_iterable(file, total_lines: int) -> Iterator[int, str, int]:
    """Generator of worker() arguments."""
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines)

def worker(page_num: int, 
           line: str, 
           total_lines: int) -> tuple[str, list[list[list[str]]]]:
    """Tokenizes texts in jsonl entry given by line."""    
    # read from line
    entry = json.loads(line)
    url = entry['url']
    text_list = entry['text_list']

    # log
    tokenizer.logger.info(f"Tokenizing page {page_num} / {total_lines}: {url}")

    # tokenize
    tokenized_text_list = [[tokenizer.tokenize(sent) for sent in text]
                           for text in text_list]

    return url, tokenized_text_list



# Main entry point

def tokenize_jsonl(inpath: str, 
                   outpath: str, 
                   vocab_path, 
                   processes: int) -> None:
    """Tokenize text stored in .jsonl file."""

    tokenizer = Tokenizer(vocab_path)
    tokenizer.logger.info(f"Started tokenizing {inpath}")

    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)

        with Pool(processes=processes, 
                  initializer=worker_init, 
                  initargs=(vocab_path,)) as pool:
            # create iterable of arguments for worker
            iterable = get_iterable(infile, total_lines, )

            # Loop over iterable. Each set of args from iterable gets passed
            # to first available processor. The processor computes worker(*args)
            # and the result gets unpacked 
            for url, text_list in pool.starmap(worker, iterable):
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, outfile)
                outfile.write('\n')

        tokenizer.logger.info(f"Finished tokenizing {inpath}")
