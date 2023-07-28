import pytest
from tests.conftest import get_content_from
import page_analyzer.html_parse as html_parse


@pytest.mark.parametrize(
    "input_html, expected_json", [
        ("hexlet_downloaded.html", "hexlet_parsed.json")
    ])
def test_seo_data(input_html, expected_json):
    text = get_content_from(input_html)
    result = html_parse.get_seo(text)
    expected = get_content_from(expected_json)
    assert result == expected
