from json import load as json_load
from os.path import splitext
from datetime import date
import re
from page_analyzer import ROOT_DIR

FIXTURES = f'{ROOT_DIR}/tests/fixtures'


def get_full_path(file_name):
    return f"{FIXTURES}/{file_name}"


def get_content_from(path):
    full_path = get_full_path(path)
    _, extension = splitext(full_path)
    with open(full_path) as content_file:
        if extension == '.json':
            result = json_load(content_file)
        elif extension == '.html':
            result = content_file.read()
        else:
            raise ValueError('Unsupported file format')
    return result


def get_normalize_code_from(code: str, add_date=False):
    result = re.sub('[ \n]*', '', code)
    if add_date:
        date_now = date.today().isoformat()
        result = re.sub('{{date}}', date_now, result)
    return result
