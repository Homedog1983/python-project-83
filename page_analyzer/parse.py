from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_normalize_url(data: str):
    parsed_data = urlparse(data)
    return ''.join([parsed_data.scheme, '://', parsed_data.hostname])


def get_seo(text: str):
    soup = BeautifulSoup(text, 'html.parser')
    h1 = soup.find('h1').string if soup.find('h1') else None
    title = soup.find('title').string if soup.find('title') else None
    description = None
    meta_tags = soup.find_all('meta')
    if meta_tags:
        for tag in meta_tags:
            if tag.attrs.get('name') == 'description':
                description = tag.attrs.get('content', '')
                break
    return {'h1': h1, 'title': title, 'description': description}
