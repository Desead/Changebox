import xml.etree.ElementTree as xml

from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from app_main.models import SwapMoney, FieldsLeft, FieldsRight, Settings


class StartView(View):
    def get(self, req):
        temp = Settings.objects.first()
        context = {
            'settings': temp
        }
        return render(req, 'index.html', context)


def ExportXML(request):
    rates = SwapMoney.objects.filter(active=True, money_left__money__active=True, money_left__active=True,
                                     money_right__active=True, money_right__money__active=True)
    # добавить ограничения по монетам и резервам
    root_element = xml.Element('rates')

    for i in rates:
        # Минимумы и максимум для обмена надо высчитывать для левой монеты, поэтому правый мин и макс переводим в левую валюту
        # начальный курс обмена должен уже учитывать номинал, поэтому здесь в расчётах он не участвует

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

        if i.city != None:
            city_element = xml.SubElement(item_element, 'city')
            city_element.text = i.city.abc_code

    return HttpResponse(xml.tostring(root_element, method='xml', encoding='utf8'), content_type='text/xml')


def ExportRates(request):
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
            min_left_to_right = min_left * rate_right / rate_left

            if max(min_left_to_right, min_right) > reserv: active = False

        temp = {}
        temp['active'] = active
        temp['right'] = right
        temp['name_left'] = i.money_left.title
        temp['name_right'] = i.money_right.title
        temp['type_left'] = i.money_left.money.money_type
        temp['type_right'] = i.money_right.money.money_type
        temp['img_left'] = ''
        temp['img_right'] = ''
        temp['place'] = 1

        swap_to_export[left].append(temp)

    return JsonResponse(swap_to_export)


def ExportDirect(request):
    '''
    def ExportDirect(request):
        cur_from = request.GET.get('cur_from')
        cur_to = request.GET.get('cur_to')

        money = SwapMoney.objects.filter(money_left__xml_code=cur_from, money_right__xml_code=cur_to)

        if money.count() != 1:
            return JsonResponse({
                'error': 'exchanges count: ' + str(money.count()),
            })

        return HttpResponse(serialize('jsonl', money))
    '''
    # пример
    # http://127.0.0.1:8000/api/v1/direct/?cur_from=BTC&cur_to=QWRUB

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
        max_left = min(money.max_left, max_left)

    max_right = money.max_right
    if money.rate_left_final > 0:
        max_right = money.max_left / money.rate_left_final * money.rate_right_final
        max_right = min(money.max_right, max_right)

    if money.money_left.money.money_type == 'fiat':
        min_left = round(min_left, 2)
        max_left = round(max_left, 2)
    else:
        min_left = round(min_left, 8)
        max_left = round(max_left, 8)

    if money.money_right.money.money_type == 'fiat':
        min_right = round(min_right, 2)
        max_right = round(max_right, 2)
        reserv = round(reserv, 2)
    else:
        min_right = round(min_right, 8)
        max_right = round(max_right, 8)
        reserv = round(reserv, 8)

    direct = {
        'money_left': money.money_left.id,
        'money_right': money.money_right.id,
        'add_left': left,
        'add_right': right,
        'min_left': min_left,
        'max_left': max_left,
        'min_right': min_right,
        'max_right': max_right,
        'rate_left_final': money.rate_left_final,
        'rate_right_final': money.rate_right_final,
        'add_fee_left': money.add_fee_left,
        'add_fee_right': money.add_fee_right,
        'reserv': reserv,

        'city': money.city,
        'seo_title': money.seo_title,
        'seo_descriptions': money.seo_descriptions,
        'seo_keywords': money.seo_keywords,
    }
    return JsonResponse(direct)


class RulesView(View):
    def get(self, request):
        context = {'rules': Settings.objects.first()}
        return render(request, 'rules.html', context)


class ConfirmView(View):
    def post(self, request):
        context = {}
        return render(request, 'confirm.html', context)
