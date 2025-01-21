"""
Core functionality for generating the BPE vocabulary. 

This consitutes part 2/3 of the byte pair encoding (BPE) tokenization pipeline:
  1. Create word frequency dict
  2. Create vocab
  3. Tokenize text

Contains:
  - increase_vocab: increases vocabulary to specified size.
"""

# Standard library
import json
import sys
import warnings
from collections import Counter
from itertools import islice
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

# Third-party
from tqdm import tqdm

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger


def create_freq_dict(freq_dict_path: str) -> dict[str, int]:
    """Create word: freq dict from file."""
    with open(freq_dict_path, 'r') as f:
        freq_dict = json.load(f)

    return freq_dict

def init_vocab(freq_dict: dict[str, int]) -> set[str]:
    """Initialize vocabulary."""
    vocab = set(' ')
    for word in freq_dict:
        vocab.update(c for c in word)

    return vocab

def chunk_freq_dict(freq_dict: dict[str, int], 
                    n_chunks: int) -> dict[str, tuple[int, list[str]]]:
    """Split word: frequency dict into several word: (freq, tokens) dicts."""
    chunks = []
    k, m = divmod(len(freq_dict), n_chunks)
    for i in range(0, n_chunks):
        # create chunk
        start = i * k + min(i, m)
        end = (i + 1) * k + min(i, m)
        chunk = {}
        for word, freq in islice(freq_dict.items(), start, end):
            tokens = [c for c in word]
            chunk[word] = (freq, tokens)

        # add to chunks
        chunks.append(chunk)

    return chunks

def get_counter(chunk: dict[str, tuple[int, list[str]]]) -> Counter[tuple[str, str], int]:
    """Get pair: freq counter from word: (freq, tokens) dict."""
    counter = Counter()
    for freq, tokens in chunk.values():
        subcounter = Counter(zip(tokens[:-1], tokens[1:]))
        counter.update({k: freq * v for k, v in subcounter.items()})
    
    return counter

def merge(pair: tuple[str, str],
          chunk: dict[str, tuple[int, list[str]]]) -> dict[str, tuple[int, list[str]]]:
    """Merge pair of tokens in word: (freq, tokens) dict."""
    for word in chunk:
        freq, tokens = chunk[word]
        if len(tokens) < 2:
            continue

        # merge all occurences of pair in tokens, creating new_tokens list
        new_tokens = []
        i = 0
        while i < len(tokens):
            t1 = tokens[i]
            t2 = tokens[i+1] if i+1 < len(tokens) else None
            # if t1 and t2 form desired pair, append pair to new_tokens
            if (t1, t2) == pair:
                new_tokens.append(''.join(pair))
                i += 2
            # otherwise append t1 to new_tokens
            else:
                new_tokens.append(t1)
                i += 1

        # replace tokens with new_tokens
        chunk[word] = (freq, new_tokens)
    
    return chunk

def save_vocab(vocab: set[str], vocab_path: str) -> None:
    """Save vocab to file."""
    with open(vocab_path, 'w') as f:
        json.dump(list(vocab), f)



# Main entry point
def increase_vocab(freq_dict_path: str,
                   vocab_path: str,
                   size: int,
                   processes: int=10) -> None:
    """Increase vocabulary to specified size."""

    # Logger
    logger = Logger('vocab')

    # Create freq dict
    freq_dict = create_freq_dict(freq_dict_path)

    # Initialize vocab
    vocab = init_vocab(freq_dict)

    # Split freq_dict into chunks
    chunks = chunk_freq_dict(freq_dict, processes)

    # BPE loop
    logger.info(f'Increasing vocab size from {len(vocab)} to {size}')
    with Pool(processes=processes) as pool:
        for s in tqdm(range(len(vocab), size)):

            # Build pair: freq dict
            start = perf_counter()
            counter = Counter()
            for c in pool.map(get_counter, chunks):
                counter.update(c)
            end = perf_counter()
            print(f'Build dict: {end - start} s')
                
            # Break if counter is empty
            if not counter:
                msg = f'Vocab size reached maximal value of {s}, which is smaller than target value {size}.\n'
                warnings.warn(msg)
                logger.info(msg)
                break 

            # Find most frequent pair
            pair = max(counter, key=counter.get)

            # Merge
            start = perf_counter()
            iterable = [(pair, chunk) for chunk in chunks]
            chunks = pool.starmap(merge, iterable)
            end = perf_counter()
            print(f'Merge pair: {end - start} s')

            # Log
            logger.info(f"Vocab increased to size {s:6d} (target {size}): Added {''.join(pair)} = {pair[0]} + {pair[1]}.")

    # Log
    logger.info(f'Finished increasing vocab.\n')

    # Save vocab
    save_vocab(vocab, vocab_path)

