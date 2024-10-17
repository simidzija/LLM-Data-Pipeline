import yaml
import json


def load_yaml(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

# with open('/Users/petar/Dropbox/llmdata/data/crawl_queue.txt') as file:
#     queue = [line.strip() for line in file]
#     print(len(queue))