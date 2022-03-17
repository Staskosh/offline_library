import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    server = Server()
    server.watch('index.html')
    server.serve(default_filename='pages/index0.html')


def get_books_list():
    with open("downloaded_books/all_books.json", "r") as my_file:
        books = json.load(my_file)
    books_list = [book for book in books]
    return books_list


def main():

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    books_list = get_books_list()
    books_by_page = 5
    grouped_books = list(chunked((books_list), books_by_page))
    os.makedirs('pages', exist_ok=True)
    page_count = len(grouped_books)
    for group_index, books in enumerate(grouped_books):

        rendered_page = template.render(
            books=books,
            num_pages=page_count,
            current_page_number=group_index,
        )

        with open(f'pages/index{group_index}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    on_reload()


if __name__ == '__main__':
    main()
