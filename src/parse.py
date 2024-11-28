import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from abc import ABC, abstractmethod

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from utils import Logger


class Parser:
    def __init__(self):
        # Tag sets
        self.end_ids = set(["See_also", "Notes", "References",  "Further_reading", "External_links"]) 
        self.boundary_classes = set(["mw-heading2", "mw-heading3"])
        self.unwanted_tags = set(["meta", "style", "mstyle", "figure"])
        
        # # Filter handlers
        # self.FILTER_HANDLERS = {
        #     'script': self.filter_handler_unwanted,
        #     'style': self.filter_handler_unwanted,
        #     'mstyle': self.filter_handler_unwanted,
        #     'sup': self.filter_handler_sup
        # }

        # # Format rules
        # self.FORMAT_RULES = [
        #     ListItemRule()
        # ]

        # Format handlers
        self.FORMAT_HANDLERS = {
            # 'ol': lambda x: self.format_list(x, ordered=True),
            # 'ul': lambda x: self.format_list(x, ordered=False),
            # 'blockquote': self.format_blockquote,
            'math': self.format_math,
            # 'sup': self.format_sup,
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
        main_tag = soup.find('div', class_="mw-content-ltr mw-parser-output", lang="en")

        if not main_tag:
            return []

        text_list = []
        text = ""
        skip = True

        for tag in main_tag.find_all(recursive=False):
            # skip tags before first 'p' tag
            if skip:
                if tag.name == 'p':
                    skip = False
                else:  # skip current tag
                    continue

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

    def get_text(self, node: Tag | NavigableString):
        # if node.name:
        #     print(f'Tag: <{node.name}>')
        # else:
        #     print(f'NavigableString: {str(node)[:20]}...')
        # Base cases
        if isinstance(node, NavigableString):
            return str(node)
        elif node.name in self.unwanted_tags:
            return ""
        elif node.name in self.FORMAT_HANDLERS:
            handler = self.FORMAT_HANDLERS[node.name]
            return handler(node)

        # Recursion
        text = ""
        for child in node.children:
            text += self.get_text(child)

        return text
        

    # def get_text(self, tag: Tag):
    #     """Parses tag by iterating over descendent nodes. Used by tag handlers."""
    #     text = ""
    #     for node in tag.descendants:
    #         if isinstance(node, NavigableString):
    #             text += self.format_node(node)

    #     text = text.strip()
    #     text += '\n'

    #     return text

    # def format_node(self, node: NavigableString):
    #     """Formats NavigableString node by calling appropriate format handler."""
    #     for rule in self.FORMAT_RULES:
    #         if rule.matches(node):
    #             return rule.format(node)
            
    #     return str(node)

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

    def format_math(self, tag: Tag):
        assert tag.name == 'math'
        # TODO: Implement
        return "MATH GOES HERE"

        
    # ####################     FILTER HANDLERS     #####################

    # def filter_handler_unwanted(self, node: NavigableString):
    #     return False
    
    # def filter_handler_sup(self, node: NavigableString):
    #     class_ = set(node.parent.get('class', []))

    #     if class_ == {'noprint','Inline-Template','Template-Fact'}:
    #         # this corresponds to [citation needed] tags
    #         return False
    #     elif class_ == {'reference'}:
    #         return False
    #     else: 
    #         return True



##############################################################################
################################ Format Rules ################################
##############################################################################

# class FormatRule(ABC):
#     @abstractmethod
#     def matches(self, node: NavigableString) -> bool:
#         pass

#     @abstractmethod
#     def format(self, node: NavigableString) -> str:
#         pass

# class ListItemRule(FormatRule):
#     def matches(self, node):
#         return (node.parent.name == 'li' and 
#                 node.parent.parent and
#                 node.parent.parent.name in ('ol', 'ul'))
    
#     def format(self, node):
#         if node.parent.parent.name == 'ol':
#             # find index of li among siblings
#             idx = 1 + sum(1 for prev in node.parent.previous_siblings if prev.name == 'li')
#             return f"  {idx}. {str(node)}"
#         else:  # ul
#             return f"  • {str(node)}"
        
# class BlockquoteHandler(FormatRule):
#     # TODO: Implement
#     pass

# class MathHandler(FormatRule):
#     # TODO: Implement
#     pass
