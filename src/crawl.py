import sys
import requests
import json
import time
import random
from pathlib import Path
from collections import deque
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger

class Crawler:
    def __init__(self, data_filepath: str, queue_filepath: str, visited_filepath: str, reset=False, seeds=None):
        super().__init__()
        self.data_filepath = data_filepath
        self.queue_filepath = queue_filepath
        self.visited_filepath = visited_filepath

        self.logger = Logger('crawl')
        self.request_handler = RequestHandler()

        if reset is True:
            assert seeds, "seeds must be list of seed urls if reset is True, but got {seeds}"

            # clear existing files
            with open(self.data_filepath, 'w'):
                pass
            with open(self.queue_filepath, 'w'):
                pass
            with open(self.visited_filepath, 'w'):
                pass
            with open(self.logger.filename, 'w'):
                pass

            # initialize queue (yet to visit)
            self.queue = deque(seeds)
            # initialize visited (already visited)
            self.visited = set([])
            # initialize extracted (queue + visited)
            self.extracted = set(self.queue)

        elif reset is False:
            # initialize queue
            with open(self.queue_filepath, 'r') as file:
                self.queue = deque([line.strip() for line in file])
            # initialize visited
            with open(self.visited_filepath, 'r') as file:
                self.visited = set([line.strip() for line in file])
            # initialize extracted
            self.extracted = set(self.queue).union(self.visited)
            # with open(self.data_filepath, 'r') as file:
                # self.extracted = set([json.loads(line)['url'] for line in file])
                # self.extracted.update(set(self.queue))

        self.url_extracter = WikiURLExtractor(self.queue, self.extracted)
    
    def scrape(self, url: str, response: requests.Response):
        # save data
        with open(self.data_filepath, 'a') as file:
            text = response.text
            entry = {'url': url, 'text': text}
            json.dump(entry, file)
            file.write('\n')

        # add to visited
        with open(self.visited_filepath, 'a') as file:
            file.write(url + '\n')
            
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
            elif status == 429:
                self.logger.info(f"STOPPING CRAWLING - Status: {status}")
                break

            print(f'page_count = {page_count}')

        self.logger.info("Finished crawling\n\n")

        # save queue
        with open(self.queue_filepath, 'w') as file:
            for url in self.queue:
                file.write(url)
                file.write('\n')
    
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
            
            # add random jitter
            wait_time = max(0, wait_time + random.uniform(-0.3, 0.3))
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
            redirect = 'mw-redirect' in tag.get("class", [])
            if (href.startswith('/wiki/')
                and not href.startswith('/wiki/List_of')
                and not href.startswith('/wiki/Main_Page') 
                and ':' not in href 
                and not redirect):
                url = 'https://en.wikipedia.org' + href
                if url not in self.extracted:
                    self.extracted.add(url)
                    self.queue.append(url)
        

