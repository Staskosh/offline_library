import urllib
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


def parse_book_link(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    book_paths_selector = '.ow_px_td .d_book'
    book_paths = soup.select(book_paths_selector)
    book_ids = [book_id.find('a')['href'] for book_id in book_paths]
    book_links = []
    for book_id in book_ids:
        book_link = urllib.parse.urljoin('http://tululu.org', book_id)
        book_links.append(book_link)
    return book_links
