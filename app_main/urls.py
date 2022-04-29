from django.urls import path, include

from app_main.views import *

export_url = 'api/v1/xml_export/'
try:
    from app_main.models import Settings

    export_url = Settings.objects.first().xml_address
    export_url = 'api/v1/' + str(export_url).strip('/') + '/'
except:
    pass

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name="signup"),
    path('accounts/lk/', LKView.as_view(), name='view_lk'),

    path('api/v1/rates/', ExportRates, name='view_rates'),
    path('api/v1/direct/', ExportDirect, name='view_direct'),
    path(export_url, ExportXML, name='view_xml'),

    path('rules/', RulesView.as_view(), name='view_rules'),
    path('security/', SecurityView.as_view(), name='view_security'),
    path('faq/', FAQView.as_view(), name='view_faq'),
    path('feedback/', FeedbackView.as_view(), name='view_feedback'),
    path('confirm/', ConfirmView.as_view(), name='view_confirm'),
    path('', StartView.as_view(), name='home'),
]

''' 
accounts/login/ [name='login']
accounts/logout/ [name='logout']
accounts/password_change/ [name='password_change']
accounts/password_change/done/ [name='password_change_done']
accounts/password_reset/ [name='password_reset']
accounts/password_reset/done/ [name='password_reset_done']
accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/reset/done/ [name='password_reset_complete']
'''
