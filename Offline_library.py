import os

import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urlsplit


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Redirect')


def download_image(img_link, image_directory):
    response = requests.get(img_link)
    response.raise_for_status()
    image_path = str(urlsplit(img_link).path)
    image = image_path.split('/')[-1]
    filepath = f'{image_directory}/{image}'
    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_img_link(number):
    url = f'http://tululu.org/b{number}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    img_path = soup.find('td', class_='ow_px_td')\
        .find('table', class_='d_book')\
        .find('div',class_='bookimage').find('img')['src']
    print(img_path)
    img_link = 'http://tululu.org' + img_path
    return img_link


def get_comments(found_comments):
    comments = []
    for comment in found_comments:
        comments.append(comment.text)
    return comments


def get_genres(found_genres):
    genres = []
    for genre in found_genres:
        genres.append(genre.text)
    return genres


def get_book_and_author_name(number):
    url = f'http://tululu.org/b{number}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_info = soup.find('td', class_='ow_px_td')
    book_and_author = book_info.find('h1').text
    book = book_and_author.split('::')[0]
    author = book_and_author.split('::')[1]
    found_genres = book_info.find('span', class_='d_book').find_all('a')
    genres = get_genres(found_genres)
    print(book, genres)
    found_comments = book_info.find_all('span', class_='black')
    comments = get_comments(found_comments)
    return book


def check_filepath(filename, directory):
    filename = sanitize_filename(filename)
    filepath = f'{directory}/{filename}'
    return filepath


def download_book(url, book_directory, number):
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{number}.{get_book_and_author_name(number)}.txt'
    filepath = check_filepath(filename, book_directory)
    # with open(filepath, 'wb') as file:
    #     file.write(response.content)


def main():
    load_dotenv()
    numbers = 10
    book_directory = os.getenv('BOOK_FOLDER')
    image_directory = os.getenv('IMAGE_FOLDER')
    os.makedirs(image_directory, exist_ok=True)
    os.makedirs(book_directory, exist_ok=True)
    for number in range(numbers):
        try:
            url = f'http://tululu.org/txt.php?id=1{number}/'
            download_book(url, book_directory, number)
            img_link = get_img_link(number)
            download_image(img_link, image_directory)
        except requests.HTTPError as error:
            print(error)


if __name__ == '__main__':
    main()


