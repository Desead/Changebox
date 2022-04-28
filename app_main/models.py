import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from Changebox import settings
from app_main.lib.number_2_str import number_2_str
from app_main.lib.remove_space_from_string import remove_space_from_string
from app_main.lib.set_seo import set_seo
from app_main.lib.validators import validate_string
from app_main.managers import CustomUserManager

DECIMAL_PLACES = 8
MAX_DIGITS = 20
'''
поля Decimal в моделях имеют копию типа CharField. Эти поля имеют суффикс _str
Данная копия нужна для красивого отображения в админке, чтобы число делилось на разряды и небыло экспоненты у decimal

Чтобы постоянно не конверировать значения - ввод или изменение происходит через _str, а участвует в расчётах Decimal поле

По идее можно в админке вызывать save и конвертить CharField в Decimal, а в модели при вызове save наоборот
Decimal конвертить в CharField. Логически это будет верно.
Но это не только приведёт к дублированию почти идентичного кода, так ещё и Decimal
постоянно придёться проверять на экспоненту. Поэтому любой ввод/изменение только через _str, а чтение через Decimal
'''


def copy_str_to_decimal(str_field):
    str_field = remove_space_from_string(str_field).replace(',', '.')
    return Decimal(str_field), number_2_str(str_field)


class CustomUser(AbstractUser):
    MAX_REFERALNUM_LETTERS = 10

    username = None
    email = models.EmailField('email address', unique=True)
    referal = models.CharField('Referal num', max_length=MAX_REFERALNUM_LETTERS, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        def gen_referal_num():
            from string import ascii_letters
            import random
            count = 1
            while True:
                num = ''.join([random.choice(ascii_letters) for _ in range(self.MAX_REFERALNUM_LETTERS)])
                if CustomUser.objects.filter(referal=num).count() == 0:
                    return num
                count += 1
                if count >= 5: break
            return num

        self.referal = gen_referal_num()
        super().save()

    class Meta:
        verbose_name_plural = '11. Пользователи'


class Commisions(models.Model):
    COMMISSION_PAYER = (
        ('sender', 'Отправитель платежа'),
        ('payment', 'Получатель платежа'),
        ('half', '50/50'),
    )
    payer = models.CharField('Оплачивает комиссию', max_length=50, choices=COMMISSION_PAYER, default='sender')

    fee_percent = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    fee_absolut = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    fee_min = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    fee_max = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)

    fee_percent_str = models.CharField('Комиссия %', default='0.0', max_length=MAX_DIGITS,
                                       validators=[validate_string], help_text='Комиссия платёжной системы в %')
    fee_absolut_str = models.CharField('Комиссия фикс', default='0.0', max_length=MAX_DIGITS,
                                       validators=[validate_string], help_text='Фиксированная комиссия в валюте')
    fee_min_str = models.CharField('Минимальное ограничение', default='0.0', max_length=MAX_DIGITS,
                                   validators=[validate_string], help_text='Минимальная взимаемая комиссия')
    fee_max_str = models.CharField('Максимальное ограничение', default='0.0', max_length=MAX_DIGITS,
                                   validators=[validate_string], help_text='Максимально возможная комиссия')

    def save(self, *args, **kwargs):
        self.fee_percent, self.fee_percent_str = copy_str_to_decimal(self.fee_percent_str)
        self.fee_absolut, self.fee_absolut_str = copy_str_to_decimal(self.fee_absolut_str)
        self.fee_min, self.fee_min_str = copy_str_to_decimal(self.fee_min_str)
        self.fee_max, self.fee_max_str = copy_str_to_decimal(self.fee_max_str)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Settings(models.Model):
    title = models.CharField('Title', max_length=100, help_text='title на сайте', default='Обменник')
    description = models.TextField('Description', help_text='descriptions на сайте', default='Самый крутой обменник')
    keywords = models.TextField('Keywords', help_text='keywords на сайте', default=' Меняем киви и не только')
    adminka = models.CharField('Админка', max_length=100, help_text='Адрес админки. Рекомендуется поменять',
                               default='admin')
    xml_address = models.CharField('Адрес для отдачи файла экспорт курсов', max_length=200, default='xml_export')
    reload_url = models.CharField('Технический адрес', max_length=50, default='update_12345')
    pause = models.BooleanField('Перерыв', default=False, help_text='Сайт не работает. На главной висит перерыв')
    reload_exchange = models.BooleanField('Технический перерыв', default=False,
                                          help_text='Сайт не работает. На главной висит перерыв, но есть доступ к сайту по техническому адресу, для проведения тестов. Рекомендуется поменять')
    job_start = models.PositiveSmallIntegerField('Час начала работы', default=0)
    job_end = models.PositiveSmallIntegerField('Час окончания работы', default=24)
    off_money = models.BooleanField('Отключать монеты', default=True,
                                    help_text='Отключать монеты и валюты, котировки которых небылы найдены среди ЦБ или Binance')
    logo = models.FileField('Логотип', upload_to='static/img/', default='', blank=True)
    exchane_name = models.CharField('Название на сайт', max_length=200, default='Exchange Money')
    rules_exchange = models.TextField('Правила обменника',
                                      default='<h1>Правила сервиса</h1><div class="rules"> Lorem ipsum dolor sit amet.</div>',
                                      help_text='Можно писать с html тэгами')
    rules_security = models.TextField('Политика безопасности',
                                      default='<h1>политика безопасности</h1><div class="rules"> Lorem ipsum dolor sit amet.</div>',
                                      help_text='Можно писать с html тэгами')
    rules_warning = models.TextField('Выдержка из правил',
                                     default='Проверьте все введённые данные и нажмите кнопку <b>Оплатить</b>',
                                     help_text='Главные тезисы при совершении обмена. Отображаются на странице совершения обмена. Можно писать с html тэгами')
    news = models.TextField('Новость на главную', blank=True, help_text='Можно использовать html тэги',
                            default='Добрый день. Сегодня Bitcoin в очередной раз удивил общественность, показав рост на 20% за два часа!')

    def __str__(self):
        return 'Базовые настройки'

    def save(self, *args, **kwargs):
        self.job_end = min(self.job_end, 24)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Базовые настройки'
        verbose_name_plural = '09. Базовые настройки'


