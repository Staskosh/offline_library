import argparse
import codecs
import json
import os
from urllib.parse import urlparse, urlsplit

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from parse_tululu_category import get_book_links
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Redirect')


def download_image(img_link, image_directory, downloaded_books_directory):
    response = requests.get(img_link)
    response.raise_for_status()
    image_path = urlsplit(img_link).path
    image_resolution = image_path.split('/')[-1]
    filepath = f'{image_directory}/{image_resolution}'
    with open(f'{downloaded_books_directory}/{filepath}', 'wb') as file:
        file.write(response.content)
    return filepath


def get_img_link(soup):
    img_selector = '.ow_px_td .d_book .bookimage img'
    img_path = soup.select_one(img_selector)['src']
    img_link = f'http://tululu.org{img_path}'
    return img_link


def get_book_info(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_and_author_selector = '.ow_px_td h1'
    book_and_author = soup.select_one(book_and_author_selector).text
    book_splited, author_splited = book_and_author.split('::')
    book = book_splited.strip()
    author = author_splited.strip()
    genres_selector = '.ow_px_td span.d_book a'
    found_genres = soup.select(genres_selector)
    genres = [genre.text for genre in found_genres]
    comments_selector = '.ow_px_td .black'
    found_comments = soup.select(comments_selector)
    comments = [comment.text for comment in found_comments]
    img_link = get_img_link(soup)

    return {'book': book,
            'author': author,
            'genres': genres,
            'comments': comments,
            'img_link': img_link,
            }


def generate_filepath(filename, book_directory):
    filename = sanitize_filename(filename)
    filepath = f'{book_directory}/{filename}'
    return filepath


def download_book(book, book_directory, book_id, downloaded_books_directory):
    url = f'http://tululu.org/txt.php'
    payload = {'id': book_id}
    response = requests.get(url, params=payload, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{book_id}.{book}.txt'
    filepath = generate_filepath(filename, book_directory)
    with open(f'{downloaded_books_directory}/{filepath}', 'w') as file:
        file.write(response.text)

    return filepath


def get_end_page():
    url = f'http://tululu.org/l55/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    pages_selector = '.ow_px_td .center .npage'
    pages = soup.select(pages_selector)
    total_pages = pages[-1].text

    return total_pages


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_page", help="Please enter the first page number",
                        type=int)
    total_pages = get_end_page()
    parser.add_argument("--end_page", help="Please enter the final page number",
                        type=int, default=total_pages)
    parser.add_argument("--dest_folder", help="Please enter the folder",
                        type=str, default='downloaded_books')
    parser.add_argument("--skip_imgs", help="If you don't want to download images",
                        action='store_true')
    parser.add_argument("--skip_txt", help="If you don't want to download books",
                        action='store_true')
    parser.add_argument("--json_path", help="Enter the path to json file",
                        type=str, default='downloaded_books')

    args = parser.parse_args()
    book_directory = os.getenv('BOOK_FOLDER')
    image_directory = os.getenv('IMAGE_FOLDER')
    os.makedirs(f'{args.dest_folder}/{book_directory}', exist_ok=True)
    os.makedirs(f'{args.dest_folder}/{image_directory}', exist_ok=True)
    os.makedirs(args.json_path, exist_ok=True)

    for page_number in range(args.start_page, args.end_page,):
        url = f'http://tululu.org/l55/{page_number}'
        response = requests.get(url)
        response.raise_for_status()
        book_links = get_book_links(response)
        books_info = []
        for book_link in book_links:
            response = requests.get(book_link)
            response.raise_for_status()
            book_info = get_book_info(response)
            book_id = urlparse(book_link).path.strip('/')[1:]
            try:
                if not args.skip_txt:
                    image_filepath = download_image(book_info['img_link'], image_directory,
                                   args.dest_folder)
                    book_info['image_filepath'] = f'{args.dest_folder}/{image_filepath}'
                if not args.skip_txt:
                    book_filepath = download_book(book_info['book'], book_directory,
                                  book_id, args.dest_folder)
                    book_info['book_filepath'] = f'{args.dest_folder}/{book_filepath}'
                books_info.append(book_info)
            except requests.HTTPError as error:
                print(error)

        with codecs.open(f'{args.json_path}/all_books.json', 'w', encoding='utf8') as json_file:
            json.dump(books_info, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
