from bs4 import BeautifulSoup
from typing import List, Dict
import json
import re


def get_bs4(num: int) -> BeautifulSoup:
    with open(f'data_card/card_{num}.html', 'r', encoding='utf-8') as file:
        src = file.read()

    return BeautifulSoup(src, 'lxml')


def transform_odometer(odometer: str) -> int:
    number = []
    for char in odometer:
        if char.isdigit():
            number.append(char)

    return int(''.join(number))


def get_small_characteristics(soup: BeautifulSoup) -> Dict[str, str | int]:
    small_characteristics = {}

    card_info_ul = soup.find(class_='CardInfo__list-MZpc1')

    # Поколение
    generation = card_info_ul.find(class_='CardInfoRow_superGen').find_all('div')[-1].find('a').text
    small_characteristics['generation'] = re.sub(r'\s+', ' ', generation)

    # Год выпуска
    small_characteristics['year'] = card_info_ul.find(class_='CardInfoRow_year').find_all('div')[-1].find(
        'a').text.strip()

    # Километраж
    odometer = card_info_ul.find(class_='CardInfoRow_kmAge').find_all('div')[-1].text
    small_characteristics['odometer'] = transform_odometer(odometer)

    # Тип машины (седан, джип ...)
    small_characteristics['car_type'] = card_info_ul.find(class_='CardInfoRow_bodytype').find_all('div')[-1].find(
        'a').text.strip().lower()

    # Цвет
    small_characteristics['color'] = card_info_ul.find(class_='CardInfoRow_color').find_all('div')[-1].find(
        'a').text.strip().lower()

    # Характеристики двигателя (объём, лошадиные силы, тип топлива)
    engine = card_info_ul.find(class_='CardInfoRow_engine').find_all('div')[-1].text
    # Объём двигателя
    small_characteristics['engine_volume'] = float(re.search(r'\d{1}\.\d{1}', engine).group())
    # Количество лошадиных сил
    small_characteristics['horsepower'] = int(re.search(r'\s\d+\s', engine).group().strip())
    # Тип топлива
    small_characteristics['oil_type'] = re.search(r'\w+$', engine).group().strip().lower()

    # Коробка передач
    small_characteristics['box'] = card_info_ul.find(class_='CardInfoRow_transmission').find_all('div')[
        -1].text.strip().lower()

    # Привод (передний, задний, полный)
    small_characteristics['drive'] = card_info_ul.find(class_='CardInfoRow_drive').find_all('div')[
        -1].text.strip().lower()

    # Положение руля (левый, правый)
    small_characteristics['wheel'] = card_info_ul.find(class_='CardInfoRow_wheel').find_all('div')[
        -1].text.strip().lower()

    # Состояние (требуется ремонт, не требуется ...)
    small_characteristics['state'] = card_info_ul.find(class_='CardInfoRow_state').find_all('div')[
        -1].text.strip().lower()

    # Таможня (растаможен, отсутствует ПТС ...)
    small_characteristics['customs'] = card_info_ul.find(class_='CardInfoRow_customs').find_all('div')[-1].text.replace(
        '\xa0', ' ').strip().lower()

    return small_characteristics


def main():
    all_car_characteristics = []
    for num in range(1, 3725):
        if num % 100 == 0:
            print(f'{num}/3724')
        try:
            soup = get_bs4(num)
            characteristics = get_small_characteristics(soup)
            all_car_characteristics.append(characteristics)

        except FileNotFoundError:
            with open('errors/missing_files.txt', 'a', encoding='utf-8') as file:
                file.write(f'Файл card_{num}.html не найден\n')
        except AttributeError as e:
            with open('errors/attribute_error.txt', 'a', encoding='utf-8') as file:
                file.write(f'{num}: {e}\n')

    with open('small_characteristics.json', 'w', encoding='utf-8') as file:
        json.dump(all_car_characteristics, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
