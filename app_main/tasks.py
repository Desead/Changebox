from Changebox.celery import app
from app_main.lib.set_all_rates import set_all_rates

'''
@app.task(time_limit=20, soft_time_limit=15)
def best_download():
    print('Пошла загрузка с беста')
    res = download_files_from_bestchange(True)
    print('Файлы загужены. Начинаем их обработку')


@app.task(time_limit=2)
def cbr_rates():
    res = get_cbr_data()
    if res[0]:
        cbr = convert_cbr_data_to_dict(res[1])
        cbr_to_redis(cbr)
        money = Money.objects.all()  # todo вынести модель из задачи celery
        set_cbr_rates(money, cbr)


@app.task(time_limit=2)
def binance_rates():
    binance = get_binance_data()
    if binance[0]:
        set_binance_rate(Money.objects.all(), binance[1])
'''


@app.task(time_limit=2)
def clear_redis():
    from Changebox.redis import redis_queue
    redis_queue.flushdb()


@app.task(time_limit=25, soft_time_limit=20)
def set_rates():
    set_all_rates()
