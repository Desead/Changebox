import json

from Changebox.settings import BASE_DIR
from app_main.models import PaySystem


def pays_load():
    with open(BASE_DIR / 'config' / 'pay_systems.json', mode='r', encoding='utf8') as fl:
        for paysystem in json.load(fl):
            PaySystem.objects.get_or_create(
                title=paysystem['title']
            )

