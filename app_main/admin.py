from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import path

from app_main.forms import CustomUserCreationForm, CustomUserChangeForm
from app_main.lib.set_all_rates import set_all_rates
from app_main.lib.start.create_all_swap import create_all_swap
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
    list_display = ('title', 'abc_code', 'money_type', 'active', 'nominal', 'cost', 'time')
    list_filter = ('active', 'money_type',)
    list_editable = ('active',)
    search_fields = ('title', 'abc_code',)
    readonly_fields = ('time',)
    save_on_top = True
    actions = [all_on, all_off]


@admin.register(FullMoney)
class FullMoneyAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'reserv', 'add_field_in', 'add_field_out', 'add_field_memo',)
    list_editable = ('active', 'reserv', 'add_field_in', 'add_field_out', 'add_field_memo',)
    list_filter = ('active', 'pay',)
    search_fields = ('title', 'xml_code',)
    save_on_top = True
    actions = [all_on, all_off]
    fieldsets = (
        ('', {'fields': ('active', 'title', 'xml_code', 'pay', 'money', 'reserv', 'logo',)}),
        ('Дополнительные поля', {'fields': ('add_field_in', 'add_field_out', 'add_field_memo',)}),
        ('Комиссии',
         {'fields': ('payer', ('fee_percent', 'fee_absolut'), ('fee_min', 'fee_max'),)}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pay":
            kwargs["queryset"] = PaySystem.objects.filter(active=True)
        if db_field.name == "money":
            kwargs["queryset"] = Money.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MonitoringInline(admin.TabularInline):
    model = Monitoring
    extra = 0
    verbose_name = 'Мониторинг'
    verbose_name_plural = 'Мониторинги'


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pause', 'job_start', 'job_end',)
    list_editable = ('pause',)
    inlines = [MonitoringInline]
    save_on_top = True

    fieldsets = (
        ('', {'fields': ('logo', 'exchane_name', 'timedelta_fiat', 'timedelta_crypto', 'news',)}),
        ('Режим работы',
         {'classes': ('collapse',), 'fields': ('pause', ('job_start', 'job_end'),)}),
        ('URL', {'classes': ('collapse',), 'fields': ('adminka', 'xml_address',)}),
        ('SEO', {'classes': ('collapse',), 'fields': ('title', 'description', 'keywords',)}),
        ('Правила', {'classes': ('collapse',), 'fields': ('rules_exchange', 'rules_security', 'rules_warning',)}),
    )

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
            set_binance_rate(Money.objects.filter(money_type='crypto'), binance[1], Settings.objects.first().off_money)
        elif request.POST.get('create_swap'):
            create_all_swap()
        elif request.POST.get('set_all_rates'):
            set_all_rates()
        return HttpResponseRedirect("../")


@admin.register(SwapMoney)
class SwapMoneyAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основные настройки обмена',
         {'fields': (
             'active', 'freeze', ('money_left', 'money_right'), ('min_left', 'min_right',),
             ('max_left', 'max_right',),)}),
        ('Настройка курсов обмена',
         {'fields': ('best_place', ('manual_rate_left', 'manual_rate_right', 'manual_active',),
                     ('rate_left', 'rate_right',),
                     ('change_left', 'change_right',),
                     ('rate_left_final', 'rate_right_final',),)}),
        ('Дополнительные комиссии',
         {'fields': (('add_fee_left', 'add_fee_right',),)}),

        ('Города', {'classes': ('collapse',), 'fields': ('city',)}),

        ('Метки для обмена', {'classes': ('collapse',), 'fields': (
            'manual', 'juridical', 'verifying', 'cardverify', 'floating', 'otherin', 'otherout', 'reg', 'card2card',
            'delivery', 'hold',)}),
        ('SEO для каждой текущей страницы. Имеют приоритет перед общими настройками SEO',
         {'classes': ('collapse',), 'fields': ('seo_title', 'seo_descriptions', 'seo_keywords')}),
    )

    list_display = (
        'money_left', 'money_right', 'active', 'min_left', 'max_left', 'min_right', 'max_right',
        'best_place', 'rate_left_final', 'rate_right_final', 'time',)

    list_display_links = ('money_left', 'money_right', 'rate_left_final', 'rate_right_final',)
    list_editable = ('active', 'best_place', 'min_left', 'max_left', 'min_right', 'max_right',)
    list_filter = ('active', 'best_place', 'money_left', 'money_right',)
    readonly_fields = ('time',)
    save_on_top = True
    actions = [all_on, all_off]
    filter_horizontal = ('city',)

    def save_model(self, request, obj, form, change):
        # obj.change_left = Decimal(remove_space_froming(obj.change_left))
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "money_left":
            kwargs["queryset"] = FullMoney.objects.filter(active=True)
        if db_field.name == "money_right":
            kwargs["queryset"] = FullMoney.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PaySystem)
class PaySystemAdmin(admin.ModelAdmin):
    list_display = ('title', 'active',)
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('title',)
    fields = ('active', 'payer', 'title', 'fee_percent', 'fee_absolut', 'fee_min', 'fee_max',)
    actions = [all_on, all_off]


@admin.register(SwapOrders)
class SwapOrdersAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('num', 'status', 'money_left', 'money_right', 'left_in', 'right_out', 'pl', 'user', 'swap_create',)
    list_editable = ('status',)
    list_filter = ('status', 'user', 'money_left', 'money_right',)
    list_display_links = ('num', 'money_left', 'money_right',)
    search_fields = ('num',)
    readonly_fields = ('num', 'money_left', 'money_right', 'left_in', 'right_out', 'pl', 'swap_create')
    fieldsets = (
        ('Основные параметры сделки',
         {'fields':
             (
                 'status', 'num', 'swap_create', 'money_left', 'money_right', 'left_in', 'right_out', 'pl', 'wallet_in',
                 'wallet_client', 'wallet_out', 'memo_out', 'user', 'phone', 'email', 'comment',
             ),
         }),
    )


@admin.register(Wallets)
class WalletsAdmin(admin.ModelAdmin):
    list_display = ('fullmoney', 'active', 'number','tag', 'balance', 'max_balance',)
    list_editable = ('active', 'number', 'balance', 'max_balance',)

    actions = [all_on, all_off]


admin.site.unregister(Group)

admin.site.site_header = 'Панель управления'  # default: "Django Administration"
admin.site.index_title = 'Обменник'  # default: "Site administration"
admin.site.site_title = 'Управление'  # default: "Django site admin"
