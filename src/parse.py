import json
from bs4 import BeautifulSoup
from bs4.element import Tag

# TODO: Add logger

with open('/Users/petar/Dropbox/llmdata/data/crawl_data_5.jsonl', 'r') as file:
    for _ in range(15):
        line = json.loads(next(iter(file)))
    url = line['url']
    html = line['text']


class Parser:
    def __init__(self):
        # Tags
        self.allowed_tags = ['div', 'p', 'ol', 'ul', 'blockquote', 'dl']
        self.end_ids = set(["See_also",
                            "Notes", 
                            "References", 
                            "Further_reading",
                            "External_links"]) 
        self.boundary_classes = set(["mw-heading2", 
                                     "mw-heading3"])

    def parse_jsonl(self, raw_path, parsed_path):
        with open(raw_path, 'r') as raw, open(parsed_path, 'w') as parsed:
            for line in raw:
                # read from file
                entry = json.loads(line)
                url = entry['url']
                html = entry['text']

                # parse
                text_list = self.parse(html)

                # write to file
                entry = {'url': url, 'text_list': text_list}
                json.dump(entry, parsed)
                parsed.write('\n')


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

        # for n, sec in enumerate(text_list):
        #     print(f'--------------- Section {n}: ---------------')
        #     print(sec)

        return text_list       


    def get_text(self, tag: Tag):
        def get_text_helper(tag: Tag, newline=True):
            def unwanted_tags(tag: Tag):
                name = tag.name
                class_ = set(tag.get('class', []))

                if name == 'style':
                    return True
                elif name == 'sup':
                    if class_ == {'noprint','Inline-Template','Template-Fact'}:
                        # [citation needed]
                        return True
                    elif class_ == {'reference'}:
                        return True
                else:
                    return False

            # get text from tag, without unwanted elements
            for unwanted in tag.find_all(unwanted_tags):
                unwanted.extract()
            text = tag.text.strip()
            if newline:
                text += '\n'
            return text
        
        def get_text_from_p(tag):
            text = get_text_helper(tag)
            return text
        
        def get_text_from_ol(tag):
            text = ""
            for i, item in enumerate(tag.find_all('li', recursive=False), 1):
                text += f"  {i}. {get_text_helper(item)}"
            return text

        def get_text_from_ul(tag):
            text = ""
            for item in tag.find_all('li', recursive=False):
                text += f"  • {get_text_helper(item)}"
            return text
        
        def get_text_from_blockquote(tag):
            # if "templatequote" in tag.get("class", []):
            #     text = f'\n{get_text_helper(tag)}'
            # else:
            text = f'\n"{get_text_helper(tag, newline=False)}"\n\n'
            return text

        if tag.name == 'p' or tag.name == 'dl':
            text = get_text_from_p(tag)
        elif tag.name == 'ol':
            text = get_text_from_ol(tag)
        elif tag.name == 'ul':
            text = get_text_from_ul(tag)
        elif tag.name == 'blockquote':
            text = get_text_from_blockquote(tag)
        else:
            text = ""
        
        return text
        # TODO: deal with equations

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

