from decimal import Decimal


def set_single_rate(swap):
    '''
    Функция получает один обмен SwapMoney.
    Далее смотрит какой курс стоит активнм - ручной или авто и в зависимости от этого изменяет итоговый курс
    Функция не сохраняет данные. Сохранить их необходимо в точке вызова!
    '''

    left_nominal = swap.money_left.money.nominal
    right_nominal = swap.money_right.money.nominal
    left_cost = swap.money_left.money.cost / left_nominal
    right_cost = swap.money_right.money.cost / right_nominal

    min_cost = min(left_cost, right_cost)
    if min_cost <= 0: min_cost = 1

    # если ручной курс = 0 то устанавливаем курс по стоимости монет
    # курс устанавливается даже если ручной курс не активен. Сделано для информации и безопасности если вдруг курс с
    # беста пропадёт то чтобы была откуда его брать
    if swap.manual_rate_left <= 0 or swap.manual_rate_right <= 0:
        swap.manual_rate_left = right_cost / min_cost
        swap.manual_rate_right = left_cost / min_cost
        swap.manual_rate_left_str = str(swap.manual_rate_left)
        swap.manual_rate_right_str = str(swap.manual_rate_right)

    # тоже самое делаем с обычным курсом
    if swap.rate_left <= 0 or swap.rate_right <= 0:
        swap.rate_left = right_cost / min_cost
        swap.rate_right = left_cost / min_cost
        swap.rate_left_str = str(swap.rate_left)
        swap.rate_right_str = str(swap.rate_right)

    # теперь изменяем финальный курс обмена
    # получаем множитель изменения курса слева и справа
    delta_left = 1 if swap.change_left == 0 else (1 + swap.change_left / 100)
    delta_right = 1 if swap.change_right == 0 else (1 + swap.change_right / 100)

    if swap.manual_active:
        left_cost = swap.manual_rate_left * delta_left
        right_cost = swap.manual_rate_right * delta_right
    else:
        left_cost = swap.rate_left * delta_left
        right_cost = swap.rate_right * delta_right

    # приводим курс обмена к виду 1:х
    min_cost = min(left_cost, right_cost)
    swap.rate_left_final_str = str(left_cost / min_cost)
    swap.rate_right_final_str = str(right_cost / min_cost)
