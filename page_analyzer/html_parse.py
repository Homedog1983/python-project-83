from bs4 import BeautifulSoup


def get_seo(text: str):
    soup = BeautifulSoup(text, 'html.parser')
    h1 = soup.find('h1').string if soup.find('h1') else None
    title = soup.find('title').string if soup.find('title') else None
    meta_tags = soup.find_all('meta')
    if meta_tags:
        for tag in meta_tags:
            if tag.attrs.get('name') == 'description':
                description = tag.attrs.get('content', '')
                break
    else:
        description = None
    return {'h1': h1, 'title': title, 'description': description}
