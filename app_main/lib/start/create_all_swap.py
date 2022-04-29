from app_main.models import FullMoney, SwapMoney


def create_all_swap():
    money = FullMoney.objects.all()
    for i in money:
        for j in money:
            if i == j:
                continue
            min_usd = 20.0
            max_usd = 1000.0

            min_left = min_usd / float(i.money.cost)
            max_left = max_usd / float(i.money.cost)

            min_right = min_usd / float(j.money.cost)
            max_right = max_usd / float(j.money.cost)

            SwapMoney.objects.get_or_create(
                money_left=i,
                money_right=j,
                min_left_str=str(min_left),
                max_left_str=str(max_left),
                min_right_str=str(min_right),
                max_right_str=str(max_right),
            )
