from Changebox.settings import BEST_SAVE
from app_main.lib.bestchange import get_rates_from_bestchange, download_files_from_bestchange
from app_main.lib.binance import set_binance_rate, get_binance_data
from app_main.lib.cbr import set_cbr_rates, get_cbr_data, convert_cbr_data_to_dict
from app_main.lib.set_final_single_rate import set_final_single_rate
from app_main.models import Money, SwapMoney, InfoPanel


def set_all_rates():
    money = Money.objects.all()
    swap = SwapMoney.objects.all()

    cbr = get_cbr_data()
    binance = get_binance_data()

    if not cbr[0]:
        info = InfoPanel()
        info.description = 'Курсы с ЦБ не загружены. Обмены не обновились'
        info.save()
        return
    if not binance[0]:
        info = InfoPanel()
        info.description = 'Курсы с Binance не загружены. Обмены не обновились'
        info.save()
        return

    cbr = convert_cbr_data_to_dict(cbr[1])
    binance = binance[1]

    # установили стоимости монеток
    set_cbr_rates(money, cbr)
    set_binance_rate(money, binance)

    # данный список нужен чтобы пометить какие обмены не были изменены с bestchange
    # если файл с беста вообще небыл получен или сайт недоступен мы без лишних ошибок
    # установим обменный курс с помошью ЦБ и Binance
    mark_changes = [False] * len(swap)

    # пробежались по всем обменам и посмотрели надо ли где то устанавливать курс с беста
    # если не надо, то к бесту не обращаемся
    for i in swap:
        if i.best_place > 0:
            best_files = download_files_from_bestchange(BEST_SAVE)  # загрузили
            if not best_files[0]:
                info = InfoPanel()
                info.description = 'Ошибка получения данных с BestChange'
                info.save()
            else:
                # устанавливаем сразу все курсы с best которые нашли
                get_rates_from_bestchange(swap, mark_changes, best_files[1])
            break

    # проверяем наличие цены для данного тикера
    def check_dict_rates(change, dict_rates, money):
        temp = dict_rates.get(money)
        if temp: return True, temp
        if change.active:
            info = InfoPanel()
            info.description = 'Курсы обмена ' + str(change) + ' отключён. Не найдена стоимость ' + str(money)
            change.active = False
            change.save()
            info.save()
        return False,

    # сюда попадаем если не нашли курс на get_rates_from_bestchange
    for num, i in enumerate(mark_changes):
        if not i:
            # устанавливаем стоимость обменов
            change = swap[num]
            if change.manual_active: continue  # ручные обмены не трогаем
            money_left_type = change.money_left.money.money_type
            money_right_type = change.money_right.money.money_type
            money_left_nominal = change.money_left.money.nominal
            money_right_nominal = change.money_right.money.nominal

            if money_left_type == 'crypto':
                money_left = change.money_left.money.tiker
                temp = check_dict_rates(change, binance, money_left)
                if not temp[0]: continue
                money_left_cost = temp[1]
            if money_left_type == 'fiat':
                money_left = change.money_left.money.abc_code
                money_left_cost = cbr[money_left]['Value']

            if money_right_type == 'crypto':
                money_right = change.money_right.money.tiker
                temp = check_dict_rates(change, binance, money_right)
                if not temp[0]: continue
                money_right_cost = temp[1]
            if money_right_type == 'fiat':
                money_right = change.money_right.money.abc_code
                money_right_cost = cbr[money_right]['Value']

            if money_left_cost > money_right_cost:
                rate_left = 1
                rate_right = (money_left_cost / money_left_nominal) / (money_right_cost / money_right_nominal)
            elif money_left_cost < money_right_cost:
                rate_left = (money_right_cost / money_right_nominal) / (money_left_cost / money_left_nominal)
                rate_right = 1
            else:
                rate_left = 1
                rate_right = 1

            change.rate_left = rate_left
            change.rate_right = rate_right

            change.save()
