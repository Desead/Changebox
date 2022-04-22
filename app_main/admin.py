from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import path

from app_main.forms import CustomUserCreationForm, CustomUserChangeForm
from app_main.lib.calculate_all_rates import set_all_rates
from app_main.lib.seo import set_seo_inner
from app_main.lib.set_change_rate import set_change_rate
from app_main.models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'referal', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'referal')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'referal',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.action(description='Включить выделенные')
def all_on(modeladmin, request, queryset):
    queryset.update(active=True)


@admin.action(description='Отключить выделенные')
def all_off(modeladmin, request, queryset):
    queryset.update(active=False)


@admin.register(InfoPanel)
class InfoPanelAdmin(admin.ModelAdmin):
    list_display = ('time', 'description', 'description_comment',)
    search_fields = ('description',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('abc_code', 'title')
    list_display_links = ('abc_code', 'title')
    search_fields = ('title',)


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id_best', 'title', 'ignore',)
    list_display_links = ('id_best', 'title',)
    list_editable = ('ignore',)
    list_filter = ('ignore',)
    search_fields = ('id_best', 'title',)
    actions = ['ignore_on', 'ignore_off']

    @admin.action(description='Игнорировать выделенные')
    def ignore_on(self, request, queryset):
        queryset.update(ignore=True)

    @admin.action(description='Отслеживать выделенные')
    def ignore_off(self, request, queryset):
        queryset.update(ignore=False)


@admin.register(Money)
class MoneyAdmin(admin.ModelAdmin):
    list_display = ('title', 'abc_code', 'money_type', 'active', 'nominal', 'cost_str', 'time')
    list_filter = ('active', 'money_type',)
    list_editable = ('active',)
    search_fields = ('title', 'abc_code',)
    readonly_fields = ('time',)
    save_on_top = True
    actions = [all_on, all_off]


class FieldsLeftInline(admin.TabularInline):
    model = FieldsLeft
    extra = 0
    verbose_name = 'Дополнительное поле'
    verbose_name_plural = 'Список дополнительных полей которые надо заполнить клиенту на сайте чтобы отдать данную валюту'


class FieldsRightInline(admin.TabularInline):
    model = FieldsRight
    extra = 0
    verbose_name = 'Дополнительное поле'
    verbose_name_plural = 'Список дополнительных полей которые надо заполнить клиенту на сайте чтобы получить данную валюту'


@admin.register(FullMoney)
class FullMoneyAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'reserv_str',)
    list_editable = ('active', 'reserv_str',)
    list_filter = ('active', 'pay',)
    search_fields = ('title', 'xml_code',)
    save_on_top = True
    actions = [all_on, all_off]
    inlines = [FieldsLeftInline, FieldsRightInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pay":
            kwargs["queryset"] = PaySystem.objects.filter(active=True)
        if db_field.name == "money":
            kwargs["queryset"] = Money.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pause', 'job_start', 'job_end',)
    list_editable = ('pause',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import/', self.my_view),
        ]
        return my_urls + urls

    def my_view(self, request):
        if request.POST.get('clear_all'):
            from django.apps import apps
            for k, v in apps.all_models['app_main'].items():
                v = str(v).split('.')
                try:
                    eval(v[len(v) - 1][:-2] + '.objects.all().delete()')
                except:
                    continue
        elif request.POST.get('city'):
            from app_main.lib.city import city_load
            city_load()
        elif request.POST.get('exchange'):
            from app_main.lib.exchange import exchange_load
            exchange_load()
        elif request.POST.get('pays'):
            from app_main.lib.paysystem import pays_load
            pays_load()
        elif request.POST.get('money'):
            from app_main.lib.money import money_load
            money_load()
        elif request.POST.get('fullmoney'):
            from app_main.lib.fullmoney import full_money_load
            full_money_load()
        elif request.POST.get('best'):
            from app_main.lib.bestchange import download_files_from_bestchange
            download_files_from_bestchange(True)

        return HttpResponseRedirect("../")


@admin.register(SwapMoney)
class SwapMoneyAdmin(admin.ModelAdmin):
    # fieldsets = (
    #     ('Основные настройки обмена',
    #      {'fields': (
    #          'active', ('money_left', 'money_right'), ('min_left_str', 'min_right_str',),
    #          ('max_left_str', 'max_right_str',), 'city', 'pause',)}),
    #     ('Настройка курсов обмена',
    #      {'fields': (('manual_rate_left', 'manual_rate_right', 'manual_active',),
    #                  'best_place', ('rate_left_str', 'rate_right_str',),
    #                  ('change_left', 'change_right',),
    #                  ('change_left_str', 'change_right_str',),
    #                  ('rate_left_final', 'rate_right_final',),)}),
    #     ('Дополнительные комиссии',
    #      {'fields': (('add_fee_left', 'add_fee_right',),)}),
    #     ('Метки для обмена', {'classes': ('collapse',), 'fields': (
    #         'manual', 'juridical', 'verifying', 'cardverify', 'floating', 'otherin', 'otherout', 'reg', 'card2card',
    #         'delivery', 'hold',)}),
    #     ('SEO для каждой текущей страницы. Имеют приоритет перед общими настройками SEO',
    #      {'classes': ('collapse',), 'fields': ('seo_title', 'seo_descriptions', 'seo_keywords')}),
    # )
    #
    # list_display = (
    #     'money_left', 'money_right', 'active', 'min_left_str', 'max_left_str', 'min_right_str', 'max_right_str',
    #     'best_place', 'rate_left_final', 'rate_right_final', 'time',)
    #
    # list_display_links = ('money_left', 'money_right', 'rate_left_final', 'rate_right_final',)
    # list_editable = ('active', 'best_place', 'min_left_str', 'max_left_str', 'min_right_str', 'max_right_str',)
    # list_filter = ('active', 'best_place', 'money_left', 'money_right',)
    # readonly_fields = ('time',)
    save_on_top = True
    actions = [all_on, all_off]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "money_left":
            kwargs["queryset"] = FullMoney.objects.filter(active=True)
        if db_field.name == "money_right":
            kwargs["queryset"] = FullMoney.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import/', self.my_view),
        ]
        return my_urls + urls

    def my_view(self, request):
        if request.POST.get('cbrbest'):
            set_all_rates()
        if request.POST.get('rnd_swap'):
            fm = FullMoney.objects.all()
            if fm.count() <= 0: return
            import random
            for i in range(20):
                swap = SwapMoney()
                swap.money_left = random.choice(fm)
                swap.money_right = random.choice(fm)
                swap.min_left = random.randint(0, 100)
                swap.max_left = random.randint(swap.min_left, 100)
                swap.min_right = random.randint(0, 10000)
                swap.max_right = random.randint(swap.min_right, 10000)
                swap.best_place = 1
                try:
                    swap.save()
                except:
                    continue

        if request.POST.get('rates'):
            pass

        return HttpResponseRedirect("../")


@admin.register(PaySystem)
class PaySystemAdmin(admin.ModelAdmin):
    list_display = ('title', 'active',)
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('title',)
    actions = [all_on, all_off]


@admin.register(SwapOrders)
class SwapOrdersAdmin(admin.ModelAdmin):
    actions = [all_on, all_off]


admin.site.unregister(Group)

admin.site.site_header = 'Панель управления'  # default: "Django Administration"
admin.site.index_title = 'Обменник'  # default: "Site administration"
admin.site.site_title = 'Управление'  # default: "Django site admin"
