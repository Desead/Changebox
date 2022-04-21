from django.core.validators import MinValueValidator
from django.db import models


class Settings(models.Model):
    title = models.CharField('Title', max_length=100, help_text='title на сайте', default='Обменник')
    description = models.TextField('Description', help_text='descriptions на сайте', default='Самый крутой обменник')
    keywords = models.TextField('Keywords', help_text='keywords на сайте', default=' Меняем киви и не только')
    adminka = models.CharField('Админка', max_length=100, help_text='Адрес админки. Рекомендуется поменять',
                               default='admin_changebox')
    xml_address = models.CharField('Адрес для отдачи файла экспорт курсов', max_length=200, default='xml_export')
    reload_url = models.CharField('Технический адрес', max_length=50, default='update_12345')
    pause = models.BooleanField('Перерыв', default=False, help_text='Сайт не работает. На главной висит перерыв')
    reload_exchange = models.BooleanField('Технический перерыв', default=False,
                                          help_text='Сайт не работает. На главной висит перерыв, но есть доступ к сайту по техническому адресу, для проведения тестов. Рекомендуется поменять')
    job_start = models.PositiveSmallIntegerField('Час начала работы', default=0)
    job_end = models.PositiveSmallIntegerField('Час окончания работы', default=24)
    off_money = models.BooleanField('Отключать монеты', default=True,
                                    help_text='Отключать монеты и валюты, котировки которых небылы найдены среди ЦБ или Binance')
    rules_exchange = models.TextField('Правила обменника', blank=True, help_text='Можно писать с html тэгами')
    rules_security = models.TextField('Политика безопасности', blank=True, help_text='Можно писать с html тэгами')

    def __str__(self):
        return 'Базовые настройки'

    class Meta:
        verbose_name = 'Базовые настройки'
        verbose_name_plural = '08. Базовые настройки'


class City(models.Model):
    title = models.CharField('Город', max_length=100, help_text='Актуально только для обмена наличных')
    abc_code = models.CharField('Код города', max_length=10, unique=True)
    id_best = models.PositiveIntegerField('ID', default=0, help_text='ID города на BestChange')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = '07. Города'
        ordering = ['title']


class Exchange(models.Model):
    title = models.CharField('Название', max_length=100, unique=True)
    id_best = models.PositiveIntegerField('ID', help_text='ID обменника на Bestchange')
    ignore = models.BooleanField('Игнорировать', default=False,
                                 help_text='Игнорировать данный обменник при анализе курсов')
    description = models.TextField('Комментарий', blank=True, help_text='Просто любой комментарий для себя')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Обменник'
        verbose_name_plural = '06. Обменники'
        ordering = ['-ignore', 'title', ]


