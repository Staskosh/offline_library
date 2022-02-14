import os

import requests
from dotenv import load_dotenv


def download_book(directory, numbers):
    for number in range(numbers):
        'http://tululu.org/txt.php?id=239'
        'http://tululu.org/txt.php?id=8689'
        'http://tululu.org/txt.php?id=32168'
        url = f'http://tululu.org/txt.php?id=2{number}9'
        response = requests.get(url)
        response.raise_for_status()

        filename = f'id{number}.txt'
        with open(f'{directory}/{filename}', 'wb') as file:
            file.write(response.content)



def main():
    load_dotenv()
    numbers = 10
    directory = os.getenv('BOOKS_FOLDER')
    os.makedirs(directory, exist_ok=True)
    download_book(directory, numbers)



if __name__ == '__main__':
    main()


