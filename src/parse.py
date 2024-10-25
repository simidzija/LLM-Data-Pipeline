import json
from bs4 import BeautifulSoup
from bs4.element import Tag


with open('/Users/petar/Dropbox/llmdata/data/crawl_data.jsonl', 'r') as file:
    for _ in range(40):
        line = json.loads(next(iter(file)))
    url = line['url']
    html = line['text']


class Parser:
    def __init__(self):
        self.allowed_tags = ['div', 'p', 'ol', 'ul', 'blockquote']
        self.end_ids = set(["See_also", 
                            "References", 
                            "Further_reading",
                            "External_links"]) 
        self.boundary_classes = set(["mw-heading2", 
                                     "mw-heading3"])
    # TODO: Add logger


    def parse(self, html: str):
        # use html5lib parser because it matches chrome better than html.parser
        soup = BeautifulSoup(html, 'html5lib')
        main_tag = (soup
            .find('div', id="mw-content-text")
            .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
        )

        text_list = []
        text = ""

        # print(main_tag.prettify())

        for tag in main_tag.find_all(self.allowed_tags, recursive=False):
            if self.is_end(tag):
                break
            elif self.is_new_section(tag):
                if text:
                    text_list.append(text.strip())
                text = ""
                continue
            else:
                text += self.get_text(tag)
        
        if text:
            text_list.append(text.strip())

        for sec in text_list:
            print(sec)
            print('\n')

        return text_list       


    def get_text(self, tag: Tag):
        if tag.name == 'p':
            text = tag.text
        elif tag.name == 'ol':
            text = ""
            for i, item in enumerate(tag.find_all('li', recursive=False), 1):
                text += f"  {i}. {item.text}"
        elif tag.name == 'ul':
            text = ""
            for item in tag.find_all('li', recursive=False):
                text += f"  • {item.text}"
        elif tag.name == 'blockquote':
            if "templatequote" in tag.get("class", []):
                text = f'\n{tag.text.strip()}\n'
            else:
                text = f'\n"{tag.text.strip()}"\n'
        else:
            text = ""
        
        return text
        # TODO: other tags: 
        # TODO: deal with equations
        # TODO: get rid of refs (eg [2])
        # TODO: get rid of [further explanation needed]
        # TODO: get rid of [citation needed]


    def is_end(self, tag: Tag):
        if tag.name != "div":
            return False

        first_child = next(tag.children, None)
        if first_child and first_child.name == "h2":
            id_ = first_child.get("id")
            return id_ in self.end_ids
        else:
            return False

    def is_new_section(self, tag: Tag):
        if tag.name != "div":
            return False
        else:
            classes = set(tag.get("class", []))
            return self.boundary_classes.intersection(classes)

        

parser = Parser()
parser.parse(html)


# import requests
# from bs4 import BeautifulSoup

# response = requests.get("https://en.wikipedia.org/wiki/Ethics_in_religion")
# html = response.text

# soup = BeautifulSoup(html, 'html5lib')
# root = (soup
#         .find('div', id="mw-content-text")
#         .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
#         )

# for tag in root.find_all(recursive=False):
#     print(tag.name)