class City(models.Model):
    title = models.CharField('Город', max_length=100, help_text='Актуально только для обмена наличных')
    abc_code = models.CharField('Код города', max_length=10, unique=True)
    id_best = models.PositiveIntegerField('ID', default=0, help_text='ID города на BestChange')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = '08. Города'
        ordering = ['title']


class Exchange(models.Model):
    title = models.CharField('Название', max_length=100, unique=True)
    id_best = models.PositiveIntegerField('ID', help_text='ID обменника на Bestchange')
    ignore = models.BooleanField('Игнорировать', default=False,
                                 help_text='Игнорировать данный обменник при анализе курсов')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Обменник'
        verbose_name_plural = '07. Обменники'
        ordering = ['-ignore', 'title', ]


class Money(models.Model):  # список валют
    help_string = '''
    Название для определения стоимости данной монеты с биржи.
    Aвтоматически установится связь со стейблкоином USDT. Если данный стейблкоин не устраивает,
    то поле можно заполнить самостоятельно. Пример для Bitcoin: Было - BTCUSDT, можно заменить на BTCUSDP
    Правила заполнения следующие: 1. Указанный тикер должен котироваться на бирже Binance. 2. Регистр имеет значение.
    Актуальные тикеры с Binance можно получить здесь: https://api.binance.com/api/v3/ticker/price
    '''
    MONEY_TYPE = (
        ('crypto', 'Крипта'),
        ('fiat', 'Фиат'),
    )
    active = models.BooleanField('Использовать', default=False,
                                 help_text='В базовых настройках есть опция для автоматического отключения не найденной валюты')
    title = models.CharField('Название', max_length=100, unique=True)
    abc_code = models.CharField('Код', max_length=20,
                                help_text='Буквенный код валюты: RUB, USD, BTC, XMR...')
    money_type = models.CharField('Тип', choices=MONEY_TYPE, max_length=20, default='crypto')
    nominal = models.PositiveIntegerField('Номинал', default=1,
                                          help_text='Единица в которых котируется данная валюта')
    cost = models.DecimalField(default=1, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS, editable=False)
    cost_str = models.CharField('USD', default='1', max_length=MAX_DIGITS, validators=[validate_string],
                                help_text='Текущая стоимость валюты/монеты выраженная в USD(T)')
    time = models.DateTimeField('Время обновления котировки', auto_now=True)
    tiker = models.CharField('Тикер с Binance', help_text=help_string, blank=True, max_length=20)
    conformation = models.PositiveSmallIntegerField('Подтверждения', default=1,
                                                    help_text='Количество необходимых подтверждения для начала перевода. Актуально только для крипты')

    def save(self, *args, **kwargs):
        self.cost, self.cost_str = copy_str_to_decimal(self.cost_str)

        if self.tiker == '':
            if self.money_type == 'crypto':
                if self.abc_code == 'USDT':
                    self.tiker = 'USDT'
                else:
                    self.tiker = self.abc_code + 'USDT'
        super(Money, self).save(*args, **kwargs)

    def __str__(self):
        return self.abc_code + ': ' + self.title

    class Meta:
        verbose_name = 'Валюта/Монета'
        verbose_name_plural = '05. Валюты/Монеты'
        ordering = ['-active', 'money_type', 'abc_code', 'title']


