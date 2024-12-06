import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

class Logger:
    def __init__(self, name: str):
        self.filename = str(ROOT/f'log/{name}.log')
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO) 

        self.handler = RotatingFileHandler(self.filename, maxBytes=10*2**20, backupCount=5)
        
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        self.handler.setFormatter(self.formatter)

        self.logger.addHandler(self.handler)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)