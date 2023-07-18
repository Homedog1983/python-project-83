from bs4 import BeautifulSoup


def get_seo(text: str):
    soup = BeautifulSoup(text, 'html.parser')
    h1 = soup.h1.contents[0] if soup.h1 else ''
    title = soup.title.contents[0] if soup.title else ''
    meta_tags = soup.find_all('meta')
    if meta_tags:
        for tag in meta_tags:
            if tag.attrs.get('name') == 'description':
                description = tag.attrs.get('content', '')
                break
        else:
            description = ''
    return {'h1': h1, 'title': title, 'description': description}
