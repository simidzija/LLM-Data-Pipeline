import requests
import json
import logging 
from logging.handlers import RotatingFileHandler
from pathlib import Path
from collections import deque
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent

# Logging
logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO) # log info, warnings, errors and critical messages

handler = RotatingFileHandler(filename=str(ROOT/'log/crawl.log'), 
                              maxBytes=10*2**20, 
                              backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

class Crawler:
    def __init__(self, urls: list, jsonl_path: str):
        super().__init__()
        self.urls = deque(urls)
        self.jsonl_path = jsonl_path
        self.visited = set()

    def extract_urls(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        urls = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/wiki/') and ':' not in href:
                full_url = 'https://en.wikipedia.org' + href
                if full_url not in self.visited:
                    urls.append(full_url)
        
        return urls
    
    def download_content(self, url: str) -> int:
        self.visited.add(url)
        response = requests.get(url)
        status = response.status_code
        if status == 200:
            with open(self.jsonl_path, 'w') as file:
                # save data
                text = response.text
                entry = {'url': url, 'text': text}
                json.dump(entry, file)
                
            # get urls
            new_urls = self.extract_urls(text)
            self.urls.extend(new_urls)
        
        return status

    @staticmethod
    def status_message(status: int) -> str:
        if status == 200:
            return "200 OK"
        elif status == 400:
            return "400 Bad Request"
        elif status == 401:
            return "401 Unauthorized"
        elif status == 403:
            return "403 Forbidden"
        elif status == 404:
            return "404 Not Found"
        elif status == 429:
            return "429 Too Many Requests"
        elif status == 500:
            return "500 Internal Server Error"
        else:
            return f"{status} Unexpected Status Code"
        

    def crawl(self, max_pages: int=10):
        page_count = 0
        while self.urls:
            url = self.urls.popleft()
            logger.info(f"Started crawling: {url}")
            status = self.download_content(url)
            if status == 200:
                page_count += 1
                if page_count > max_pages:
                    break
            logger.info(Crawler.status_message(status))


# TODO: Refactor into Crawler base class and WikiCrawler, etc. subclasses

