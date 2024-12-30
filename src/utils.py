import sys
import os
import yaml
import json
from pathlib import Path
import numpy as np

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


        
    


    