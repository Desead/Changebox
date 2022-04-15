import json

from Changebox.settings import BASE_DIR
from app_main.models import Exchange


def exchange_load():
    with open(BASE_DIR / 'config' / 'exchange.json', mode='r', encoding='utf8') as fl:
        for exchange in json.load(fl):
            Exchange.objects.get_or_create(
                title=exchange['title'],
                id_best=exchange['id_best'],
            )
