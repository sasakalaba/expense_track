from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from .views import (
    AccountViewSet,
    ExpenseViewSet,
    UserViewSet,
    not_found_404
)


"""
Account views.
"""
account_register = AccountViewSet.as_view({
    'post': 'create'
})


"""
Expense views.
"""
expense_list = ExpenseViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

expense_detail = ExpenseViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})


"""
Report views.
"""
report_detail = ExpenseViewSet.as_view({
    'get': 'report'
})


"""
User views.
"""
user_list = UserViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_me = UserViewSet.as_view({
    'get': 'me'
})


urlpatterns = format_suffix_patterns([
    url(r'^users/$', user_list, name='user_list'),
    url(r'^users/me$', user_me, name='user_me'),
    url(r'^users/(?P<username>[A-Za-z0-9-]+)/$', user_detail, name='user_detail'),
    url(r'^users/(?P<username>[A-Za-z0-9-]+)/expenses/$', expense_list, name='expense_list'),
    url(r'^users/(?P<username>[A-Za-z0-9-]+)/expenses/report/(?P<week>\d+)$', report_detail, name='report_detail'),
    url(r'^users/(?P<username>[A-Za-z0-9-]+)/expenses/(?P<pk>\d+)$', expense_detail, name='expense_detail'),
    url(r'^.*$', not_found_404, name='not_found_404')
])
