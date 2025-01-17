"""
Core functionality to parse Wikipedia html. 

Contains:
  - Parser: class for parsing Wikipedia html
  - parse_jsonl: function for parsing text stored in jsonl file. 
    Can utilize multiple processors.
"""

# Standard library
import json
import sys
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Iterator, Optional

# Third-party
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from logger import Logger

class Parser:
    """Class for parsing Wikipedia html."""

    def __init__(self) -> None:
        # Tag sets
        self.end_ids = set(["See_also", "Notes", "References",  "Further_reading", "External_links", "References_and_notes", "Footnotes"]) 
        self.unwanted_tags = set(["meta", "style", "mstyle", "figure", "table"])
        self.unwanted_classes = set(['Inline-Template', 'Template-Fact', 'ambox', 'box-Fringe_theories', 'cartbox', 'gallery', 'hatnote', 'infobox', 'locmap', 'magnify', 'mbox', 'media', 'metadata', 'mw-editsection', 'mw-empty-elt', 'navbar', 'navbox', 'navbox-styles', 'navigation-not-searchable', 'noprint', 'noprint', 'portal', 'reflist', 'reference', 'references', 'reflist', 'sidebar', 'stub', 'thumb', 'thumbinner', 'toc', 'vertical-navbox', 'wikitable'])
        
        # Format handlers
        self.FORMAT_HANDLERS = [
            (self.match_list, self.format_list),
            (self.match_math, self.format_math),
            (self.match_sup, self.format_sup),
            (self.match_dl, self.format_dl),
            (self.match_blockquote, self.format_blockquote),
            (self.match_heading, self.format_heading)
        ]

        # Logger
        self.logger = Logger('parse')

    def parse(self, html: str) -> list[str]:
        """Parse Wiki html and return list of text from each section."""
        # soup
        soup = BeautifulSoup(html, 'html5lib')

        # title
        title = soup.find('h1', id="firstHeading").get_text().strip()

        # main tag
        main_tag = soup.find('div', class_="mw-content-ltr mw-parser-output", lang="en")

        if not main_tag:
            return []

        text_list = []
        text = f'# {title}\n\n'
        skip = True

        for tag in main_tag.find_all(recursive=False):
            # skip tags before first 'p' tag
            if skip:
                if tag.name == 'p':
                    skip = False
                    self.indent = ""
                    self.last_char = ""
                else:  # skip current tag
                    continue

            if self.is_end(tag):
                break
            elif self.is_new_section(tag):
                if text:
                    text_list.append(text)
                text = "## " + self.heading_title(tag, level_str='h2') + "\n\n"
                self.indent = ""
                self.last_char = ""
            else:
                text += self.get_text(tag)
        
        if text:
            text_list.append(text)

        return text_list       

    def get_text(self, node: Tag | NavigableString) -> str:
        """Returns parsed text from html node."""

        # Base cases
        if isinstance(node, NavigableString):
            return self.format_string_node(node)
        elif self.is_unwanted_tag(node):
            return ""
        elif self.is_unwanted_class(node):
            return ""

        text = self.format_tag_node(node)
        if text is not None:
            return text

        # Recursion
        text = self.parse_children(node)  # calls get_text on child nodes
        self.last_char = text[-1] if text else self.last_char

        return text
    
    ###########################  Helper Functions  ###########################

    def format_tag_node(self, tag_node: Tag) -> Optional[str]:
        """Formats Tag node using appropriate format handler."""
        for match_fcn, format_fcn in self.FORMAT_HANDLERS:
            if match_fcn(tag_node):
                text = format_fcn(tag_node)
                self.last_char = text[-1] if text else self.last_char
                return text
        
        # if no formatter matches, return None
        return None

    def format_string_node(self, string_node: NavigableString) -> str:
        """Formats NavigableString node using appropriate format handler."""
        text = self.indent.join(str(string_node).splitlines(keepends=True))
        text = self.indent + text if self.last_char == '\n' else text
        self.last_char = text[-1] if text else self.last_char
        return text
    
    def is_unwanted_tag(self, node: Tag) -> bool:
        """Checks if node is an unwanted tag."""
        return node.name in self.unwanted_tags

    def is_unwanted_class(self, node: Tag | NavigableString) -> bool:
        """Checks if node contains an unwanted class."""
        classes = set(node.get('class', []))
        return classes.intersection(self.unwanted_classes)
    
    def parse_children(self, tag: Tag) -> str:
        """Parses children of tag, returning text."""
        text = ""
        for child in tag.children:
            text += self.get_text(child)
        return text   

    def is_end(self, tag: Tag) -> bool:
        """Checks if tag is an end tag."""
        if tag.name != "div":
            return False

        first_child = next(tag.children, None)
        if first_child and first_child.name == "h2":
            id_ = first_child.get("id")
            return id_ in self.end_ids
        else:
            return False

    def is_new_section(self, tag: Tag) -> bool:
        """Checks if tag represents the start of a new section."""
        return "mw-heading2" in tag.get('class', [])
    
    def heading_title(self, tag: Tag, level_str: str) -> str:
        """Returns markdown level 'h2', 'h3', etc. if it exists 
        else returns empty string"""
        node = tag.find(level_str)
        title = node.get_text() if node else ""
        return title


    ##############################  Format Handlers  ###########################

    # list
    def match_list(self, tag: Tag) -> bool:
        """Checks if tag is a list tag."""
        return tag.name in ('ul', 'ol')
    
    def format_list(self, tag: Tag) -> str:
        """Formats list tag."""
        ordered = tag.name == 'ol'
        text = "" if self.last_char == "\n" else "\n"

        # increase indent
        self.global_indent = self.indent + "  "
        self.indent = ""
        
        if ordered:
            idx = 1
            for li_tag in tag.find_all('li', recursive=False):
                if "mw-empty-elt" in li_tag.get('class', []):
                    continue
                text += self.global_indent + f"{idx}. {self.get_text(li_tag)}\n"
                idx += 1
        else:  # unordered
            for li_tag in tag.find_all('li', recursive=False):
                text += self.global_indent + f"• {self.get_text(li_tag)}\n"
        
        # decrease indent
        self.indent = self.global_indent[:-2]
        
        return text
        
    # math
    def match_math(self, tag: Tag) -> bool:
        """Checks if tag is a math tag."""
        return "mwe-math-element" in tag.get('class', [])
    
    def format_math(self, tag: Tag) -> str:
        """Formats math tag."""
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

    # sup
    def match_sup(self, tag: Tag) -> bool:
        """Checks if tag is a sup tag."""
        return tag.name == 'sup'
    
    def format_sup(self, tag: Tag) -> str:
        """Formats sup tag."""
        if 'reference' in tag.get('class', []):
            return ""
        
        text = "^" + self.parse_children(tag)
        return text
    
    # dl
    def match_dl(self, tag: Tag) -> bool:
        """Checks if tag is a dl tag."""
        return tag.name == 'dl'
    
    def format_dl(self, tag: Tag) -> str:
        """Formats dl tag."""
        self.indent += "  "
        text = self.parse_children(tag) + '\n'
        self.indent = self.indent[:-2]
        return text
    
    # blockquote
    def match_blockquote(self, tag: Tag) -> bool:
        """Checks if tag is a blockquote tag."""
        return tag.name == 'blockquote'
    
    def format_blockquote(self, tag: Tag) -> str:
        """Formats blockquote tag."""
        self.indent += "    "
        text = self.parse_children(tag) + '\n'
        self.indent = self.indent[:-4]
        return text
    
    # heading
    def match_heading(self, tag: Tag) -> bool:
        """Checks if tag is a h3, h4, or h5 level heading tag."""
        return tag.name in ('h3', 'h4', 'h5')

    def format_heading(self, tag: Tag) -> str:
        """Formats heading tag."""
        level = int(tag.name[-1])
        text = '#' * level + ' '
        text += self.parse_children(tag) + '\n'
        return text


