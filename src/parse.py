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
        # Tag sets
        self.allowed_tags = set(['div', 'p', 'ol', 'ul', 'blockquote', 'dl'])
        self.end_ids = set(["See_also", "Notes", "References",  "Further_reading", "External_links"]) 
        self.boundary_classes = set(["mw-heading2", "mw-heading3"])
        
        # Handlers 
        self.FILTER_HANDLERS = {
            'script': self.filter_handler_unwanted,
            'style': self.filter_handler_unwanted,
            'mstyle': self.filter_handler_unwanted,
            'sup': self.filter_handler_sup
        }

        self.FORMAT_HANDLERS = {
            'li': self.format_handler_list_item,
            'blockquote': self.format_handler_blockquote,
            'math': self.format_handler_math
        }

        # Logger
        self.logger = Logger('parse')

    def parse_jsonl(self, raw_path, parsed_path):
        """Parse html data stored in .jsonl file."""
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
        """Parse wiki html and return list of text from each section."""
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
            else:
                text += self.get_text(tag)
        
        if text:
            text_list.append(text)
    
        for text in text_list:
            print('--------------------------------------------------------')
            print(text)

        return text_list       

    ####################     Helper Functions     #####################

    def get_text(self, tag: Tag, newline=True):
        """Parses tag by iterating over descendent nodes. Used by tag handlers."""
        text = ""
        for node in tag.descendants:
            if isinstance(node, NavigableString):
                if self.filter_node(node):
                    text += self.format_node(node)

        text = text.strip()
        if newline:
            text += '\n'
        return text

    def filter_node(self, node: NavigableString):
        """Filters NavigableString node by calling appropriate filter handler."""
        parent = node.parent
        return self.FILTER_HANDLERS.get(parent.name, lambda x: True)(node)

    def format_node(self, node: NavigableString):
        """Formats NavigableString node by calling appropriate format handler."""
        parent = node.parent
        return self.FORMAT_HANDLERS.get(parent.name, lambda x: str(x))(node)

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

        
    ####################     FILTER HANDLERS     #####################

    def filter_handler_unwanted(self, node: NavigableString):
        return False
    
    def filter_handler_sup(self, node: NavigableString):
        class_ = set(node.parent.get('class', []))

        if class_ == {'noprint','Inline-Template','Template-Fact'}:
            # this corresponds to [citation needed] tags
            return False
        elif class_ == {'reference'}:
            return False
        else: 
            return True

    ####################     FORMAT HANDLERS     #####################

    def format_handler_list_item(self, node: NavigableString):
        parent = node.parent
        grandparent = parent.parent
        if grandparent.name == 'ol':
            # find index of li among siblings
            idx = 1 + sum(1 for prev in parent.previous_siblings if prev.name == 'li')
            return f"  {idx}. {str(node)}"
        else:  # ul
            return f"  • {str(node)}"
        
    def format_handler_blockquote(self, node: NavigableString):
        return f'\n"{str(node)}"\n\n'

    def format_handler_math(self, node: NavigableString):
        # TODO: implement
        return "MATH GOES HERE"
