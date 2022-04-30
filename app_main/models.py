import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from Changebox import settings
from app_main.lib.number_2_str import number_2_str
from app_main.lib.remove_space_from_string import remove_space_from_string
from app_main.lib.set_seo import set_seo
from app_main.lib.set_single_rate import set_single_rate
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

RULES = '''
<p><strong>1. Стороны соглашения.</strong></p>
<p>Договор заключается между интернет сервисом по обмену титульных знаков, далее Исполнитель, — с одной стороны, и
    Заказчик, в лице того, кто воспользовался услугами Исполнителя, — с другой стороны.</p>
<p><strong>2. Список терминов.</strong></p>
<p>2.1. Обмен титульных знаков — автоматизированный продукт интернет обслуживания, который предоставляется Исполнителем
    на основании данных правил.<br>
    2.2. Заказчик — физическое лицо, соглашающееся с условиями Исполнителя и данного соглашения, к которому
    присоединяется.<br>
    2.3. Титульный знак — условная единица той или иной платежной системы, которая соответствует расчетам электронных
    систем и обозначает объем прав, соответствующих договору системы электронной оплаты и ее Заказчика.<br>
    2.4. Заявка — сведения, переданные Заказчиком для использования средств Исполнителя в электронном виде и
    свидетельствующие о том, что он принимает условия пользования сервисом, которые предлагаются Исполнителем в данной
    заявке.</p>
<p><strong>3. Условия соглашения.</strong></p>
<p>Данные правила считаются организованными за счет условий общественной оферты, которая образуется во время подачи
    Заказчиком заявки и является одной из главных составляющих настоящего договора. Общественной офертой именуются
    отображаемые исполнителем сведения об условиях подачи заявки. Главным составляющим общественной оферты являются
    действия, сделанные в завершении подачи заявки Заказчиком и говорящие о его точных намерениях совершить сделку на
    условиях предложенных Исполнителем перед завершением данной заявки. Время, дата, и параметры заявки создаются
    Исполнителем автоматически в момент окончания формирования данной заявки. Предложение должно приняться Заказчиком в
    течение 24 часов от окончания формирования заявки. Договор по обслуживанию вступает в силу с момента поступления
    титульных знаков в полном размере, указанном в заявке, от Заказчика на реквизиты Исполнителя. Операции с титульными
    знаками учитываются согласно правилам, регламенту и формату электронных систем по расчетам. Договор действителен в
    течение срока , который устанавливается с момента подачи заявки до расторжения по инициативе одной из сторон.</p>
<p><strong>4. Предмет соглашения.</strong></p>
<p>Путем использования технических методов Исполнитель обязуется выполнять обмен титульных знаков за комиссионное
    вознаграждение от Заказчика, после подачи данным лицом заявки и совершает это путем продажи титульных знаков лицам,
    желающим их приобрести по сумме, указанной не ниже, чем в заявке поданной Заказчиком. Денежные средства Исполнитель
    обязуется переводить на указанные Заказчиком реквизиты. В случае возникновения во время обмена прибыли, она остается
    на счету Исполнителя, как дополнительная выгода и премия за комиссионные услуги.</p>
<p><strong>5. В дополнение.</strong></p>
<p>5.1. Если на счет Исполнителя поступает сумма, отличающаяся от указанной в заявке, Исполнитель делает перерасчет,
    который соответствует фактическому поступлению титульных знаков. Если данная сумма превышает указанную в заявке
    более чем на 10%, Исполнитель расторгает договор в одностороннем порядке и все средства возвращаются на реквизиты
    Заказчика, с учетом вычтенной суммы на комиссионные расходы во время перевода.<br>
    5.2. В случае, когда титульные знаки не отправляются Исполнителем на указанные реквизиты Заказчика в течение 24
    часов, Заказчик имеет полное право потребовать расторжение соглашения и аннулировать свою заявку, тем самым совершая
    возврат титульных знаков на свой счет в полном объеме. Заявка на расторжение соглашения и возврата титульных знаков
    выполняется Исполнителем в том случае, если денежные средства еще не были переведены на указанные реквизиты
    Заказчика. В случае аннулирования договора, возврат электронной валюты производится в течение 24 часов с момента
    получения требовании о расторжении договора. Если задержки при возврате возникли не по вине Исполнителя, он не несет
    за них ответственности.<br>
    5.3. Если титульные знаки не поступаеют от Заказчика на счет Исполнителя в течение указанного срока, с момента
    подачи заявки Заказчиком, соглашение между сторонами расторгается Исполнителем с одной стороны, так как договор не
    вступает в действие. Заказчик может об этом не уведомляться. Если титульные знаки поступает на реквизиты Исполнителя
    после указанного срока, то такие средства переводятся обратно на счет Заказчика, причем все комиссионные расходы,
    связанные с переводом, вычитаются из данных средств.<br>
    5.4. Если происходит задержка перевода средств на реквизиты, указанные Заказчиком, по вине расчетной системы,
    Исполнитель не несет ответственности за ущерб, возникающий в результате долгого поступления денежных средств. В этом
    случае Заказчик должен согласиться с тем, что все претензии будут предъявляться к расчетной системе, а Исполнитель
    оказывает свою помощь по мере своих возможностей в рамках закона.<br>
    5.5. В случае обнаружения подделки коммуникационных потоков или оказания воздействия, с целью ухудшить работу
    Исполнителя, а именно его программного кода, заявка приостанавливается, а переведенные средства подвергаются
    перерасчету в соответствии с действующим соглашением. Если Заказчик не согласен с перерасчетом, он имеет полное
    право расторгнуть договор и титульные знаки отправятся на реквизиты указанные Заказчиком.<br>
    5.6. В случае пользования услугами Исполнителя, Заказчик полностью соглашается с тем, что Исполнитель несет
    ограниченную ответственность соответствующую рамкам настоящих правил полученных титульных знаков и не дает
    дополнительных гарантий Заказчику, а также не несет перед ним дополнительной ответственности. Соответственно
    Заказчик&nbsp; не несет дополнительной ответственности перед Исполнителем.<br>
    5.7. Заказчик обязуется выполнять нормы соответствующие законодательству, а также не подделывать коммуникационные
    потоки и не создавать препятствий для нормальной работы программного кода Исполнителя.<br>
    5.8.Исполнитель не несет ответственности за ущерб и последствия при ошибочном переводе электронной валюты в том
    случае, если Заказчик указал при подаче заявки неверные реквизиты.</p>
<p><strong>6. Гарантийный срок</strong></p>
<p>В течение 24 часов с момента исполнения обмена титульных знаков Исполнитель дает гарантию на оказываемые услуги при
    условии, если не оговорены иные сроки.</p>
<p><strong>7. Непредвиденные обстоятельства.</strong></p>
<p>В случае, когда в процессе обработки заявки Заказчика возникают непредвиденные обстоятельства, способствующие
    невыполнению Исполнителем условий договора, сроки выполнения заявки переносятся на соответствующий срок длительности
    форс-мажора. За просроченные обязательства Исполнитель ответственности не несет.</p>
<p><strong>8. Форма соглашения.</strong></p>
<p>Данное соглашение обе стороны, в лице Исполнителя и Заказчика, принимают как равноценный по юридической силе договор,
    обозначенный в письменной форме.</p>
<p><strong>9. Работа с картами Англии, Германии и США.</strong></p>
<p>Для владельцев карт стран Англии, Германии и США условия перевода титульных знаков продляются на неопределенный срок,
    соответствующий полной проверке данных владельца карты. Денежные средства в течение всего срока не подвергаются
    никаким операциям и в полном размере находятся на счете Исполнителя.</p>
<p><strong>10 Претензии и споры.</strong></p>
<p>Претензии по настоящему соглашению принимаются Исполнителем в форме электронного письма, в котором Заказчик указывает
    суть претензии. Данное письмо отправляется на указанные на сайте реквизиты Исполнителя.</p>
<p><strong>11. Проведение обменных операций.</strong></p>
<p>11.1.Категорически запрещается пользоваться услугами Исполнителя для проведения незаконных переводов и мошеннических
    действий. При заключении настоящего договора, Заказчик обязуется выполнять эти требования и в случае мошенничества
    нести уголовную ответственность, установленную законодательством на данный момент.<br>
    11.2. В случае невозможности выполнения заявки автоматически, по не зависящим от Исполнителя обстоятельствам, таким
    как отсутствие связи, нехватка средств, или же ошибочные данные Заказчика, средства поступают на счет в течение
    последующих 24 часов или же возвращается на реквизиты Заказчика за вычетом комиссионных расходов.<br>
    11.3.По первому требованию Исполнитель вправе передавать информацию о переводе электронной валюты правоохранительным
    органам, администрации расчетных систем, а также жертвам неправомерных действий, пострадавшим в результате
    доказанного судебными органами мошенничества.<br>
    11.4. Заказчик обязуется представить все документы, удостоверяющие его личность, в случае подозрения о мошенничестве
    и отмывании денег.<br>
    11.5. Заказчик обязуется не вмешиваться в работу Исполнителя и не наносить урон его программной и аппаратной части,
    а также Заказчик обязуется передавать точные сведения для обеспечения выполнения Исполнителем всех условий договора.
</p>
<p><strong>12.Отказ от обязательств.</strong></p>
<p>Исполнитель имеет право отказа на заключение договора и выполнение заявки, причем без объяснения причин. Данный пункт
    применяется по отношению к любому клиенту.</p>

'''
SECURITY = '''
<p>
    1. <strong>Назначение и область применения Положения об обработке и защите персональных данных сервисом
        domain_name</strong><br>
    1.1. Настоящее Положение устанавливает порядок получения, учета, обработки, накопления и хранения сведений,
    отнесенных к персональным данным Пользователей Сервиса.<br>
    1.2. Настоящее Положение действует в соответствии с Правилами предоставления услуг сервисом domain_name (далее
    по тексту Сервис). Все значения терминов и определений, применяемых в настоящем Положении, соответствуют значениям,
    раскрытым в Правилах.<br>
    1.3. Под Пользователями подразумеваются лица, являющиеся стороной Оферты, в соответствии с Правилами предоставления
    услуг Сервисом.<br>
    1.4. Цель настоящего Положения – защита персональных данных Пользователей от несанкционированного доступа и
    разглашения. Персональные данные всегда являются конфиденциальной, строго охраняемой информацией.<br>
    1.5. Сервис размещается на территории государства Нидерланды. Настоящее Положение разработано в соответствии с
    «Общим регламентом защиты персональных данных» Европейского союза (General Data Protection Regulation, GDPR;
    Постановление Европейского Союза 2016/679).<br>
    1.6. Действующая версия Положения расположена для публичного доступа на сайте Сервиса. Администрация Сервиса вправе
    в любое время в одностороннем порядке изменять настоящее Положение. Такие изменения вступают в силу по истечении 3
    (трех) календарных дней с момента размещения новой версии Положения на сайте, если иной порядок вступления не
    предусмотрен специально в новой версии Положения. При несогласии Пользователя с внесенными изменениями он обязан
    направить соответствующее письмо на электронную почту, указанную на данном сайте.</p>
<p>2. <strong>Понятие и состав персональных данных </strong><br>
    2.1. Под персональными данными Пользователей понимается информация, необходимая работодателю в связи с трудовыми
    отношениями и касающаяся конкретного работника, а также сведения о фактах, событиях и обстоятельствах жизни
    работника, позволяющие идентифицировать его личность.<br>
    2.2. Состав персональных данных:<br>
    2.2.1. Личные данные<br>
    2.2.1.1. При использовании Сервиса, администрация может попросить Пользователя предоставить определенную личную
    информацию, которую Сервис использует для связи с Пользователем или его идентификации («Личные данные»).<br>
    2.2.1.2. Идентификационная информация может включать, но не ограничивается:<br>
    • Email адрес;<br>
    • Имя и Фамилия;<br>
    • Телефонный номер;<br>
    • Адрес, Город, Страна, Почтовый индекс и другие данные.<br>
    2.2.2. Cookies и Данные об использовании<br>
    2.2.2.1. Сервис также может собирать информацию о доступе к Сервису и его использовании («Данные об использовании»).<br>
    Эти данные могут включать в себя следующую информацию:<br>
    • Адрес интернет-протокола компьютера Пользователя (например, IP-адрес);<br>
    • Тип браузера;<br>
    • Версию браузера;<br>
    • Версию страницы Сервиса;<br>
    • Время посещения страниц Сервиса, время, потраченное на эти страницы;<br>
    • Уникальные идентификаторы устройств и другие диагностические данные.<br>
    2.2.2.2. Сервис использует файлы coоkie и аналогичные технологии для отслеживания активности на Сервисе и хранения
    определенной информации.<br>
    Файлы coоkie представляют собой файлы с небольшим количеством данных, которые могут включать анонимный уникальный
    идентификатор. Cookies-файлы отправляются в браузер Пользователя с веб-сайта и хранятся на устройстве Пользователя.
    Технологии отслеживания, которые также используются — теги и сценарии для сбора и отслеживания информации, а также
    для улучшения и анализа работы Сервиса.<br>
    2.3. Пользователь может отказаться от всех файлов coоkie или указать, когда отправлять coоkie-файл.<br>
    2.4. Если Пользователь не принимает файлы coоkie, то Пользователь понимает и принимает обстоятельства того, что
    объем использования функций Сервиса может быть ограничен.<br>
    2.5. Примеры используемых Сервисом Cookies:<br>
    • Сессионные файлы Cookies (используются для управления Сервисом);<br>
    • Cookies предпочтений (используются Сервисом для запоминания предпочтений Пользователя и различных настроек);<br>
    • Cookies безопасности (используются Сервисом для обеспечения безопасности).</p>
<p>3. Сбор персональных данных Пользователей<br>
    3.1. Сбор персональных данных Пользователей является составляющей частью процесса обработки таких персональных
    данных, что предусматривает действия по подбору или упорядочению сведений о Пользователе Сервиса.<br>
    3.2. Основаниями для обработки персональных данных Пользователей являются:<br>
    • заключение и исполнение Оферты, в соответствии с Правилами, стороной которой является субъект персональных данных
    – Пользователь;<br>
    • необходимость защиты законных интересов владельцев персональных данных, кроме случаев, когда субъект персональных
    данных требует прекратить обработку его персональных данных и необходимости защиты персональных данных превышают
    такой интерес.<br>
    3.3. Факт ознакомления Пользователя с правами в сфере защиты персональных данных, сообщение о владельце персональных
    данных, состав и содержание собранных персональных данных, цель сбора персональных данных и лица, которым будут
    передаваться персональные данные, подтверждается акцептом Оферты, в соответствии с Правилами.<br>
    3.4. В случае выявления факта обработки сведений о Пользователе, которые не соответствуют действительности, такие
    сведения должны быть исправлены или уничтожены.</p>
<p>4. Хранение и уничтожение персональных данных Пользователей<br>
    4.1. Хранение персональных данных предусматривает действия по обеспечению их целостности и соответствующего режима
    доступа к ним.<br>
    4.2. Персональные данные Пользователей обрабатываются в форме, допускающей идентификацию лица, которого они
    касаются, и хранятся в срок не более, чем это необходимо в соответствии с их законным назначением и целью их
    обработки, если иное не предусмотрено законодательством в сфере архивного дела и делопроизводства.<br>
    4.3. Персональные данные Пользователей удаляются или уничтожаются в порядке, установленном в соответствии с
    требованиями закона.<br>
    4.4. Персональные данные подлежат уничтожению в случае:<br>
    • окончания срока хранения данных, определенного согласием субъекта (Пользователя) персональных данных на обработку
    этих данных или законом;<br>
    • прекращения правоотношений между Пользователем и Сервисом, если иное не предусмотрено законом;<br>
    • вступления в законную силу решения суда об изъятии данных о Пользователе из базы персональных данных;<br>
    4.5. Уничтожение персональных данных проводится способом, исключающим дальнейшую возможность восстановления таких
    персональных данных.</p>
<p>5. Использование данных<br>
    Сервис использует собранные данные для различных целей:<br>
    5.1. Обеспечение участия Пользователя в интерактивных функциях Сервиса;<br>
    5.2. Обеспечение поддержки и обслуживания Пользователей;<br>
    5.3. Проведение анализа для улучшения работы Сервиса;<br>
    5.4. Мониторинг использования Сервиса;<br>
    5.5. Предотвращение, обнаружение и устранение технических проблем в работе Сервиса;<br>
    5.6. Уведомление Пользователя об изменениях в Сервисе.</p>
<p>6. Передача персональных данных третьим лицам и предоставление третьим лицам доступа к персональным данным
    Пользователей<br>
    6.1. Передача персональных данных Пользователей третьим лицам определяется условиями согласия на обработку
    персональных данных или в соответствии с требованиями закона.<br>
    6.2. Доступ к персональным данным третьему лицу предоставляется только в соответствии с «Общим регламентом защиты
    персональных данных».<br>
    6.3. Пользователь имеет право на получение любых сведений о себе, содержащиеся в распоряжении Сервиса, без указания
    цели запроса.<br>
    6.4. Сервис может использовать сторонних поставщиков услуг для мониторинга и анализа использования Сервиса:<br>
    6.4.1. Google Analytics — это служба веб-аналитики, предлагаемая Google, которая отслеживает и сообщает о трафике
    веб-сайта. Google использует собранные данные для отслеживания и контроля использования Сервиса. Эти данные
    предоставляются другим службам Google. Google может использовать собранные данные для контекстуализации и
    персонализации рекламы своей собственной рекламной сети.<br>
    6.4.2. Пользователь может отказаться от того, чтобы предоставить информацию об активности на Сервисе доступным для
    Google Analytics, установив надстройку браузера Google Analytics для отказа. Надстройка не позволяет Google
    Analytics JavaScript (ga.js, analytics.js и dc.js) обмениваться информацией с Google Analytics об активности
    Пользователя на сайте Сервиса.<br>
    6.4.3. Пользователь может ознакомиться с правилами конфиденциальности Google в разделе «Политика конфиденциальности
    и Условия использования» на сайте Google.</p>
<p>7. Cсылки на сторонние сайты<br>
    7.1. Сервис может содержать ссылки на сторонние сайты, которые не управляются Сервисом.<br>
    7.2. Если Пользователь переходит по ссылке по такой ссылке, то он попадет на сайт третьей стороны. Администрация
    сервиса настоятельно рекомендует пользователю ознакомиться с Политикой конфиденциальности каждого стороннего сайта,
    который Пользователь посещает.<br>
    7.3. Сервис не контролирует и не несет ответственности за контент, политику конфиденциальности или действия
    сторонних сайтов и служб.</p>
'''
WARNING = '''
<ul>
    <li>Проверьте сумму перевода и получения</li>
    <li>Проверьте кошелёк получателя</li>
</ul>
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
    reload_url = models.CharField('Технический адрес', max_length=50, default='pause_url')
    pause = models.BooleanField('Перерыв', default=False, help_text='Сайт не работает. На главной висит перерыв')
    reload_exchange = models.BooleanField('Технический перерыв', default=False,
                                          help_text='Сайт не работает. На главной висит перерыв, но есть доступ к сайту по техническому адресу, для проведения тестов. Рекомендуется поменять')
    job_start = models.PositiveSmallIntegerField('Час начала работы', default=0)
    job_end = models.PositiveSmallIntegerField('Час окончания работы', default=24)
    off_money = models.BooleanField('Отключать монеты', default=True,
                                    help_text='Отключать монеты и валюты, котировки которых небылы найдены среди ЦБ или Binance')
    logo = models.FileField('Логотип', upload_to='static/img/logo', default='', blank=True)
    exchane_name = models.CharField('Название на сайт', max_length=200, default='Exchange Money')
    rules_exchange = models.TextField('Правила обменника', default=RULES,
                                      help_text='Можно писать с html тэгами. Слово в тексте domain_name заменяется на текущий домен')
    rules_security = models.TextField('Политика безопасности', default=SECURITY,
                                      help_text='Можно писать с html тэгами. Слово в тексте domain_name заменяется на текущий домен')
    rules_warning = models.TextField('Выдержка из правил', default=WARNING,
                                     help_text='Главные тезисы при совершении обмена. Отображаются на странице совершения обмена. Можно писать с html тэгами. Слово в тексте domain_name заменяется на текущий домен')
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
        verbose_name = 'Валюта'
        verbose_name_plural = '05. Валюты'
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

    rate_left_str = models.CharField('Курс слева', max_length=MAX_DIGITS, default='0.0', validators=[validate_string])
    rate_right_str = models.CharField('Курс справа', max_length=MAX_DIGITS, default='0.0', validators=[validate_string],
                                      help_text='Курс, полученный с ЦБ, Binance или BestChange.')

    change_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    change_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    change_left_str = models.CharField('+/- % слева', max_length=MAX_DIGITS, default='0.0',
                                       validators=[validate_string])
    change_right_str = models.CharField('+/- % справа', max_length=MAX_DIGITS, default='0.0',
                                        validators=[validate_string],
                                        help_text='Изменение курса в %')

    rate_left_final = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    rate_right_final = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    rate_left_final_str = models.CharField('Итого слева', max_length=MAX_DIGITS, default='0.0',
                                           validators=[validate_string])
    rate_right_final_str = models.CharField('Итого справа', max_length=MAX_DIGITS, default='0.0',
                                            validators=[validate_string],
                                            help_text='Итоговый курс. Изменяется автоматически')

    add_fee_left = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)
    add_fee_right = models.DecimalField(default=0, decimal_places=DECIMAL_PLACES, max_digits=MAX_DIGITS)

    add_fee_left_str = models.CharField('Доп слева', max_length=MAX_DIGITS, default='0.0',
                                        validators=[validate_string])
    add_fee_right_str = models.CharField('Доп справа', max_length=MAX_DIGITS, default='0.0',
                                         validators=[validate_string],
                                         help_text='Сумма фиксированной удерживаемой комисии.')

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
        set_single_rate(self)

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
