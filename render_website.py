import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

from livereload import Server


def on_reload():
    server = Server()
    server.watch('template.html')
    server.serve(root='.')


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

    rendered_page = template.render(
        books=get_books(),
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    on_reload()


if __name__ == '__main__':
    main()