import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from utils import Logger


class Parser:
    def __init__(self):
        # Tags
        self.allowed_tags = set(['div', 'p', 'ol', 'ul', 'blockquote', 'dl'])
        self.unwanted_tags = set(['script', 'style', 'mstyle'])
        self.end_ids = set(["See_also", "Notes", "References",  "Further_reading", "External_links"]) 
        self.boundary_classes = set(["mw-heading2", "mw-heading3"])
        
        self.TAG_HANDLERS = {
            'p': self.get_text_from_p,
            'dl': self.get_text_from_dl,
            'ol': self.get_text_from_ol,
            'ul': self.get_text_from_ul,
            'blockquote': self.get_text_from_blockquote
        }

        # Logger
        self.logger = Logger('parse')

    def parse_jsonl(self, raw_path, parsed_path):
        self.logger.info(f"Started parsing {raw_path}")
        with open(raw_path, 'r') as raw, open(parsed_path, 'w') as parsed:
            total_lines = sum(1 for _ in raw)
            raw.seek(0)

            for page_num, line in enumerate(raw, 1):
                # read from file
                entry = json.loads(line)
                url = entry['url']
                html = entry['text']

                # log
                self.logger.info(f"Parsing page {page_num} / {total_lines} : {url}")

                # parse
                text_list = self.parse(html)

                # write to file
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, parsed)
                parsed.write('\n')

        self.logger.info(f"Finished parsing {raw_path}\n\n")


    def parse(self, html: str) -> list[str]:
        # use html5lib parser because it matches chrome better than html.parser
        soup = BeautifulSoup(html, 'html5lib')
        main_tag = (soup
            .find('div', id="mw-content-text")
            .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
        )

        text_list = []
        text = ""

        for tag in main_tag.find_all(self.allowed_tags, recursive=False):
            if self.is_end(tag):
                break
            elif self.is_new_section(tag):
                if text:
                    text_list.append(text)
                text = ""
                continue
            else:
                text += self.get_text(tag)
        
        if text:
            text_list.append(text)
    
        for text in text_list:
            print('--------------------------------------------------------')
            print(text)

        return text_list       


    def get_text(self, tag: Tag) -> str:
        """Returns string of text in tag."""
        text = self.TAG_HANDLERS.get(tag.name, lambda x: "")(tag)
        
        return text
        # TODO: deal with equations

    def get_text_helper(self, tag: Tag, newline=True):
        text = ""
        for node in tag.descendants:
            if self.keep_text_node(node):
                text += str(node)

        text = text.strip()
        if newline:
            text += '\n'
        return text

    def keep_text_node(self, node: Tag):
        """Return True if node is a text node and if we should keep it"""
        if not isinstance(node, NavigableString):
            return False
        
        parent = node.parent
        name = parent.name
        class_ = set(parent.get('class', []))

        if name in self.unwanted_tags:
            return False
        elif name == 'sup':
            if class_ == {'noprint','Inline-Template','Template-Fact'}:
                # this corresponds to [citation needed] tags
                return False
            elif class_ == {'reference'}:
                return False

        return True 

    def get_text_from_p(self, tag):
        text = self.get_text_helper(tag)
        return text

    def get_text_from_dl(self, tag):
        text = self.get_text_helper(tag)
        return text
    
    def get_text_from_ol(self, tag):
        text = ""
        for i, item in enumerate(tag.find_all('li', recursive=False), 1):
            text += f"  {i}. {self.get_text_helper(item)}"
        return text

    def get_text_from_ul(self, tag):
        text = ""
        for item in tag.find_all('li', recursive=False):
            text += f"  • {self.get_text_helper(item)}"
        return text
    
    def get_text_from_blockquote(self, tag):
        # if "templatequote" in tag.get("class", []):
        #     text = f'\n{get_text_helper(tag)}'
        # else:
        text = f'\n"{self.get_text_helper(tag, newline=False)}"\n\n'
        return text

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

        


