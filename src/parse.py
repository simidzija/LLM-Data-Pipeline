import json
from bs4 import BeautifulSoup
from bs4.element import Tag


with open('/Users/petar/Dropbox/llmdata/data/crawl_data.jsonl', 'r') as file:
    for _ in range(50):
        line = json.loads(next(iter(file)))
    url = line['url']
    html = line['text']



class Parser:
    def __init__(self):
        self.min_len = 100
    
    # TODO: Add logger

    def get_text(self, tag: Tag):
        if tag.name == 'p':
            return tag.text
        else:
            return ""

        # TODO: deal with other cases (eg blockquote, li, etc)
        # TODO: get rid of refs (eg [2])
        # TODO: get rid of [further explanation needed]

    def parse_intro(self, tag: Tag):
        def is_intro_tag(child):
            result = (child.parent == tag and 
                      not child.find_previous('div', class_="mw-heading2"))
            return result
        
        intro_tags = tag.find_all(is_intro_tag)

        text = ""
        for par in intro_tags:
            text += self.get_text(par)

        return text


    def parse(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        contents = (soup
            .find('div', id="mw-content-text")
            .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
        )

        text = ""

        text += self.parse_intro(contents)

        print(text)

        # sections = []
        # for par in contents.find_all('p', recursive=False):
        #     section = ''
        #     for subpar in par.find_all('p'):
        #         text = subpar.text
        #         section += text
        #     sections.append(section)
            
        # for section in sections:
        #     print(section[:20])


        
        

parser = Parser()
parser.parse(html)