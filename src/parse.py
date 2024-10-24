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
        self.end_ids = set(["See_also", 
                            "References", 
                            "Further_reading",
                            "External_links"]) 
        self.boundary_classes = set(["mw-headings2", 
                                     "mw-headings3"])
    # TODO: Add logger


    def parse(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        main_tag = (soup
            .find('div', id="mw-content-text")
            .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
        )

        text_list = []
        text = ""

        for tag in main_tag.children:
            print(tag.name)
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
                

        print(text_list)

        return text_list       

    def is_end(self, tag: Tag):
        if tag.name != "div":
            return False

        first_child = next(tag.children, None)
        if first_child is None:
            return False
        elif first_child.name == "h2":
            ids = set(tag.get("id", []))
            return self.end_ids.union(ids)
        else:
            return False


    def is_new_section(self, tag: Tag):
        if tag.name != "div":
            return False
        else:
            classes = set(tag.get("class", []))
            return self.boundary_classes.union(classes)



    def get_text(self, tag: Tag):
        if tag.name == 'p':
            return tag.text
        else:
            return ""

        # TODO: deal with other cases (eg blockquote, li, etc)
        # TODO: deal with equations
        # TODO: get rid of refs (eg [2])
        # TODO: get rid of [further explanation needed]



    # def parse_intro(self, tag: Tag):
    #     def is_intro_tag(child):
    #         # True iff child is 1st level tag before first subheading
    #         result = (child.parent == tag and 
    #                   child.find_previous('div', class_="mw-heading2") is None)
    #         return result
        
    #     intro_tags = tag.find_all(is_intro_tag)

    #     text = ""
    #     for par in intro_tags:
    #         text += self.get_text(par)

    #     return [text]

    # def parse_main(self, tag: Tag):



    # def parse(self, html: str):
    #     soup = BeautifulSoup(html, 'html.parser')
    #     contents = (soup
    #         .find('div', id="mw-content-text")
    #         .find('div', class_="mw-content-ltr mw-parser-output", lang="en")
    #     )

    #     text = []
        
    #     # Parse intro section
    #     text.extend(self.parse_intro(contents))

    #     # Parse other sections (h2 level)
    #     text.extend(self.parse_main(contents))


    #     for section in contents.find_all('div', class_="mw-heading2"):
    #         print(section.name)
    #         text.extend(self.get_text(section))

    #     for i, subtext in enumerate(text, 1):
    #         print(f'Subtext {i}:\n')
    #         print(subtext)
    #         print('\n')




        
        

parser = Parser()
parser.parse(html)