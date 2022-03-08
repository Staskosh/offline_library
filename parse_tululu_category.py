import urllib
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


def get_book_links(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    book_paths_selector = '.ow_px_td .d_book'
    book_paths = soup.select(book_paths_selector)
    book_ids = [book_id.select_one('a')['href'] for book_id in book_paths]
    book_links = [urllib.parse.urljoin('http://tululu.org', book_id) for book_id in book_ids]

    return book_links
