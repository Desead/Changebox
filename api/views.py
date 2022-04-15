from rest_framework import generics

from api.serializers import *
from app_main.models import *


class MoneyAPIView(generics.ListAPIView):
    queryset = Money.objects.all()
    serializer_class = MoneySerializer

class CityAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class SettingsAPIView(generics.ListAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer

class ExchangeAPIView(generics.ListAPIView):
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer

class PaySystemAPIView(generics.ListAPIView):
    queryset = PaySystem.objects.all()
    serializer_class = PaySystemSerializer

class FullMoneyAPIView(generics.ListAPIView):
    queryset = FullMoney.objects.all()
    serializer_class = FullMoneySerializer

class SwapMoneyAPIView(generics.ListAPIView):
    queryset = SwapMoney.objects.all()
    serializer_class = SwapMoneySerializer