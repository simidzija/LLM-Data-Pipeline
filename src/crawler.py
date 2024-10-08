import requests

def download_content(url):
    request = requests.get(url)
    status = request.status_code
    if status == 200:
        content = request.text
        return content

def extract_urls(content):
    pass


