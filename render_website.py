import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_books(json_path):
    with open(f'{json_path}/all_books.json', 'r') as my_file:
        books = json.load(my_file)
    return books


def render_pages():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_path", help="Enter the path to json file",
                        type=str, default='downloaded_books')
    args = parser.parse_args()
    template = env.get_template('index.html')
    books = get_books(args.json_path)
    books_by_page = 5
    grouped_books = list(chunked((books), books_by_page))
    os.makedirs('pages', exist_ok=True)
    page_count = len(grouped_books)
    for current_page_number, books in enumerate(grouped_books, start=1):
        rendered_page = template.render(
            books=books,
            num_pages=page_count,
            current_page_number=current_page_number,
        )

        with open(f'pages/index{current_page_number}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def rebuild():
    render_pages()
    print("Site rebuilt")


def on_reload():
    rebuild()

    server = Server()

    server.watch('index.html', rebuild)

    server.serve(root='.')


def main():
    render_pages()

    on_reload()


if __name__ == '__main__':
    main()