class PaySystem(Commisions):  # список платёжных систем: киви, яндекс, вебмани и т.д.
    active = models.BooleanField('Использовать', default=False)
    title = models.CharField('Название', max_length=100, help_text='Название платёжной системы', unique=True)


    def save(self, *args, **kwargs):
        self.fee_percent, self.fee_percent_str = copy_str_to_decimal(self.fee_percent_str)
        self.fee_absolut, self.fee_absolut_str = copy_str_to_decimal(self.fee_absolut_str)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Платёжная система'
        verbose_name_plural = '06. Платёжные системы'
        ordering = ['-active', '-title']


class FullMoney(Commisions):  # объединили монетки и платёжные системы
    active = models.BooleanField('Использовать', default=False)
    title = models.CharField('Название', max_length=30, unique=True, help_text='Это название отображается на сайте')
    xml_code = models.CharField('XML', max_length=20,
                                help_text='Буквенный код валюты для экспорта. Взято с https://jsons.info/signatures/currencies')
    pay = models.ForeignKey(PaySystem, verbose_name='Платёжная система', on_delete=models.CASCADE, blank=True,
                            null=True, help_text='У крипты платёжная система может отсутствовать')
    money = models.ForeignKey(Money, verbose_name='Код валюты', on_delete=models.CASCADE)
    reserv = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS, editable=False)
    reserv_str = models.CharField('Резерв', max_length=MAX_DIGITS, help_text='Доступный для обмена резерв',
                                  default='0.0', validators=[validate_string])
    logo = models.FileField('Логотип', upload_to='static/img/money', default='', blank=True)

    def save(self, *args, **kwargs):
        self.reserv, self.reserv_str = copy_str_to_decimal(self.reserv_str)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Валюта+ПС'
        verbose_name_plural = '04. Валюта+ПС'
        ordering = ('title',)
        unique_together = ('pay', 'money')


