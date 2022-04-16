"""Changebox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from Changebox.settings import DEBUG
from app_main.models import Settings

# если бд ещё нету или в ней не заполнена таблица Settings то вываливается ошибка т.к. нет нужных полей
admin_path = 'admin/'
if not DEBUG:
    try:
        admin_path = str(Settings.objects.first().adminka).strip('/') + '/'
    except AttributeError as error:
        pass

urlpatterns = [
    path(admin_path, admin.site.urls),
    # path('api/v1/', include('api.urls')),
    path('', include('app_main.urls')),
]
