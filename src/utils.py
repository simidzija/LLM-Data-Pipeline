import sys
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