class Money(models.Model):  # список валют
    help_string = '''
    Название для определения стоимости данной валюты (монеты) с биржи.
    Для фиатной валюты поле не актуально.
    Для криптовалюты автоматически установится связь со стейблкоином USDT. Если данный стейблкоин не устраивает,
    то поле можно заполнить самостоятельно. Пример для Bitcoin: Было - BTCUSDT, можно заменить на BTCUSDP
    Правила заполнения следующие: 1. Указанный тикер должен котироваться на бирже Binance. 2. Регистр имеет значение.
    Актуальные тикеры с Binance можно получить здесь: https://api.binance.com/api/v3/ticker/price
    '''
    MONEY_TYPE = (
        ('crypto', 'Крипта'),
        ('fiat', 'Фиат'),
    )
    active = models.BooleanField('Использовать', default=False)
    title = models.CharField('Название', max_length=100, unique=True)
    abc_code = models.CharField('Код', max_length=20,
                                help_text='Буквенный код валюты: RUB, USD, BTC, XMR...')
    tiker = models.CharField('Тикер с Binance', help_text=help_string, blank=True, max_length=20)
    money_type = models.CharField('Тип', choices=MONEY_TYPE, max_length=10, default='crypto')
    nominal = models.PositiveIntegerField('Номинал', default=1,
                                          help_text='Единица в которых котируется данная валюта')
    cost = models.FloatField('USD', default=1, help_text='Текущая стоимость валюты/монеты выраженная в USD(T)')
    time = models.DateTimeField('Время обновления котировки', auto_now=True)
    memo = models.CharField('Доп. поле', max_length=255, blank=True,
                            help_text='Используется только для криптовалюты: MEMO, Destination tag, Message')
    conformation = models.PositiveSmallIntegerField('Подтверждения', default=1,
                                                    help_text='Количество необходимых подтверждения для начала перевода. Актуально только для крипты')

    def __str__(self):
        return self.abc_code + ': ' + self.title

    def save(self, *args, **kwargs):
        if self.tiker == '':
            if self.money_type == 'crypto':
                if self.abc_code == 'USDT':
                    self.tiker = 'USDT'
                else:
                    self.tiker = self.abc_code + 'USDT'
        super(Money, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Валюта/Монета'
        verbose_name_plural = '04. Валюты/Монеты'
        ordering = ['-active', 'money_type', 'abc_code', 'title']


class PaySystem(models.Model):  # список платёжных систем: киви, яндекс, вебмани и т.д.
    title = models.CharField('Название', max_length=100, help_text='Название платёжной системы', unique=True)
    active = models.BooleanField('Использовать', default=False)
    description = models.TextField('Комментарий', blank=True, help_text='Просто любой комментарий для себя')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Платёжная система'
        verbose_name_plural = '05. Платёжные системы'
        ordering = ['-active', '-title']


class FullMoney(models.Model):
    active = models.BooleanField('Использовать', default=False)
    title = models.CharField('Название', max_length=30, unique=True, help_text='Это название отображается на сайте')
    xml_code = models.CharField('XML', max_length=20,
                                help_text='Буквенный код валюты для экспорта. Взято с https://jsons.info/signatures/currencies')
    pay = models.ForeignKey(PaySystem, verbose_name='Платёжная система', on_delete=models.CASCADE, blank=True,
                            null=True, help_text='У крипты платёжная система может отсутствовать')
    money = models.ForeignKey(Money, verbose_name='Код валюты', on_delete=models.CASCADE)
    reserv = models.FloatField('Резерв', default=0, help_text='Доступный для обмена резерв')
    description = models.TextField('Комментарий', help_text='Просто любой комментарий для себя', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Валюта+ПС'
        verbose_name_plural = '03. Валюта+ПС'
        ordering = ('title',)
        unique_together = ('pay', 'money')


class SwapMoney(models.Model):  # Основная таблица настроек обменов.
    active = models.BooleanField('Вкл', default=False, help_text='Включить или отключить данный обмен')
    money_left = models.ForeignKey(FullMoney, verbose_name='Монета слева', on_delete=models.CASCADE,
                                   related_name='money_left_re')
    money_right = models.ForeignKey(FullMoney, verbose_name='Монета справа', on_delete=models.CASCADE,
                                    related_name='money_right_re')
    min_left = models.FloatField('Минимум слева', default=0, help_text='Минимальная сумма обмена',
                                 validators=[MinValueValidator(0)])
    max_left = models.FloatField('Максимум слева', default=0, help_text='Максимальная сумма обмена',
                                 validators=[MinValueValidator(0)])
    min_right = models.FloatField('Минимум справа', default=0, help_text='Минимальная сумма обмена',
                                  validators=[MinValueValidator(0)])
    max_right = models.FloatField('Максимум справа', default=0, help_text='Максимальная сумма обмена',
                                  validators=[MinValueValidator(0)])
    pause = models.PositiveIntegerField('Заморозка', default=0,
                                        help_text='Заморозка средст при обмене. Указывается в минутах.')
    rate_left = models.FloatField('Курс слева', default=0, validators=[MinValueValidator(0)])
    rate_right = models.FloatField('Курс справа', default=0, validators=[MinValueValidator(0)],
                                   help_text='Начальный курс, полученный с ЦБ, Binance или BestChange. Менять не рекомендуется. Данный курс периодически изменяется автоматически')
    rate_left_final = models.FloatField('Итого слева', default=0)
    rate_right_final = models.FloatField('Итого справа', default=0,
                                         help_text='Итоговый курс. Если в результате расчётов получился итоговый курс <= 0, то автоматически устанавливается значение = 1')
    change_left = models.FloatField('+/- % слева', default=0)
    change_right = models.FloatField('+/- % справа', default=0,
                                     help_text='Изменение курса в % (прибыль) Пример расчёта: Если = 5, то курс умножается на 1.05, если = -5, то на 0.95')
    add_fee_left = models.FloatField('Доп слева', default=0, validators=[MinValueValidator(0, 'Комиссия >= 0')])
    add_fee_right = models.FloatField('Доп справа', default=0, validators=[MinValueValidator(0, 'Комиссия >= 0')],
                                      help_text='Сумма фиксированной удерживаемой комисии. На курс обмена не влияет, изменяется только итоговая отдаваемая сумма!')

    # todo Городов для обмена наличными может быть несколько.
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город', null=True, blank=True,
                             help_text='Город для обмена. Актуально только для обмена с наличными деньгами', default='')
    time = models.DateTimeField('Время установки курса', auto_now=True)
    best_place = models.PositiveSmallIntegerField('Место', default=1,
                                                  help_text='Желаемое место на BestChange, если обмен не найден, то автоматически устанавливается в 0. Если стоит 0, то курс устанавливается по ЦБ и Binance. Если по ЦБ и Binance также не удалось установить, то используются значения из ручного курса')

    # Manual Settings
    manual_active = models.BooleanField('Ручной курс', default=False,
                                        help_text='Курс установленный вручную является приоритетным')
    manual_rate_left = models.FloatField('Ручной курс слева', default=0, validators=[MinValueValidator(0)])
    manual_rate_right = models.FloatField('Ручной курс справа', default=0, validators=[MinValueValidator(0)])

    # SEO Setting
    seo_title = models.CharField('Title для данной страницы', max_length=255, blank=True)
    seo_descriptions = models.CharField('Descriptions для данной страницы', max_length=255, blank=True)
    seo_keywords = models.TextField('Keywords для данной страницы', max_length=255, blank=True)

    # Метки для текущего направления обмена
    manual = models.BooleanField(default=True,
                                 help_text='Обменный пункт работает в ручном или полуавтоматическом режиме')
    juridical = models.BooleanField(default=False,
                                    help_text='Обменный пункт производит переводы средств на банковский счет клиента со счета юридического лица или ИП. Данная метка актуальна к установке только в направлениях * —› Любой Банк')
    verifying = models.BooleanField(default=False,
                                    help_text='Обменный пункт может требовать от клиента документы, удостоверяющие его личность')
    cardverify = models.BooleanField(default=False,
                                     help_text='Обменный пункт может требовать от клиента верифицировать банковскую карту')
    floating = models.BooleanField(default=False,
                                   help_text='Плавающий курс, который не фиксируется в заявке. При этом сумма обмена может измениться на момент отправки средств клиенту')
    otherin = models.BooleanField(default=False,
                                  help_text='Прием денежных средств от клиента производится на стороннюю платежную систему')
    otherout = models.BooleanField(default=False,
                                   help_text='Выплата денежных средств клиенту производится со сторонней платежной системы')
    reg = models.BooleanField(default=False,
                              help_text='Для проведения обмена пользователь обязательно должен зарегистрироваться на сайте обменного пункта')
    card2card = models.BooleanField(default=False,
                                    help_text='Обменный пункт принимает средства от пользователей переводами Card2Card (не через карточный мерчант). Данная метка актуальна к установке только в направлениях Visa/MasterCard —› *')
    delivery = models.BooleanField(default=False,
                                   help_text='Обменный пункт не имеет офиса в выбранном городе, оплата курьерской доставки включена в курс обмена или отображена посредством метки "Дополнительная комиссия"')
    hold = models.BooleanField(default=False,
                               help_text='Проведение обмена может быть задержано')

    def __str__(self):
        return str(self.money_left) + " -> " + str(self.money_right)

    class Meta:
        verbose_name = 'Обмен: Настройки'
        verbose_name_plural = '02. Обмен: Настройки'
        unique_together = ['money_left', 'money_right']


class SwapOrders(models.Model):
    swapmoney = models.ForeignKey(SwapMoney, on_delete=models.CASCADE, verbose_name='Направление обмена')
    value_from = models.CharField('Отдаёт слева', max_length=50)
    value_to = models.CharField('Получает справа', max_length=50)

    def __str__(self):
        return str(self.swapmoney)

    class Meta:
        verbose_name = 'Обмен: Заявки'
        verbose_name_plural = '01. Обмен: Заявки'


class InfoPanel(models.Model):
    description = models.TextField('Описание действия')
    time = models.DateTimeField('Время наступления события', auto_now_add=True)
    full_error = models.TextField('Полное описание', blank=True, editable=False)
    description_comment = models.TextField('Комментарий', blank=True, help_text='Просто любой комментарий для себя')

    def __str__(self):
        return str(self.time)[:19] + ' -> ' + self.description[:150]

    class Meta:
        verbose_name = 'Информация'
        verbose_name_plural = '09. Информация'
        ordering = ['-time', ]


class FieldsLeft(models.Model):
    title = models.CharField('Название', max_length=20)
    pay = models.ForeignKey(FullMoney, on_delete=models.CASCADE)

    def __str__(self):
        return ''


class FieldsRight(models.Model):
    title = models.CharField('Название', max_length=20)
    pay = models.ForeignKey(FullMoney, on_delete=models.CASCADE)

    def __str__(self):
        return ''
