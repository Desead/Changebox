from app_main.models import FullMoney, SwapMoney

MIN_USD = 20.0
MAX_USD = 1000.0
ROUND_NUM = 8


def create_all_swap():
    money = FullMoney.objects.all()
    for i in money:
        for j in money:
            if i == j:
                continue

            swap = SwapMoney.objects.get_or_create(
                money_left=i,
                money_right=j,
            )
            if swap[1]:
                swap[0].min_left = round(MIN_USD / i.money.cost, ROUND_NUM)
                swap[0].max_left = round(MAX_USD / i.money.cost, ROUND_NUM)
                swap[0].min_right = round(MIN_USD / j.money.cost, ROUND_NUM)
                swap[0].max_right = round(MAX_USD / j.money.cost, ROUND_NUM)
                swap[0].save()
