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
        
        # Format handlers
        self.FORMAT_HANDLERS = [
            (self.match_list, self.format_list),
            (self.match_math, self.format_math),
        ]

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
        # Base cases
        if isinstance(node, NavigableString):
            return str(node)
        if node.name in self.unwanted_tags:
            return ""
        for match_fcn, format_fcn in self.FORMAT_HANDLERS:
            if match_fcn(node):
                return format_fcn(node)

        # Recursion
        text = ""
        for child in node.children:
            text += self.get_text(child)

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


    ##############################  Format Handlers  ###########################

    # list

    def match_list(self, tag: Tag):
        return tag.name in ('ul', 'ol')
    
    def format_list(self, tag: Tag):
        ordered = tag.name == 'ol'
        text = ""
        if ordered:
            idx = 1
            for li_tag in tag.find_all('li', recursive=False):
                text += f"  {idx}. {self.get_text(li_tag)}\n"
                idx += 1
        else:  # unordered
            for li_tag in tag.find_all('li', recursive=False):
                text += f"  • {self.get_text(li_tag)}\n"
        
        return text
        
    # math

    def match_math(self, tag):
        return "mwe-math-element" in tag.get('class', [])
    
    def format_math(self, tag):
        annotation_tag = tag.find('annotation')
        if not annotation_tag:
            return "< --- MISSING MATH --- >"

        child = tag.find('span')
        inline = child and "mwe-math-mathml-inline" in child.get('class', [])
        latex = annotation_tag.get_text().strip()

        # remove prefix
        prefix = '{\displaystyle' 
        if latex.startswith(prefix):
            latex = latex[len(prefix):-1].strip()

        if inline:
            return '$' + latex + '$ '
        else:
            return '$$' + latex + '$$\n'
