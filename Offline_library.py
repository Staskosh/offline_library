import argparse
import os
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Redirect')


def download_image(img_link, image_directory):
    response = requests.get(img_link)
    response.raise_for_status()
    image_path = urlsplit(img_link).path
    image_resolution = image_path.split('/')[-1]
    filepath = f'{image_directory}/{image_resolution}'
    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_img_link(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    img_path = soup.find('td', class_='ow_px_td')\
        .find('table', class_='d_book')\
        .find('div', class_='bookimage').find('img')['src']
    img_link = f'http://tululu.org{img_path}'
    return img_link


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')
    book_info = soup.find('td', class_='ow_px_td')
    book_and_author = book_info.find('h1').text
    book, author = book_and_author.split('::')
    found_genres = book_info.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in found_genres]
    found_comments = book_info.find_all('span', class_='black')
    comments = [comment.text for comment in found_comments]

    return {'book': book,
            'author': author,
            'genres': genres,
            'comments': comments
            }


def generate_filepath(filename, directory):
    filename = sanitize_filename(filename)
    filepath = f'{directory}/{filename}'
    return filepath


def download_book(book, book_directory, book_id):
    url = f'http://tululu.org/txt.php?id=1{book_id}/'
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{book_id}.{book}.txt'
    filepath = generate_filepath(filename, book_directory)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", help="Please enter the first page number", type=int)
    parser.add_argument("end_id", help="Please enter the final page number", type=int)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    book_directory = os.getenv('BOOK_FOLDER')
    image_directory = os.getenv('IMAGE_FOLDER')
    os.makedirs(book_directory, exist_ok=True)
    os.makedirs(image_directory, exist_ok=True)
    for book_id in range(start_id, end_id):
        try:
            url = f'http://tululu.org/b{book_id}/'
            html_content = requests.get(url)
            html_content.raise_for_status()
            check_for_redirect(html_content)
            book_info = parse_book_page(html_content)
            download_book(book_info['book'], book_directory, book_id)
            img_link = get_img_link(html_content)
            download_image(img_link, image_directory)
        except requests.HTTPError as error:
            print(error)


if __name__ == '__main__':
    main()
