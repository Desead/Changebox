def set_seo(swap):
    '''
    Устанавливает SEO теги для внутренних страниц
    Тэги изменяются только если они не заполнены
    Все изменённые данные необходимо сохранять в точке вызова
    '''
    if swap.seo_title == '':
        swap.seo_title = 'Обмен ' + str(swap.money_left) + ' на ' + str(swap.money_right)
    if swap.seo_descriptions == '':
        swap.seo_descriptions = 'Надёжный и безопасный обмен ' + str(swap.money_left) + ' на ' + str(
            swap.money_right) + ' Круглосуточно и без перерывов'
    if swap.seo_keywords == '':
        swap.seo_keywords = str(swap.money_left) + ', ' + str(
            swap.money_right) + ', обмен, валюта, криптовалюта, безопасный обмен'
