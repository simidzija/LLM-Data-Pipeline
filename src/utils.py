import sys
import yaml
import json
from pathlib import Path
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

def load_yaml(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def get_jsonl_len_stats(path: str) -> tuple[float]:
    """
    Return stats dict about jsonl file, containing:
      - mean number of paragraphs per article
      - std dev of number of paragraphs per article
      - mean number of characters per paragraph
      - std dev of number of characters per paragraph
    """

    pars_per_article = []
    chars_per_par = []
    stats = {}

    with open(path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            text_lst = entry["text_list"]
            pars_per_article.append(len(text_lst))
            chars_per_par.extend([len(par) for par in text_lst])
        
    stats['avg_pars_per_article'] = np.mean(pars_per_article)
    stats['std_pars_per_article'] = np.std(pars_per_article)
    stats['avg_chars_per_par'] = np.mean(chars_per_par)
    stats['std_chars_per_par'] = np.std(chars_per_par)

    return stats

def plot_len_frequencies(path: str, plot_title):
    """Plot text len vs freq for data in path"""
    with open(path, 'r') as file:
        len_counter = defaultdict(int)
        for line in file:
            entry = json.loads(line)
            text_list = entry['text_list']
            for text in text_list:
                len_text = len(text)
                len_counter[len_text] += 1

    plt.scatter(list(len_counter.keys()), list(len_counter.values()), s=5)
    plt.title = plot_title
    plt.xlabel('text len')
    plt.ylabel('frequency')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.3)
    plt.show()


def get_texts(path: str, condition) -> dict[str, list[int]]:
    """Get texts which satisfy condition"""
    results = defaultdict(list)
    with open(path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            url = entry['url']
            text_list = entry['text_list']
            for idx, text in enumerate(text_list):
                if condition(text):
                    results[url].append(idx)

    return results





if __name__ == '__main__':
    inpath = str(ROOT/'data'/'normalize_data.jsonl')

    title = 'Length of text in normalize_data.jsonl after implementing cutoff'
    plot_len_frequencies(inpath, title)
    
    # condition = lambda text: len(text) > 0
    # results = get_texts(inpath, condition)
    # count = sum([len(idxs) for idxs in results.values()])
    # print(f'total pars = {count}')

    # condition = lambda text: len(text) > 50
    # results = get_texts(inpath, condition)
    # count = sum([len(idxs) for idxs in results.values()])
    # print(f'pars with len > 50 = {count}')
    