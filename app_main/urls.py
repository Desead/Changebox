from django.urls import path

from app_main.views import *

export_url = 'xml_export/'

try:
    from app_main.models import Settings

    export_url = Settings.objects.first().xml_address
    export_url = str(export_url).strip('/') + '/'
except:
    pass

urlpatterns = [
    path('api/v1/rates/', ExportRates, name='view_rates'),
    path('api/v1/direct/', ExportDirect, name='view_direct'),
    path(export_url, ExportXML, name='view_xml'),
    path('rules/', RulesView.as_view(), name='view_rules'),
    path('', StartView.as_view(), name='view_index'),
]
