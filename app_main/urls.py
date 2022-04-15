from django.urls import path

from app_main.models import Settings
from app_main.views import StartView, ExportRates, ExportApi

export_url = 'xml_export/'

try:
    export_url = Settings.objects.first().xml_address
    export_url = str(export_url).strip('/') + '/'
except AttributeError as error:
    pass

urlpatterns = [
    path(export_url, ExportRates, name='view_export'),
    path('api/v1/rates/', ExportApi, name='view_api'),
    path('', StartView.as_view(), name='view_index'),
]
