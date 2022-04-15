import json

from Changebox.settings import BESTCHANGE_FILES, BASE_DIR
from app_main.models import Money, FullMoney


def full_money_load():
    with open(BESTCHANGE_FILES / 'bm_cycodes.dat', mode='r', encoding='cp1251') as fl:
        xml = {}
        for i in fl.readlines():
            temp = i.strip().split(';')
            xml[temp[0]] = temp[1]

    with open(BASE_DIR / 'config' / 'crypto.json', mode='r', encoding='utf8') as fl:
        crypto = json.load(fl)

    for money in Money.objects.all():
        if money.money_type != 'crypto': continue
        temp = FullMoney()
        temp.title = money.title + ' (' + money.abc_code + ')'
        temp.money = money

        for k, v in crypto.items():
            if v == temp.title:
                temp.xml_code = xml[k]
                break
        temp.reserv = 10000 / money.cost
        try:
            temp.save()
        except:
            print('error: ', money.cost, temp.title)
            continue

    # with open(BASE_DIR / 'config' / 'crypto.json', mode='r', encoding='utf8') as fl:
    #
    #     crypto = json.load(fl)
    #     for num, i in crypto.items():
    #         money = str(i).split()
    #         if len(money) == 3:
    #             money[0] = money[0] + ' ' + money[1]
    #             money[1] = money[2]
    #         money[1] = str(money[1]).lstrip('(').rstrip(')')
    #
    #         temp = FullMoney()
    #         temp.title = i
    #         temp.xml_code = money[1]
    #         mn = Money.objects.filter(abc_code=money[1])
    #         if len(mn) == 1:
    #             temp.money = mn[0]
    #             temp.reserv = mn[0].cost * 10000
    #             try:
    #                 temp.save()
    #             except:
    #                 continue
