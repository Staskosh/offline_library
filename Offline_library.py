import os

import requests
from dotenv import load_dotenv


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('It is not a book')


def download_book(directory, number):
    url = f'http://tululu.org/txt.php?id={number}'
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'id{number}.txt'
    with open(f'{directory}/{filename}', 'wb') as file:
        file.write(response.content)


def main():
    load_dotenv()
    numbers = 10
    directory = os.getenv('BOOKS_FOLDER')
    os.makedirs(directory, exist_ok=True)
    for number in range(numbers):
        try:
            download_book(directory, number)
        except requests.HTTPError as error:
            print(error)


if __name__ == '__main__':
    main()


