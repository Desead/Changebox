import random
import xml.etree.ElementTree as xml
from decimal import Decimal
from string import ascii_letters

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from app_main.forms import CustomUserCreationForm
from app_main.lib.get_pause import get_pause
from app_main.models import SwapMoney, FieldsLeft, FieldsRight, Settings, InfoPanel, SwapOrders, FullMoney, CustomUser, \
    Monitoring


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class StartView(View):
    def get(self, request):
        temp = Settings.objects.first()

        job_start = temp.job_start
        job_end = temp.job_end

        if job_start == job_end or (job_start == 0 and job_end == 24) or (job_start == 24 and job_end == 00):
            time_job = 'Круглосуточно'
        else:
            time_job = f' с {job_start}:00 по {job_end}:00 (МСК)'

        if get_pause(temp):
            return render(request, 'pause.html', {'settings': temp})

        while True:
            num = ''.join([random.choice(ascii_letters) for i in range(15)])
            if SwapOrders.objects.filter(num=num).count() == 0:
                break

        last_swap = SwapOrders.objects.all().order_by('-swap_create')

        context = {
            'settings': temp,
            'time_job': time_job,
            'num': num,
            'monitors': Monitoring.objects.filter(connect=temp.pk, active=True),
            'last_swap': last_swap,
        }

        return render(request, 'index.html', context)


class LKView(View):
    def get(self, request):
        print(request.user)
        context = {'settings': Settings.objects.first(),
                   'user': CustomUser.objects.get(email=request.user),
                   'orders': SwapOrders.objects.filter(user__email=request.user)}
        return render(request, 'lk.html', context)


class FAQView(View):
    def get(self, request):
        context = {'settings': Settings.objects.first()}
        return render(request, 'faq.html', context)


class FeedbackView(View):
    def get(self, request):
        context = {'settings': Settings.objects.first()}
        return render(request, 'feedback.html', context)


class RulesView(View):
    def get(self, request):
        context = {'settings': Settings.objects.first()}
        return render(request, 'rules.html', context)


class SecurityView(View):
    def get(self, request):
        context = {'settings': Settings.objects.first()}
        return render(request, 'security.html', context)


