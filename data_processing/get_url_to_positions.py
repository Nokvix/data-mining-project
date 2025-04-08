from bs4 import BeautifulSoup
from typing import List


def write_urls_to_file(urls: List[str]) -> None:
    with open('urls.txt', 'a', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')


def get_url() -> None:
    for page in range(1, 100):
        with open(f'pages/page_{page}.html', 'r', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        cards = soup.find_all(class_='ListingItemTitle__link')
        urls = [block.get('href') for block in cards]
        write_urls_to_file(urls)
        # print(f'{page}/99')


def main():
    get_url()


if __name__ == '__main__':
    main()
