from decimal import Decimal


def set_final_single_rate(swap):
    '''
    Функция получает один обмен SwapMoney и изменяет начальный курс обмена в зависимости от значений (+- % изменения)
    На выходе получаем фигальный курс обмена

    Функция не сохраняет данные. Сохранить их необходимо в точке вызова!
    ситуация когда начальын курс = 0 здесь не рассматривается. Начальынй курс меняется в другом месте
    '''

    left_cost = 0
    right_cost = 0
    if swap.manual_active:
        left_cost = swap.manual_rate_left
        right_cost = swap.manual_right_cost

    if left_cost == 0 or right_cost == 0:
        left_cost = swap.rate_left
        right_cost = swap.rate_right

    # получаем множитель изменения курса слева и справа
    delta_left = 1 if swap.change_left == 0 else (1 + swap.change_left / 100)
    delta_right = 1 if swap.change_right == 0 else (1 + swap.change_right / 100)

    left_cost = left_cost * delta_left
    right_cost = right_cost * delta_right

    # ищем минимум чтобы привести курс обмена к 1
    min_cost = min(left_cost, right_cost)
    if min_cost <= 0:
        return

    swap.rate_left_final = left_cost / min_cost
    swap.rate_right_final = right_cost / min_cost