class ConfirmView(View):
    def post(self, request):
        context = {'settings': Settings.objects.first()}
        if request.POST.get('cancel'):
            order = SwapOrders.objects.filter(num=request.POST.get('num'))
            if order.count() == 1:
                order = order[0]
                order.status = 'cancel'
                order.save()
                context['order'] = order

            return render(request, 'cancel_swap.html', context)

        fullmoney = FullMoney.objects.all()

        if request.user.is_authenticated:
            user = CustomUser.objects.get(email=request.user)
        else:
            user = None

        order = SwapOrders.objects.get_or_create(
            money_left=fullmoney.get(xml_code=request.POST.get('money_left')),
            money_right=fullmoney.get(xml_code=request.POST.get('money_right')),
            left_in=request.POST.get('left_sum'),
            right_out=request.POST.get('right_sum'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            num=request.POST.get('num'),
            user=user,
        )

        context['order'] = order[0]
        return render(request, 'confirm.html', context)


def ExportXML(request):
    # добавить ограничения по монетам и резервам
    root_element = xml.Element('rates')

    if get_pause(Settings.objects.first()):
        return HttpResponse(xml.tostring(root_element, method='xml', encoding='utf8'), content_type='text/xml')

    rates = SwapMoney.objects.filter(active=True, money_left__money__active=True, money_left__active=True,
                                     money_right__active=True, money_right__money__active=True)

    for i in rates:
        # Минимумы и максимум для обмена надо высчитывать для левой монеты, поэтому правый мин и макс переводим в левую валюту
        # начальный курс обмена должен уже учитывать номинал, поэтому здесь в расчётах он не участвует

        if (i.rate_right_final <= 0 or i.rate_left_final <= 0):
            continue

        min_right_to_left = i.min_right / i.rate_right_final * i.rate_left_final
        minamount = max(i.min_left, min_right_to_left)

        max_right_to_left = i.max_right / i.rate_right_final * i.rate_left_final
        if 0 in (i.max_left, max_right_to_left):  # избавляемся от 0 в сравнении
            maxamount = max(i.max_left, max_right_to_left)
        else:
            maxamount = min(i.max_left, max_right_to_left)

        if 0 < maxamount < minamount: continue

        item_element = xml.Element('item')
        root_element.append(item_element)

        # создаем дочерние суб-элементы.
        from_element = xml.SubElement(item_element, 'from')
        from_element.text = i.money_left.xml_code

        to_element = xml.SubElement(item_element, 'to')
        to_element.text = i.money_right.xml_code

        in_element = xml.SubElement(item_element, 'in')
        in_element.text = str(i.rate_left_final)

        out_element = xml.SubElement(item_element, 'out')
        out_element.text = str(i.rate_right_final)

        amount_element = xml.SubElement(item_element, 'amount')
        amount_element.text = str(i.money_right.reserv)

        if i.money_left.money.money_type == 'fiat':  # до скольки знаков округлять вывод чисел
            round_num = 2
        else:
            round_num = 8

        if minamount > 0:
            minamount_element = xml.SubElement(item_element, 'minamount')
            minamount_element.text = str(round(minamount, round_num)) + ' ' + i.money_left.money.abc_code
        if maxamount > 0:
            maxamount_element = xml.SubElement(item_element, 'maxamount')
            maxamount_element.text = str(round(maxamount, round_num)) + ' ' + i.money_left.money.abc_code

        if i.add_fee_left > 0:
            fromfee = xml.SubElement(item_element, 'fromfee')
            fromfee.text = str(round(i.add_fee_left, round_num)) + ' ' + i.money_left.money.abc_code

        if i.add_fee_right > 0:
            tofee = xml.SubElement(item_element, 'tofee')
            tofee.text = str(round(i.add_fee_right, round_num)) + ' ' + i.money_right.money.abc_code

        param = []
        if i.manual: param.append('manual')
        if i.juridical: param.append('juridical')
        if i.verifying: param.append('verifying')
        if i.cardverify: param.append('cardverify')
        if i.floating: param.append('floating')
        if i.otherin: param.append('otherin')
        if i.otherout: param.append('otherout')
        if i.reg: param.append('reg')
        if i.card2card: param.append('card2card')
        if i.delivery: param.append('delivery')
        if i.hold: param.append('hold')

        param_str = ','.join(param)
        if param_str != '':
            param_element = xml.SubElement(item_element, 'param')
            param_element.text = param_str

        city = ','.join([i.abc_code for i in i.city.all()])
        if city:
            city_element = xml.SubElement(item_element, 'city')
            city_element.text = city

    return HttpResponse(xml.tostring(root_element, method='xml', encoding='utf8'), content_type='text/xml')


def ExportRates(request):
    if get_pause(Settings.objects.first()):
        return JsonResponse({'error': 'pause'})

    swap = SwapMoney.objects.all()
    swap_to_export = {}
    for i in swap:
        left = i.money_left.xml_code
        right = i.money_right.xml_code

        if not swap_to_export.get(left):
            swap_to_export[left] = []
        '''
        Обмен можно отключить многими способами:
        1. Отключить сам обмен
        2. Отключить монету
        3. Отключить платёжку
        4. Отключить платёжку+монету
        5. При этом у крипты нету платёжки и на этой проверке возникает ошибка. Поэтому она обрабатывается в try  
        6. При этом даже если всё включено но нету резервов то обмен тоже нужно отключить  
        '''
        active = i.active and i.money_left.active and i.money_right.active and i.money_left.money.active and i.money_right.money.active

        if active:
            try:
                active = active and i.money_left.pay.active
            except AttributeError:
                pass
        if active:
            try:
                active = active and i.money_right.pay.active
            except AttributeError:
                pass

        # для подсчёта доступности обмена по резервам, надо минимальную сумму слева и справа привести к правой монете
        # и сравнить с имеющимися резервами

        if active:
            min_left = i.min_left
            min_right = i.min_right
            rate_left = i.rate_left_final
            rate_right = i.rate_right_final
            reserv = i.money_right.reserv
            if rate_left <= 0:
                active = False
            else:
                min_left_to_right = min_left * rate_right / rate_left
                if max(min_left_to_right, min_right) > reserv: active = False

        temp = {}
        temp['active'] = active
        temp['right'] = right
        temp['name_left'] = i.money_left.title
        temp['name_right'] = i.money_right.title
        temp['type_left'] = i.money_left.money.money_type
        temp['type_right'] = i.money_right.money.money_type
        temp['img_left'] = str(i.money_left.logo)
        temp['img_right'] = str(i.money_right.logo)
        temp['place'] = 1

        swap_to_export[left].append(temp)

    return JsonResponse(swap_to_export)


def ExportDirect(request):
    if get_pause(Settings.objects.first()):
        return JsonResponse({'error': 'pause'})

    cur_from = request.GET.get('cur_from')
    cur_to = request.GET.get('cur_to')
    city = request.GET.get('city')

    money = SwapMoney.objects.filter(money_left__xml_code=cur_from, money_right__xml_code=cur_to)

    if money.count() != 1:
        return JsonResponse({
            'error': 'exchanges count: ' + str(money.count()),
        })
    money = money[0]

    # добавили дополнительные поля
    temp = FieldsLeft.objects.filter(pay=money.money_left)
    left = []
    for i in temp:
        left.append(i.title)

    temp = FieldsRight.objects.filter(pay=money.money_right)
    right = []
    for i in temp:
        right.append(i.title)

    # считаем и передём минимальный минимум и максимальный максимум
    reserv = money.money_right.reserv

    min_left = money.min_left
    if money.rate_right_final > 0:
        min_left = money.min_right / money.rate_right_final * money.rate_left_final
        min_left = max(money.min_left, min_left)

    min_right = money.rate_left_final
    if money.rate_left_final > 0:
        min_right = money.min_left / money.rate_left_final * money.rate_right_final
        min_right = max(money.min_right, min_right)

    max_left = money.max_left
    if money.rate_right_final > 0:
        max_left = min(money.max_right, reserv) / money.rate_right_final * money.rate_left_final
        max_left = max(money.max_left, max_left) if 0 in [money.max_left, max_left] else min(money.max_left, max_left)

    max_right = money.max_right
    if money.rate_left_final > 0:
        max_right = money.max_left / money.rate_left_final * money.rate_right_final
        max_right = max(money.max_right, max_right) if 0 in [money.max_right, max_right] else min(money.max_right,
                                                                                                  max_right)

    if money.money_left.money.money_type == 'fiat':
        min_left = 0 if min_left == 0 else min_left.quantize(Decimal('0.01'))
        max_left = 0 if max_left == 0 else max_left.quantize(Decimal('0.01'))
    else:
        min_left = 0 if min_left == 0 else min_left.quantize(Decimal('0.00000001'))
        max_left = 0 if max_left == 0 else max_left.quantize(Decimal('0.00000001'))

    if money.money_right.money.money_type == 'fiat':
        min_right = 0 if min_right == 0 else min_right.quantize(Decimal('0.01'))
        max_right = 0 if max_right == 0 else max_right.quantize(Decimal('0.01'))
        reserv = 0 if reserv == 0 else reserv.quantize(Decimal('0.01'))
    else:
        min_right = 0 if min_right == 0 else min_right.quantize(Decimal('0.00000001'))
        max_right = 0 if max_right == 0 else max_right.quantize(Decimal('0.00000001'))
        reserv = 0 if reserv == 0 else reserv.quantize(Decimal('0.00000001'))

    def del_last_zero(num) -> str:  # Удаляем последние незначащие нули
        num = list(str(num))
        if '.' in num:
            while True:
                n = len(num) - 1
                if n <= 0:
                    break
                if num[n] == '0':
                    num.pop(n)
                else:
                    break
        return ''.join(num)

    direct = {
        'money_left': money.money_left.id,
        'money_right': money.money_right.id,
        'add_left': left,
        'add_right': right,
        'min_left': del_last_zero(min_left),
        'max_left': del_last_zero(max_left),
        'min_right': del_last_zero(min_right),
        'max_right': del_last_zero(max_right),
        'rate_left_final': money.rate_left_final,
        'rate_right_final': money.rate_right_final,
        'add_fee_left': 0 if money.add_fee_left == 0 else money.add_fee_left.quantize(Decimal('0.00000001')),
        'add_fee_right': 0 if money.add_fee_right == 0 else money.add_fee_right.quantize(Decimal('0.00000001')),
        'reserv': reserv,

        'seo_title': money.seo_title,
        'seo_descriptions': money.seo_descriptions,
        'seo_keywords': money.seo_keywords,
    }
    city = ','.join([i.abc_code for i in money.city.all()])
    if city:
        direct['city'] = city

    return JsonResponse(direct)
