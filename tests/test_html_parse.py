import pytest
import os
import page_analyzer.html_parse as html_parse
from json import load as json_load
from os.path import splitext


def get_full_path(file_name):
    FIXTURES = f'{os.path.dirname(__file__)}/fixtures'
    return f"{FIXTURES}/{file_name}"


def get_content_from(path):
    _, extension = splitext(path)
    with open(path) as content_file:
        if extension == '.json':
            result = json_load(content_file)
        elif extension == '.html':
            result = content_file.read()
        else:
            raise ValueError('Unsupported file format')
    return result


@pytest.mark.parametrize(
    "input_html, expected_json", [
        (get_full_path("hexlet_downloaded.html"),
            get_full_path("hexlet_parsed.json"))
    ])
def test_seo_data(input_html, expected_json):
    text = get_content_from(input_html)
    result = html_parse.get_seo(text)
    expected = get_content_from(expected_json)
    assert result == expected
