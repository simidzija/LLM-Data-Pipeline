import sys
import os
import yaml
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

def load_yaml(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def combine_jsonl_files(old_paths: list[str], new_path: str, overwrite=False):
    if os.path.exists(new_path) and not overwrite:
        raise RuntimeError(f'path {new_path} already exists and overwrite is set to {overwrite}.')

    with open(new_path, 'w') as outfile:
        for old_path in old_paths:
            with open(old_path, 'r') as infile:
                outfile.write(infile.read())
                outfile.write('\n')



# if __name__ == '__main__':
    # old_paths = []
    # for i in range(1,6):
    #     path = str(ROOT/f'data/parse_data_{i}.jsonl')
    #     old_paths.append(path)
    
    # new_path = str(ROOT/'data/parse_data.jsonl')

    # combine_jsonl_files(old_paths, new_path)

        
    


    