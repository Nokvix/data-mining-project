from fake_useragent import FakeUserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from typing import List
import random
import time

URL = 'https://auto.ru/cars/toyota/camry/all/'
ua = FakeUserAgent()
NUMBER_OF_PAGES = 99


def create_driver():
    options = Options()
    # options.page_load_strategy = 'eager'
    ua_random = ''
    while True:
        ua_random = ua.random
        if ('Mobile' in ua_random) or ('Android' in ua_random) or ('IPhone' in ua_random):
            continue
        break

    print(ua_random)
    options.add_argument(f'user-agent={ua_random}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    return driver


def find_object(driver, search_by: str, value: str, timeout: int = 5, many: bool = False) -> WebElement | List[WebElement]:
    WebDriverWait(driver, timeout).until(
        expected_conditions.element_to_be_clickable((search_by, value))
    )
    if many:
        return driver.find_elements(search_by, value)

    return driver.find_element(search_by, value)


def select_location(driver: webdriver.Chrome):
    find_object(driver, By.CLASS_NAME, 'GeoSelect-QRQ2Q').click()

    find_object(driver, By.CLASS_NAME, 'GeoSelectPopupRegion').click()

    select_group = find_object(driver, By.CLASS_NAME, 'GeoSelectPopup__no-suggest')
    find_object(select_group, By.TAG_NAME, 'button', many=True)[-1].click()


def go_to_next_page(driver: webdriver.Chrome):
    next_button = find_object(driver, By.CLASS_NAME, 'ListingPagination__next')
    if next_button.get_attribute('href'):
        next_button.click()


def scroll_and_save_html(driver: webdriver.Chrome):
    global NUMBER_OF_PAGES

    for page in range(1, NUMBER_OF_PAGES + 1):
        if page > 1:
            driver.get(URL + f'?page={page}')
        pagination_area = find_object(driver, By.CLASS_NAME, 'ListingPagination__sequenceControls')
        driver.execute_script('arguments[0].scrollIntoView();', pagination_area)
        time.sleep(10)

        with open(f'pages/page_{page}.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
            print(f'Страница {page}/{NUMBER_OF_PAGES}')

        time.sleep(random.randint(2, 4))

        if page % 5 == 0:
            time.sleep(random.randint(6, 12))


def main():
    driver = create_driver()
    try:
        driver.get(url=URL)
        select_location(driver)
        scroll_and_save_html(driver)

    except Exception as e:
        print(f'Что то сломалось: {e}')

    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()

