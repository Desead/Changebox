import io
import zipfile
from decimal import Decimal
from pathlib import Path
from time import sleep
from typing import Dict

import requests

from Changebox.settings import BESTCHANGE_FILES
from app_main.lib.set_single_rate import set_single_rate
from app_main.models import Exchange, InfoPanel


def download_files_from_bestchange(save_file=False) -> (bool, dict):
    """
    Получаем zip с беста, разархивируем его и сохраняем всё содержимое в словаре best_files.
    При желании можно создать файлы на диске в каталоге BESTCHANGE_FILES
    на выходе получаем кортеж (bool, dict)
    первый элемент - успешность загрузки файлов
    второй - словарь - всё, что загружено с беста. ключ = имя файла из архива info.zip
    так будет выглядеть наш словарик со всем файлами с беста - каждый ключ = содержимому одного файла

    'bm_info.dat': [],
    'bm_top.dat': [],
    'bm_news.dat': [],
    'bm_bcodes.dat': [],
    'bm_cities.dat': [],
    'bm_cycodes.dat': [],
    'bm_exch.dat': [],
    'bm_brates.dat': [],
    'bm_cy.dat': [],
    'bm_rates.dat': [],
    """

    if not Path(BESTCHANGE_FILES).exists():
        Path(BESTCHANGE_FILES).mkdir(parents=True, exist_ok=True)

    BESTCHANGE_API = (
        'http://api.bestchange.ru/info.zip',
        'http://api.bestchange.net/info.zip',
        'http://api.bestchange.com/info.zip'
    )

    for best in BESTCHANGE_API:
        responce = requests.get(best, timeout=(10, 25))
        if responce.status_code == 200:
            break
        else:
            print('Ошибка загрузки данных с беста: ', best)
            sleep(5)
    else:
        return False, {}

    if save_file:
        with open(BESTCHANGE_FILES / 'info.zip', mode='wb') as fl:
            fl.write(responce.content)

    best_files = {}
    with zipfile.ZipFile(io.BytesIO(responce.content), 'r') as zf:
        if save_file:
            zf.extractall(BESTCHANGE_FILES)

        for i in zf.namelist():
            best_files[i] = []
            with zf.open(i) as f:
                best_files[i] = f.read().decode('cp1251').split('\n')

    return True, best_files


