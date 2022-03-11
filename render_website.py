import json
import os

import requests
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape

from livereload import Server


def on_reload():
    server = Server()
    server.watch('template.html')
    server.serve(default_filename='pages/index0.html')


def get_books():
    with open("downloaded_books/all_books.json", "r") as my_file:
        books_json = my_file.read()

    books = json.loads(books_json)
    return books


def main():

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    books = get_books()
    list_books = [book for book in books]
    grouped_books = list(chunked((list_books), 5))
    os.makedirs('pages', exist_ok=True)
    num_pages = len(grouped_books)
    for group_index, books in enumerate(grouped_books):

        rendered_page = template.render(
            books=books,
            num_pages=num_pages,
            current_page_number=group_index,
        )

        with open(f'pages/index{group_index}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    on_reload()


if __name__ == '__main__':
    main()