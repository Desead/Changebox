import xml.etree.ElementTree as ET
from time import sleep

import requests

from Changebox.redis import redis_money
from app_main import models


def get_cbr_data() -> tuple[bool, str]:
    '''
    Получили данные  ЦБ
    '''

    CB_API = (
        'http://www.cbr.ru/scripts/XML_daily.asp',
        'https://www.cbr-xml-daily.ru/daily.xml',
    )

    for i in CB_API:
        response = requests.get(i, timeout=(5, 5))
        if response.status_code == 200:
            return True, response.text
        else:
            sleep(5)
    else:
        return False, ''


def convert_cbr_data_to_dict(dirty_data: str) -> dict:
    '''
    Получили с сайта ЦБ xml строку.
    1. Её надо распарсить
    2. Все курсы установлены к рублю. В связи с этим отсутствует сама валюты рубль - её надо добавить
    3. Приводим все курсы к USD

    Словарь который получаем на выходе:
    {'BYN': {'NumCode': '933', 'CharCode': 'BYN', 'Nominal': 1, 'Name': 'Белорусский рубль', 'Value': 0.35574594090593764}}
    '''
    cbr = {}
    for child in ET.fromstring(dirty_data):
        temp = {}
        for i in child:
            temp[i.tag] = i.text
        cbr[temp['CharCode']] = temp

    # добавляем в словарь cbr курс рубля
    cbr['RUB'] = {}
    cbr['RUB']['NumCode'] = '810'
    cbr['RUB']['CharCode'] = 'RUB'
    cbr['RUB']['Nominal'] = '1'
    cbr['RUB']['Name'] = 'Российский рубль'
    cbr['RUB']['Value'] = '1.0'

    # получаем курс usd
    usd = float(cbr['USD']['Value'].replace(',', '.'))

    # Устанавливаем все курсы к USD
    for i in cbr:
        cbr[i]['Value'] = float((cbr[i]['Value']).replace(',', '.')) / usd
        cbr[i]['Nominal'] = int(cbr[i]['Nominal'])

    return cbr


def cbr_to_redis(cbr: dict):
    pipe = redis_money.pipeline()
    for money in cbr.values():
        pipe.hset(name=money['CharCode'], key='Nominal', value=money['Nominal'])
        pipe.hset(name=money['CharCode'], key='Value', value=money['Value'])
        pipe.hset(name=money['CharCode'], key='type', value='fiat')
    pipe.execute()


def set_cbr_rates(money, cbr):
    off_money = models.Settings.objects.first().off_money

    for i in money:
        if i.money_type == 'fiat':
            if cbr.get(i.abc_code) is None:
                cost = 1
                nominal = 1
                if i.active:
                    error_string = 'В списке ЦБ не найдена валюта: ' + i.title + '.'
                    if off_money:
                        error_string += ' Валюта отключена'
                        i.active = False
                    info = models.InfoPanel()
                    info.description = error_string
                    info.save()

            else:
                cost = cbr[i.abc_code]['Value']  # получили цену с ЦБ текущей валюты, но она выражена в RUB
                nominal = cbr[i.abc_code]['Nominal']
            i.cost = cost
            i.nominal = nominal
            i.save()
