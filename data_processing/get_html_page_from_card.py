from fake_useragent import FakeUserAgent
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from typing import List
import random
import time

from data_collection import find_object

ua = FakeUserAgent()


def create_webdriver() -> webdriver.Chrome:
    options = Options()
    options.page_load_strategy = 'eager'
    ua_random = ''
    while True:
        ua_random = ua.random
        if ('Mobile' in ua_random) or ('Android' in ua_random) or ('IPhone' in ua_random):
            continue
        break

    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')  # Важно для Linux и некоторых Windows
    options.add_argument('--disable-software-rasterizer')
    options.add_argument(f'user-agent={ua_random}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    # driver.maximize_window()

    return driver


def find_object_visibility(driver, search_by: str, value: str, timeout: int = 10, many: bool = False) -> WebElement | \
                                                                                                         List[
                                                                                                             WebElement]:
    WebDriverWait(driver, timeout).until(
        expected_conditions.visibility_of_element_located((search_by, value))
    )
    if many:
        return driver.find_elements(search_by, value)

    return driver.find_element(search_by, value)


def write_error(card_number: int, url: str) -> None:
    with open('error.txt', 'a', encoding='utf-8') as file:
        file.write(f'{card_number + 1}:\t{url}\n')


def find_scroll_click(driver: webdriver.Chrome, search_by: str, value: str, card_number: int, url: str):
    error = ''
    for _ in range(3):
        try:
            button = find_object(driver, search_by, value)
            driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)
            button.click()
            return True

        except Exception as e:
            error = e
            driver.refresh()

    write_error(card_number, url)
    with open('error_text.txt', 'a', encoding='utf-8') as file:
        file.write(f'{card_number}:\t{error}\n\n\n')
    return False


def get_html_from_page(driver: webdriver.Chrome):
    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()
    urls = [url.strip() for url in urls]

    for i, url in enumerate(urls):
        if i < 38:
            continue

        print(f'{i + 1}/{len(urls)}')
        try:
            driver.get(url=url)
        except Exception:
            write_error(i, url)
            continue

        # all_options_button = find_object(driver, By.CLASS_NAME, 'ComplectationGroupsDesktop__cutLink')
        # driver.execute_script('arguments[0].scrollIntoView({block: "center"});', all_options_button)
        # all_options_button.click()
        # if not find_scroll_click(driver, By.CLASS_NAME, 'ComplectationGroupsDesktop__cutLink', i, url):
        #     continue

        # all_characteristics = find_object(driver, By.CLASS_NAME, 'CardInfo__buttonSpecifications-qSEUu')
        # driver.execute_script('arguments[0].scrollIntoView({block: "center"});', all_characteristics)
        # all_characteristics.click()
        if not find_scroll_click(driver, By.CLASS_NAME, 'CardInfo__buttonSpecifications-qSEUu', i, url):
            continue

        try:
            find_object_visibility(driver, By.CLASS_NAME, 'ModificationInfo__group-RYeJn')
        except Exception:
            write_error(i, url)
            continue

        with open(f'data_card/card_{i + 1}.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)

        time.sleep(random.randint(1, 3))

        if i % 21 == 0:
            time.sleep(random.randint(6, 12))


def main():
    driver = create_webdriver()
    try:
        get_html_from_page(driver)
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