# Multiprocessing functions

def get_iterable(file, total_lines: int) -> Iterator[tuple[int, str, int]]:
    """Generator of worker() arguments."""
    for page_num, line in enumerate(file, 1):
        yield (page_num, line, total_lines)

def worker_init() -> None:
    """Initializes worker."""
    global parser 
    parser = Parser()
    process = current_process()
    print(f'Initialized {process.name}')

def worker(page_num: int, line: str, total_lines: int) -> tuple[str, list[str]]:
    """Parses html in jsonl entry given by line."""
    # read from line
    entry = json.loads(line)
    url = entry['url']
    html = entry['text']

    # log
    parser.logger.info(f"Parsing page {page_num} / {total_lines} : {url}")

    # parse
    text_list = parser.parse(html)
    return url, text_list


# Main entry point

def parse_jsonl(raw_path: str, parsed_path: str, processes: int):
    """Parse html data stored in .jsonl file using multiprocessing."""
    parser = Parser()
    parser.logger.info(f"Started parsing {raw_path}")

    # read from file
    with open(raw_path, 'r') as infile, open(parsed_path, 'w') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)

        with Pool(processes=processes, initializer=worker_init) as pool:
            iterable = get_iterable(infile, total_lines)
            for url, text_list in pool.starmap(worker, iterable):
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, outfile)
                outfile.write('\n')


    parser.logger.info(f"Finished parsing {raw_path}\n\n")

