from bs4 import BeautifulSoup



class Parser:
    def __init__(self):
        pass

    def parse(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')

