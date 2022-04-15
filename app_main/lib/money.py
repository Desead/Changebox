import json

from Changebox.settings import BASE_DIR
from app_main.models import Money


def money_load():
    with open(BASE_DIR / 'config' / 'cbr.json', mode='r', encoding='utf8') as fl:
        # Добавили фиат с ЦБ
        for cbr in json.load(fl).values():
            Money.objects.get_or_create(
                title=cbr['Name'],
                abc_code=cbr['CharCode'],
                money_type='fiat',
                nominal=int(cbr['Nominal']),
            )

        # Добавили рубль, так как среди курсов ЦБ его нету
        Money.objects.get_or_create(
            title='Российский рубль',
            abc_code='RUB',
            money_type='fiat',
        )

    with open(BASE_DIR / 'config' / 'crypto.json', mode='r', encoding='utf8') as fl:
        for i in json.load(fl).values():
            money = str(i).split()
            if len(money) == 3:
                money[0] = money[0] + ' ' + money[1]
                money[1] = money[2]
            money[1] = str(money[1]).lstrip('(').rstrip(')')

            Money.objects.get_or_create(
                title=money[0],
                abc_code=money[1],
                money_type='crypto',
            )