def get_rates_from_bestchange(swap, mark_changes, best_files: Dict, use_local_files=False):
    '''
    получаем все курсы и устанавливает у них обмены. Там где установили меняем флаг mark_changes
    устанавливаем только начальный курс обмена. Изменение +-% и финальный курс ставиться в функции set_single_rate
    '''
    if use_local_files:
        with open(BESTCHANGE_FILES / 'bm_rates.dat', mode='r') as fl:
            rates = fl.read().split('\n')
        with open(BESTCHANGE_FILES / 'bm_cycodes.dat', mode='r') as fl:
            money = fl.read().split('\n')
    else:
        rates = best_files['bm_rates.dat']
        money = best_files['bm_cycodes.dat']

    # Составили список ID обменников, курсы с которых надо игнорировать
    temp = Exchange.objects.filter(ignore=True)
    exchange = []
    for i in temp:
        exchange.append(i.id_best)

    # создаём 2 словаря money_to_id и обратный ему id_to_money для перевода названия монеты в id и обратно
    money_to_id = {}  # {'WMZ':'1'}
    id_to_money = {}  # {'1':'WMZ'}
    for i in money:
        j = i.split(';')
        money_to_id[j[1]] = j[0]
        id_to_money[j[0]] = j[1]

    # Создаём словарь словарей changes с настроенными из админке обменами
    changes = {}
    for i in swap:
        if i.best_place == 0:
            continue
        money_left = money_to_id[i.money_left.xml_code]  # берём название валюты и переводим его в id
        money_right = money_to_id[i.money_right.xml_code]

        '''
        все данные с курсами хранятся в списке rates в виде строк.
        Вид этих данных:
        139;59;714;1;290408.4901;58509.05;0.4228;1;0.2;3.44349436;0
        формат данных:
        ID отдаваемой валюты; ID получаемой валюты; ID обменника; курс обмена (отдать); курс обмена (получить); резерв получаемой валюты; отзывы; xx 
        этих строк порядка 200 000
        Чтобы за один проход соотнести эти курсы с установленными обменами из админки, необходимо нужные обмены
        из админки собрать в словарь changes имеюший следующую структуру:
        {
            '42': {  внешний ключ = ID отдаваемой валюты. внутренние ключи = ID получаемой валюты
                '168': set(), Используем множество а не список так как попадается много дубликатов
                '42': set(),  во множествах хранятся сами курсы обмена
            },
        }
        '''
        if changes.get(money_left) is None:
            changes[money_left] = {}
        changes[money_left][money_right] = []

    # бежим по файлу со всеми курсам и за 1 проход закидываем в словарь changes все обмены которые нам нужны
    # если обмен не нужен, к примеру он из обменника который надо игнорировать, то этот обмен не копираем себе
    double_exchange = {}
    for rate in rates:
        # получили список:
        # ID отдаваемой валюты; ID получаемой валюты; ID обменника; курс обмена (отдать); курс обмена (получить); резерв
        line = rate.split(';')[:6]
        # разбираем на элементы только ради человеко удобства
        money_left = line[0]
        money_right = line[1]
        exchange_id = line[2]
        # по идее можно игнорировать обменники где резерв менее установленного лимита. Ещё не реализовано
        money_reserv = line[5]
        if money_left in changes:  # если данный обмен нам нужен то записываем его в словарь changes
            if money_right in changes[money_left]:
                if exchange_id not in exchange:
                    # в файле с курсами бывает попадаются дублирующиеся строки. Чтобы их убрать создал новый словарь
                    # double_exchange и если ID обменника в этом словаре уже есть, значит повтор и его не пишем
                    current_key = money_left + ':' + money_right
                    if double_exchange.get(current_key) is None:
                        double_exchange[current_key] = []
                    if exchange_id not in double_exchange[current_key]:
                        double_exchange[current_key].append(exchange_id)
                        changes[money_left][money_right].append(line)

    # Все курсы собраны. осталось определить нужный и записать его в бд
    for num, i in enumerate(swap):
        if i.best_place == 0:  # значит курсы обмена ставим не с беста
            continue

        money_left = i.money_left.xml_code  # берём название валюты и переводим его в id
        money_right = i.money_right.xml_code
        money_left_id = money_to_id[money_left]  # берём название валюты и переводим его в id
        money_right_id = money_to_id[money_right]

        rate = changes[money_left_id][money_right_id]
        rate_left = []
        rate_right = []
        for r in rate:
            rate_left.append(r[3])  # r[0]=from, r[1]=to, r[2]=exchange
            rate_right.append(r[4])  # r[3]=rate_from r[4]=rate_to

        len_rate = len(rate_left)  # сколько курсов всего в списке
        if len_rate == 0:
            info = InfoPanel()
            info.description = 'Обмен ' + str(
                i) + ' устанавливается по курсам ЦБ и Binance. Желаемое место на BestChange установлено в 0'
            info.save()
            i.best_place = 0
            i.save()
            continue  # значит текущего обмена на бесте нету и его надо составить из курсов монет

        need_place = i.best_place - 1  # желаемая позиция на бесте

        '''
        выбор места на бесте:
        1. Сначала находим котировку того места которое нам нужно
        2. Определяем тип монеты котировку которой меняем - крипта или фиат. от этого зависит размер дельты - 0.01 или 0.00001
        3. В зависимости от нужного места и стороны где котировка неравна 1, изменяем полученную котировку (дальше расписано если меняем правую котировку):
        3.1 Если надо занять последнее место, то к последней котировке добавляем дельту
        3.2 В остальных случаях мы от котировку на нужном нам месте вычитаем дельту
        '''

        if rate_left[0] == '1':
            temp = [Decimal(x) for x in rate_right]
            delta = Decimal('0.01') if i.money_right.money.money_type == 'fiat' else Decimal('0.00001')
            temp.sort(reverse=True)
            i.rate_left = Decimal('1')
            if need_place >= len_rate:
                i.rate_right = temp[len_rate - 1] - delta  # значит хотим занять последнюю позицию
            else:
                i.rate_right = temp[need_place] + delta

        if rate_right[0] == '1':
            temp = [Decimal(x) for x in rate_left]
            delta = Decimal('0.01') if i.money_right.money.money_type == 'fiat' else Decimal('0.00001')
            temp.sort(reverse=False)
            i.rate_right = Decimal('1')
            if need_place >= len_rate:
                i.rate_left = temp[len_rate - 1] + delta  # значит хотим занять последнюю позицию
            else:
                i.rate_left = temp[need_place] - delta

        i.rate_left_str = str(i.rate_left)
        i.rate_right_str = str(i.rate_right)

        mark_changes[num] = True
        i.save()
