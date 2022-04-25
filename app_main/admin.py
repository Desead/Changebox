from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import path

from app_main.forms import CustomUserCreationForm, CustomUserChangeForm
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
    list_display = ('abc_code', 'title',)
    list_display_links = ('abc_code', 'title',)
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
        if request.POST.get('city'):
            from app_main.lib.start.city_load import city_load
            city_load()
        elif request.POST.get('exchange'):
            from app_main.lib.start.exchange_load import exchange_load
            exchange_load()
        elif request.POST.get('pays'):
            from app_main.lib.start.pays_load import pays_load
            pays_load()
        elif request.POST.get('money'):
            from app_main.lib.start.money_load import money_load
            money_load()
        elif request.POST.get('best_load'):
            from app_main.lib.bestchange import download_files_from_bestchange
            download_files_from_bestchange(True)
        elif request.POST.get('best_read'):
            from app_main.lib.bestchange import get_rates_from_bestchange
            get_rates_from_bestchange(SwapMoney.objects.all(), {}, {}, True)
        elif request.POST.get('cbr_rates'):
            from app_main.lib.cbr import get_cbr_data
            from app_main.lib.cbr import convert_cbr_data_to_dict
            from app_main.lib.cbr import set_cbr_rates
            cbr = get_cbr_data()
            cbr = convert_cbr_data_to_dict(cbr[1])
            set_cbr_rates(Money.objects.filter(money_type='fiat'), cbr)
        elif request.POST.get('binance_rates'):
            from app_main.lib.binance import get_binance_data
            from app_main.lib.binance import set_binance_rate
            binance = get_binance_data()
            set_binance_rate(Money.objects.filter(money_type='crypto'), binance[1])
        return HttpResponseRedirect("../")


@admin.register(SwapMoney)
class SwapMoneyAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основные настройки обмена',
         {'fields': (
             'active', 'freeze',('money_left', 'money_right'), ('min_left_str', 'min_right_str',),
             ('max_left_str', 'max_right_str',), )}),
        ('Настройка курсов обмена',
         {'fields': ('best_place', ('manual_rate_left_str', 'manual_rate_right_str', 'manual_active',),
                     ('rate_left_str', 'rate_right_str',),
                     ('change_left_str', 'change_right_str',),
                     ('rate_left_final_str', 'rate_right_final_str',),)}),
        ('Дополнительные комиссии',
         {'fields': (('add_fee_left_str', 'add_fee_right_str',),)}),

        ('Города', {'classes': ('collapse',), 'fields': ('city',)}),

        ('Метки для обмена', {'classes': ('collapse',), 'fields': (
            'manual', 'juridical', 'verifying', 'cardverify', 'floating', 'otherin', 'otherout', 'reg', 'card2card',
            'delivery', 'hold',)}),
        ('SEO для каждой текущей страницы. Имеют приоритет перед общими настройками SEO',
         {'classes': ('collapse',), 'fields': ('seo_title', 'seo_descriptions', 'seo_keywords')}),
    )

    list_display = (
        'money_left', 'money_right', 'active', 'min_left_str', 'max_left_str', 'min_right_str', 'max_right_str',
        'best_place', 'rate_left_final_str', 'rate_right_final_str', 'time',)

    list_display_links = ('money_left', 'money_right', 'rate_left_final_str', 'rate_right_final_str',)
    list_editable = ('active', 'best_place', 'min_left_str', 'max_left_str', 'min_right_str', 'max_right_str',)
    list_filter = ('active', 'best_place', 'money_left', 'money_right',)
    readonly_fields = ('time',)
    save_on_top = True
    actions = [all_on, all_off]
    filter_horizontal = ('city',)

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "city":
    #         kwargs["queryset"] = City.objects.filter(active=True)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

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
