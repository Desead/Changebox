from rest_framework import serializers

from app_main.models import *


class MoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Money
        fields = ('active', 'title', 'abc_code', 'money_type', 'nominal', 'cost', 'time',)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('title', 'abc_code', 'id_best')


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ('job_start', 'job_end', 'pause', 'reload_exchange')


class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exchange
        fields = ('title', 'id_best', 'ignore',)


class PaySystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaySystem
        fields = ('title', 'active',)


class FullMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = FullMoney
        fields = ('active', 'title', 'xml_code', 'pay', 'money', 'reserv',)


class SwapMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = SwapMoney
        fields = ('active', 'money_left', 'money_right', 'min_left', 'max_left', 'min_right', 'max_right',)
