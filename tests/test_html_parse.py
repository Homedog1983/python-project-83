import pytest
import os
import page_analyzer.html_parse as html_parse
from json import load as json_load


def get_full_path(file_name):
    FIXTURES = f'{os.path.dirname(__file__)}/fixtures'
    return f"{FIXTURES}/{file_name}"


@pytest.mark.parametrize(
    "input_html, expected_json", [
        (get_full_path("hexlet_downloaded.html"),
            get_full_path("hexlet_parsed.json"))
    ])
def test_seo_data(input_html, expected_json):
    with open(input_html) as html_file:
        text = html_file.read()
    seo_data = html_parse.get_seo(text)
    with open(expected_json) as file:
        expected_dict = json_load(file)
    assert seo_data == expected_dict
