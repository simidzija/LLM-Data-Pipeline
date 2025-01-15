import sys
import json
from pathlib import Path
from collections import defaultdict
import warnings

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Vocab:
    """BPE vocabulary class"""
    def __init__(self, freq_dict_path: str, vocab_path: str) -> None:
        self.freq_dict_path = freq_dict_path
        self.vocab_path = vocab_path

        # initialize vocab and create freq_tokens dict
        self.freq_tokens = {}  # {word1: (freq1, tokens1), etc.}
        self.vocab = set()
        with open(freq_dict_path, 'r') as f:
            freq_dict: dict[str, int] = json.load(f)
            for word, freq in freq_dict.items():
                tokens = [c for c in word]
                self.vocab.update(tokens)
                self.freq_tokens[word] = (freq, tokens)

    def increase_vocab(self, size: int) -> None:
        """Increase vocab to given size by performing BPE merges."""
        if size < len(self.vocab):
            raise ValueError(f'target vocab size ({size}) cannot be less than initial vocab size ({len(self.vocab)})')

        while len(self.vocab) < size:
            pair = self.most_frequent_pair()
            if pair is None:
                warnings.warn(f'Vocab size reached maximal value of {len(self.vocab)}, which is smaller than target value {size}.')
                return
            self.vocab.add(''.join(pair))
            self.merge(pair)

    def most_frequent_pair(self) -> tuple[str, str] | None:
        """Return most frequent pair of adjacent tokens from token lists in self.freq_tokens"""
        # create pair frequency dict
        pair_freq = defaultdict(int)  # {pair1: freq1, etc.}
        for freq, tokens in self.freq_tokens.values():
            if len(tokens) < 2:
                continue
            for t1, t2 in zip(tokens[:-1], tokens[1:]):
                pair_freq[(t1, t2)] += freq
            
        # return most frequent pair
        if pair_freq:
            pair = max(pair_freq, key=pair_freq.get)
            return pair
        else:
            return None

    def merge(self, pair: tuple[str, str]) -> None:
        """Merge given pair of tokens in all token lists in self.freq_tokens"""
        for word in self.freq_tokens:
            freq, tokens = self.freq_tokens[word]
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
            self.freq_tokens[word] = (freq, new_tokens)
            