class SwapMoney(models.Model):  # Основная таблица настроек обменов.
    active = models.BooleanField('Вкл', default=False, help_text='Включить или отключить данный обмен')
    money_left = models.ForeignKey(FullMoney, verbose_name='Монета слева', on_delete=models.CASCADE,
                                   related_name='money_left_re')
    money_right = models.ForeignKey(FullMoney, verbose_name='Монета справа', on_delete=models.CASCADE,
                                    related_name='money_right_re')

    min_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    max_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    min_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    max_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    min_left_str = models.CharField('Минимум слева', max_length=MAX_DIGITS, default='0.0',
                                    validators=[validate_string])
    max_left_str = models.CharField('Максимум слева', max_length=MAX_DIGITS, default='0.0',
                                    validators=[validate_string])
    min_right_str = models.CharField('Минимум справа', max_length=MAX_DIGITS, default='0.0',
                                     validators=[validate_string])
    max_right_str = models.CharField('Максимум справа', max_length=MAX_DIGITS, default='0.0',
                                     validators=[validate_string])

    rate_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    rate_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    rate_left_str = models.CharField('Курс слева', max_length=MAX_DIGITS, default='1', validators=[validate_string])
    rate_right_str = models.CharField('Курс справа', max_length=MAX_DIGITS, default='1', validators=[validate_string],
                                      help_text='Начальный курс, полученный с ЦБ, Binance или BestChange. Менять не рекомендуется. Данный курс периодически изменяется автоматически')

    change_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    change_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    change_left_str = models.CharField('+/- % слева', max_length=MAX_DIGITS, default='0.0',
                                       validators=[validate_string])
    change_right_str = models.CharField('+/- % справа', max_length=MAX_DIGITS, default='0.0',
                                        validators=[validate_string],
                                        help_text='Изменение курса в % (прибыль) Пример расчёта: Если = 5, то курс умножается на 1.05, если = -5, то на 0.95.')

    rate_left_final = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    rate_right_final = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    rate_left_final_str = models.CharField('Итого слева', max_length=MAX_DIGITS, default='0.0',
                                           validators=[validate_string])
    rate_right_final_str = models.CharField('Итого справа', max_length=MAX_DIGITS, default='0.0',
                                            validators=[validate_string],
                                            help_text='Итоговый курс. Если в результате расчётов получился итоговый курс <= 0, то автоматически устанавливается значение = 1')

    add_fee_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    add_fee_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    add_fee_left_str = models.CharField('Доп слева', max_length=MAX_DIGITS, default='0.0',
                                        validators=[validate_string])
    add_fee_right_str = models.CharField('Доп справа', max_length=MAX_DIGITS, default='0.0',
                                         validators=[validate_string],
                                         help_text='Сумма фиксированной удерживаемой комисии. На курс обмена не влияет, изменяется только итоговая отдаваемая сумма!')

    manual_active = models.BooleanField('Ручной курс', default=False,
                                        help_text='Курс установленный вручную является приоритетным')
    manual_rate_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    manual_rate_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    manual_rate_left_str = models.CharField('Ручной курс слева', max_length=MAX_DIGITS, default='0.0',
                                            validators=[validate_string])
    manual_rate_right_str = models.CharField('Ручной курс справа', max_length=MAX_DIGITS, default='0.0',
                                             validators=[validate_string])

    freeze = models.PositiveIntegerField('Заморозка', default=0, help_text='Заморозка средств при обмене, в минутах.')
    # city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город', null=True, blank=True,
    #                          help_text='Город для обмена. Актуально только для обмена с наличными деньгами', default='')
    time = models.DateTimeField('Время установки курса', auto_now=True)
    best_place = models.PositiveSmallIntegerField('BC', default=1,
                                                  help_text='Необходимое место на BestChange, если обмен не найден, '
                                                            'то место устанавливается в 0, а курс устанавливается с ЦБ или Binance.'
                                                            ' Если по ЦБ и Binance также не удалось установить, то используются '
                                                            'значения из ручного курса. Если необходимо занять '
                                                            'последнее место на Bestchange, то можно поставить большое '
                                                            'число, к примеру 1000. Если курс устанавливается в зависимости от места на Bestchange, '
                                                            'то никакие дополнительные комиссии на него не действуют.')
    city = models.ManyToManyField(City, blank=True, verbose_name='Города на обмена наличных', )
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

    def save(self, *args, **kwargs):
        def round_string(mmstr, rnd_num):
            mmstr = mmstr.replace(',', '.').split('.')
            if len(mmstr) > 1:
                mmstr[1] = mmstr[1][:rnd_num]
            return '.'.join(mmstr)

        set_seo(self)
        # set_change_rate(self)

        rnd_left = 2
        rnd_right = 2
        if self.money_left.money.money_type == 'crypto':
            rnd_left = 8
        if self.money_right.money.money_type == 'crypto':
            rnd_right = 8

        self.min_left, self.min_left_str = copy_str_to_decimal(round_string(self.min_left_str, rnd_left))
        self.max_left, self.max_left_str = copy_str_to_decimal(round_string(self.max_left_str, rnd_left))
        self.min_right, self.min_right_str = copy_str_to_decimal(round_string(self.min_right_str, rnd_right))
        self.max_right, self.max_right_str = copy_str_to_decimal(round_string(self.max_right_str, rnd_right))

        self.rate_left, self.rate_left_str = copy_str_to_decimal(self.rate_left_str)
        self.rate_right, self.rate_right_str = copy_str_to_decimal(self.rate_right_str)

        self.change_left, self.change_left_str = copy_str_to_decimal(self.change_left_str)
        self.change_right, self.change_right_str = copy_str_to_decimal(self.change_right_str)

        self.rate_left_final, self.rate_left_final_str = copy_str_to_decimal(self.rate_left_final_str)
        self.rate_right_final, self.rate_right_final_str = copy_str_to_decimal(self.rate_right_final_str)

        self.add_fee_left, self.add_fee_left_str = copy_str_to_decimal(self.add_fee_left_str)
        self.add_fee_right, self.add_fee_right_str = copy_str_to_decimal(self.add_fee_right_str)

        self.manual_rate_left, self.manual_rate_left_str = copy_str_to_decimal(self.manual_rate_left_str)
        self.manual_rate_right, self.manual_rate_right_str = copy_str_to_decimal(self.manual_rate_right_str)

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.money_left) + " -> " + str(self.money_right)

    class Meta:
        verbose_name = 'Обмен: Настройки'
        verbose_name_plural = '02. Обмен: Настройки'
        unique_together = ['money_left', 'money_right']


