from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login
from rest_framework.authtoken.views import obtain_auth_token
from api.urls import account_register


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'login', login, {'template_name': 'login.html'},
        name='login'),
    url(r'^logout', logout_then_login, name='logout_then_login'),
    url(r'', include('expense_trackapp.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^api-auth$', obtain_auth_token, name='account_login'),
    url(r'^api-register$', account_register, name='account_register'),
]
