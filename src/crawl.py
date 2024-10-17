import requests
import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from collections import deque
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent

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



class RequestHandler:
    def __init__(self, refill_rate: float=1.0, bucket_limit: float=10.0):
        self.refill_rate = refill_rate # tokens / second
        self.bucket_limit = bucket_limit
        self.tokens = 0
        self.last_add = time.monotonic()

    def wait(self):
        # add tokens to bucket
        new_tokens = self.refill_rate * (time.monotonic() - self.last_add)
        self.tokens = min(self.bucket_limit, self.tokens + new_tokens)
        self.last_add = time.monotonic()

        # wait if necessary
        if self.tokens > 1:
            self.tokens -= 1
        else:
            wait_time = (1 - self.tokens) / self.refill_rate
            time.sleep(wait_time)
            # token gets added but then immediately used (reset to 0)
            self.last_add = time.monotonic()
            self.tokens = 0

    def request(self, url: str):
        self.wait()
        response = requests.get(url, headers={'User-Agent': 'WikiCrawler/1.0 (Educational personal project; https://github.com/simidzija)'})
        status = response.status_code
        if status == 200:
            # OK
            pass
        elif status == 400:
            # Bad Request
            pass
        elif status == 404:
            # Not Found
            pass
        elif status == 429:
            pass
            # Too Many Requests
            # TODO: Implement extra wait logic
        else:
            pass

        return response


class WikiURLExtractor():
    def __init__(self, queue: deque[str], extracted: set[str]):
        self.queue = queue
        self.extracted = extracted

    def extract(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup.find_all('a', href=True):
            href = tag['href']
            if href.startswith('/wiki/') and ':' not in href:
                url = 'https://en.wikipedia.org' + href
                if url not in self.extracted:
                    self.extracted.add(url)
                    self.queue.append(url)
        


class Crawler:
    def __init__(self, data_filepath: str, queue_filepath: str, reset=False, seeds=None):
        super().__init__()
        self.data_filepath = data_filepath
        self.queue_filepath = queue_filepath

        self.logger = Logger('crawl')
        self.request_handler = RequestHandler()

        if reset is True:
            assert seeds, "seeds must be list of seed urls if reset is True, but got {seeds}"

            # clear existing files
            with open(self.data_filepath, 'w'):
                pass
            with open(self.queue_filepath, 'w'):
                pass
            with open(self.logger.filename, 'w'):
                pass

            # define url queue and visited set
            self.queue = deque(seeds)
            self.extracted = set(self.queue)

        elif reset is False:
            with open(self.queue_filepath, 'r') as file:
                self.queue = deque([line.strip() for line in file])
            with open(self.data_filepath, 'r') as file:
                self.extracted = set([json.loads(line)['url'] for line in file])
                self.extracted.update(set(self.queue))

        self.url_extracter = WikiURLExtractor(self.queue, self.extracted)
    
    def scrape(self, url: str, response: requests.Response):
        # save data
        with open(self.data_filepath, 'a') as file:
            text = response.text
            entry = {'url': url, 'text': text}
            json.dump(entry, file)
            file.write('\n')
            
        # extract urls
        self.url_extracter.extract(text)
       

    def crawl(self, max_pages: int=10):
        self.logger.info("Started crawling")
        page_count = 0

        while self.queue and page_count < max_pages:
            url = self.queue.popleft()
            response = self.request_handler.request(url)
            status = response.status_code
            self.logger.info(f"Crawling {url} - Status: {status}")

            if status == 200:
                self.scrape(url, response)
                page_count += 1

            print(f'page_count = {page_count}')

        self.logger.info("Finished crawling\n\n")

        # save queue
        with open(self.queue_filepath, 'w') as file:
            for url in self.queue:
                file.write(url)
                file.write('\n')
    




# TODO: Refactor into Crawler base class and WikiCrawler, etc. subclasses

