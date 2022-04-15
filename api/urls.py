from django.urls import path

from api.views import *

urlpatterns = [
    path('money/', MoneyAPIView.as_view()),
    path('city/', CityAPIView.as_view()),
    path('settings/', SettingsAPIView.as_view()),
    path('exchange/', ExchangeAPIView.as_view()),
    path('pay/', PaySystemAPIView.as_view()),
    path('fullmoney/', FullMoneyAPIView.as_view()),
    path('swap/', SwapMoneyAPIView.as_view()),
]
