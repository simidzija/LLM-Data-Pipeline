import yaml
from src.crawler import download_content

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = load_config('config/settings.yaml')
    print(config)