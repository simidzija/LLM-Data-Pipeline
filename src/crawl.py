import requests
import json
from pathlib import Path
from collections import deque
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

class Crawler:
    def __init__(self, urls: list):
        self.urls = deque(urls)
        self.visited = set()

    def download_content(self, url: str):
        self.visited.add(url)
        response = requests.get(url)
        status = response.status_code
        if status == 200:
            with open(str(ROOT/'data/crawled_data_wiki.jsonl'), 'w') as file:
                # save data
                text = response.text
                entry = {'url': url, 'text': text}
                json.dump(entry, file)
                
                # get urls
                new_urls = self.extract_urls(text)
                self.urls.extend(new_urls)
                print(self.urls)

    def extract_urls(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        urls = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/wiki/') and ':' not in href:
                full_url = 'https://en.wikipedia.org' + href
                urls.append(full_url)
        
        return urls

    def crawl(self, max_pages: int=10):
        page_count = 0
        while self.urls:
            url = self.urls.popleft()




