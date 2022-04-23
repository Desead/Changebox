import json

from Changebox.settings import BASE_DIR
from app_main.models import City


def city_load():
    with open(BASE_DIR / 'config' / 'city.json', mode='r', encoding='utf8') as fl:
        for city in json.load(fl):
            City.objects.get_or_create(
                title=city['title'],
                id_best=city['id_best'],
                abc_code=city['abc_code'],
            )
