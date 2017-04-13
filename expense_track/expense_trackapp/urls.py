from django.conf.urls import url
from expense_trackapp import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
]
