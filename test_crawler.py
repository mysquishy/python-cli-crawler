import pytest
import requests
from main import crawl_page

class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        pass

def dummy_get(url):
    # Returns a dummy HTML with a title and one link
    html_content = "<html><head><title>Test Title</title></head><body><a href='/link1'>Link1</a></body></html>"
    return DummyResponse(html_content)

def dummy_get_error(url):
    raise requests.RequestException("Dummy error")

def test_crawl_page_success(monkeypatch):
    monkeypatch.setattr(requests, "get", dummy_get)
    outputs = []
    visited = set(["http://dummysite"])
    crawl_page("http://dummysite", 1, visited, outputs)
    # Verify that the title was extracted correctly
    assert any("Title: Test Title" in line for line in outputs)

def test_crawl_page_error(monkeypatch):
    monkeypatch.setattr(requests, "get", dummy_get_error)
    outputs = []
    visited = set()
    crawl_page("http://dummysite", 1, visited, outputs)
    # Verify that an error message was logged
    assert any("Error fetching URL: Dummy error" in line for line in outputs)
