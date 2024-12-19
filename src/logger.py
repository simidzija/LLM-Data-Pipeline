import sys
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))


class Logger:
    _loggers = {}

    def __init__(self, name: str):
        if name in Logger._loggers:
            print('logger found')
            self.logger = Logger._loggers[name]
            return 

        self.filename = str(ROOT/f'log/{name}.log')
        lock_file = Path(f'{self.filename}.__{name}.lock')
        if lock_file.exists():
            lock_file.unlink()
        log_dir = ROOT/'log'
        log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            self.handler = ConcurrentRotatingFileHandler(
                self.filename, 
                maxBytes=1024*1024*1024, 
                backupCount=5
            )
        
            self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
            self.handler.setFormatter(self.formatter)

            self.logger.addHandler(self.handler)
        
        Logger._loggers[name] = self.logger

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)