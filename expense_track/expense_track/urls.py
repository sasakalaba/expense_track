from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'login/', login, {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/', logout_then_login, name='logout_then_login'),
    url(r'', include('expense_trackapp.urls')),
]
