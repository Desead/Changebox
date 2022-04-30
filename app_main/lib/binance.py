import json

import requests

from app_main.models import InfoPanel, Settings


def get_binance_data() -> tuple[bool, dict]:
    ''' Формат вывода
    {
        "ETHBTC": "0.06887000",
        "LTCBTC": "0.00269200",
        "BNBBTC": "0.00953600",
        "NEOBTC": "0.00049900",
        "QTUMETH": "0.00210800",
        "EOSETH": "0.00073900",
        "SNTETH": "0.00002027",
        "BNTETH": "0.00082100",
        "BCCBTC": "0.07908100",
    }
    '''
    url = 'https://api.binance.com/api/v3/ticker/price'
    response = requests.get(url, timeout=(5, 5))
    if response.status_code != 200:
        return False, {}

    binance = {}
    for i in json.loads(response.text):  # с бинанса получаем строку, поэтому её надо перевести итерируемый объект
        binance[i['symbol']] = i['price']

    return True, binance


def set_binance_rate(money, binance, off_money=True):
    for i in money:
        if i.money_type == 'crypto':
            if binance.get(i.tiker) is None:
                if i.active:
                    error_string = 'Не найдена криптовалюта: ' + i.title + '.'
                    if off_money:
                        error_string += ' Монета отключена'
                        i.active = False
                    info = InfoPanel()
                    info.description = error_string
                    info.save()
            else:
                i.cost = binance[i.tiker]
            i.save()
