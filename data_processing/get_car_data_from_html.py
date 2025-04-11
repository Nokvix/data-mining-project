from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Tuple
from pprint import pprint
import csv
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
    small_characteristics['Generation'] = re.sub(r'\s+', ' ', generation)

    # Год выпуска
    small_characteristics['Year'] = int(card_info_ul.find(class_='CardInfoRow_year').find_all('div')[-1].find(
        'a').text.strip())

    # Километраж
    odometer = card_info_ul.find(class_='CardInfoRow_kmAge').find_all('div')[-1].text
    small_characteristics['Odometer'] = transform_odometer(odometer)

    # Тип машины (седан, джип ...)
    small_characteristics['CarType'] = card_info_ul.find(class_='CardInfoRow_bodytype').find_all('div')[-1].find(
        'a').text.strip().lower()

    # Цвет
    small_characteristics['Color'] = card_info_ul.find(class_='CardInfoRow_color').find_all('div')[-1].find(
        'a').text.strip().lower()

    # Характеристики двигателя (объём, лошадиные силы, тип топлива)
    engine = card_info_ul.find(class_='CardInfoRow_engine').find_all('div')[-1].text
    # Объём двигателя
    small_characteristics['EngineVolume'] = float(re.search(r'\d{1}\.\d{1}', engine).group())
    # Количество лошадиных сил
    small_characteristics['Horsepower'] = int(re.search(r'\s\d+\s', engine).group().strip())
    # Тип топлива
    small_characteristics['OilType'] = re.search(r'\w+$', engine).group().strip().lower()

    # Коробка передач
    small_characteristics['Box'] = card_info_ul.find(class_='CardInfoRow_transmission').find_all('div')[
        -1].text.strip().lower()

    # Привод (передний, задний, полный)
    small_characteristics['Drive'] = card_info_ul.find(class_='CardInfoRow_drive').find_all('div')[
        -1].text.strip().lower()

    # Положение руля (левый, правый)
    small_characteristics['Wheel'] = card_info_ul.find(class_='CardInfoRow_wheel').find_all('div')[
        -1].text.strip().lower()

    # Состояние (требуется ремонт, не требуется ...)
    small_characteristics['State'] = card_info_ul.find(class_='CardInfoRow_state').find_all('div')[
        -1].text.strip().lower()

    # Таможня (растаможен, отсутствует ПТС ...)
    small_characteristics['Customs'] = card_info_ul.find(class_='CardInfoRow_customs').find_all('div')[-1].text.replace(
        '\xa0', ' ').strip().lower()

    return small_characteristics


def try_to_convert_to_number(text: str) -> int | float | str:
    try:
        num = int(text)
        return num
    except ValueError:
        try:
            num = float(text)
            return num
        except ValueError:
            return text


def get_full_characteristics_from_ul(card_specifications: List[Tag], block_name: str, field_names: List[str],
                                     column_names: List[str]) -> List[Tuple[str, str | int]]:
    values = []

    ul_block = get_ul(card_specifications, block_name)
    if not ul_block:
        return []

    all_li = ul_block.find_all('li')
    for i, field_name in enumerate(field_names):
        field_name = field_name.strip()
        pattern = re.compile(rf'{field_name}')
        for li in all_li:
            elem = li.find(string=pattern)
            if elem:
                li_text = li.find_all('span')[-1].text.replace('\xa0', '').strip().lower()
                li_text = try_to_convert_to_number(li_text)
                values.append((column_names[i], li_text))
                break

    return values


def preprocess_max_speed_acceleration_to_100(max_speed: str | None, acceleration_to_100: str | None) -> Tuple[int, float]:
    if max_speed:
        max_speed = int(re.search(r'\d+', max_speed).group().strip())

    if acceleration_to_100:
        acceleration_to_100 = float(re.search(r'\d+\..\d*', acceleration_to_100).group().strip())

    return max_speed, acceleration_to_100


def get_ul(div_blocks: List[Tag], needed_text: str) -> Tag | None:
    pattern = re.compile(rf'{needed_text}')
    for div in div_blocks:
        elem = div.find(string=pattern)
        if elem:
            ul = div.find('ul')
            return ul
    return None


def get_full_characteristics(soup: BeautifulSoup, small_characteristics: Dict[str, str | int]) -> Dict[str, str | int]:
    about_car = {}
    values = []
    column_names = ['CarClass', 'NumberTransmissions', 'FrontSuspensionType', 'RearSuspensionType', 'FrontBrakes',
                    'RearBrakes', 'MaxSpeed', 'AccelerationTo100', 'FuelGrade', 'TypeSupercharger', 'NumberCylinders',
                    'ValvesPerCylinder']

    for column_name in column_names:
        about_car[column_name] = None

    card_specifications = soup.find(class_='CardSpecifications__modificationInfo-n3XCR').find_all('div')

    values.extend(get_full_characteristics_from_ul(card_specifications, 'Общая информация', ['Класс автомобиля'], ['CarClass']))

    values.extend(get_full_characteristics_from_ul(card_specifications, 'Трансмиссия', ['Количество передач'], ['NumberTransmissions']))

    values.extend(get_full_characteristics_from_ul(
        card_specifications, 'Подвеска и тормоза', ['Тип передней подвески', 'Тип задней подвески', 'Передние тормоза', 'Задние тормоза'],
        ['FrontSuspensionType', 'RearSuspensionType', 'FrontBrakes', 'RearBrakes']
    ))

    values.extend(get_full_characteristics_from_ul(
        card_specifications, 'Эксплуатационные показатели', ['Максимальная скорость', 'Разгон до 100 км/ч', 'Марка топлива'],
        ['MaxSpeed', 'AccelerationTo100', 'FuelGrade']
    ))

    values.extend(get_full_characteristics_from_ul(
        card_specifications, 'Двигатель', ['Тип наддува', 'Количество цилиндров', 'Число клапанов на цилиндр'],
        ['TypeSupercharger', 'NumberCylinders', 'ValvesPerCylinder']
    ))

    for column_name, value in values:
        about_car[column_name] = value

    for column_name, value in about_car.items():
        small_characteristics[column_name] = value

    small_characteristics['MaxSpeed'], small_characteristics['AccelerationTo100'] = (
        preprocess_max_speed_acceleration_to_100(small_characteristics['MaxSpeed'],
                                                 small_characteristics['AccelerationTo100']))

    return small_characteristics


def write_to_csv(all_car_characteristics: List[Dict[str, int | str | float]]) -> None:
    column_names = tuple(all_car_characteristics[0].keys())

    with open('car_characteristics.csv', 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(column_names)

    for elem in all_car_characteristics:
        values = tuple(elem.values())
        with open('car_characteristics.csv', 'a', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(values)


def main():
    all_car_characteristics = []
    for num in range(1, 3725):
        if num % 100 == 0:
            print(f'{num}/3724')
        try:
            soup = get_bs4(num)
            characteristics = get_small_characteristics(soup)
            characteristics = get_full_characteristics(soup, characteristics)
            all_car_characteristics.append(characteristics)
            # pprint(characteristics)

        except FileNotFoundError:
            with open('errors/missing_files.txt', 'a', encoding='utf-8') as file:
                file.write(f'Файл card_{num}.html не найден\n')
        except AttributeError as e:
            with open('errors/attribute_error.txt', 'a', encoding='utf-8') as file:
                file.write(f'{num}: {e}\n')

        # finally:
        #     return

    with open('car_characteristics.json', 'w', encoding='utf-8') as file:
        json.dump(all_car_characteristics, file, indent=4, ensure_ascii=False)

    write_to_csv(all_car_characteristics)


if __name__ == '__main__':
    main()