class Wallets(models.Model):
    fullmoney = models.ForeignKey(FullMoney, on_delete=models.CASCADE, verbose_name='Кошелёк')
    name = models.CharField('Номер кошелька', max_length=100)

    def __str__(self):
        return self.fullmoney.title + ': ' + self.name

    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = '03. Кошельки'


class SwapOrders(models.Model):
    ORDERS_STATUS = (
        ('new', 'Новая'),
        ('cancel', 'Отмена'),
        ('end', 'Завершена'),
        ('error', 'Ошибка'),
        ('back', 'Возврат'),
        ('pause', 'Ожидание клиента'),
    )
    status = models.CharField('Статус сделки', max_length=100, choices=ORDERS_STATUS, default='new')
    num = models.CharField('Номер сделки', max_length=15, unique=True)
    swap_create = models.DateTimeField('Время сделки', auto_now=True, editable=False)
    money_left = models.ForeignKey(FullMoney, verbose_name='Монета слева', on_delete=models.CASCADE,
                                   related_name='swap_orders_left')
    money_right = models.ForeignKey(FullMoney, verbose_name='Монета справа', on_delete=models.CASCADE,
                                    related_name='swap_orders_right')
    left_in = models.CharField('Приход', max_length=50, help_text='Сколько денег пришло')
    right_out = models.CharField('Расход', max_length=50, help_text='Сколько денег ушло')
    pl = models.FloatField('Прибыль', default=0,
                           help_text='Прибыль рассчитывается в USD по курсу на момент сделки')
    wallet_in = models.ForeignKey(Wallets, on_delete=models.CASCADE, verbose_name='Кошелёк обменника', blank=True,
                                  null=True, related_name='wallet_in')
    wallet_out = models.ForeignKey(Wallets, on_delete=models.CASCADE, verbose_name='Кошелёк клиента', blank=True,
                                   null=True, related_name='wallet_out')
    phone = models.CharField('Телефон', max_length=20, default='', blank=True)
    email = models.EmailField('Почта', default='', blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь', null=True,
                             blank=True)
    comment = models.TextField('Комментарий', blank=True, help_text='Любой необходимый для себя комментарий')

    def __str__(self):
        return str(self.money_left.title) + ' -> ' + str(self.money_right.title)

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
        verbose_name_plural = '10. Информация'
        ordering = ['-time', ]


class AddFields(models.Model):
    # Модель для дополнительных полей, нужных для обмена. Необходимо две идентичных модели для левой и правой монеты
    title = models.CharField('Название', max_length=20, unique=True)
    pay = models.ForeignKey(FullMoney, on_delete=models.CASCADE)

    def __str__(self):
        return ''

    class Meta:
        abstract = True


class FieldsLeft(AddFields):
    pass


class FieldsRight(AddFields):
    pass


class Monitoring(models.Model):
    active = models.BooleanField('Использовать', default=True)
    title = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка')
    logo = models.FileField('Лого', upload_to='static/img/monitor/', default='', blank=True)
    connect = models.ForeignKey(Settings, on_delete=models.CASCADE, verbose_name='Партнёр')

    def __str__(self):
        return self.title
