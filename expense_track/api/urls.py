from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from .views import (
    AccountViewSet,
    # ExpenseViewSet,
    # UserViewSet,
    # ReportViewSet,
    not_found_404
)


"""
Account views.
"""
# account_login = AccountViewSet.as_view({
#     'post': 'login'
# })

account_register = AccountViewSet.as_view({
    'post': 'create'
})


"""
Expense views.
"""
# expense_list = ExpenseViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
#     # 'delete': 'destroy'
# })
#
# expense_detail = ExpenseViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'delete': 'destroy'
# })


"""
User views.
"""
# user_list = UserViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
#     # 'delete': 'destroy'
# })
#
# user_detail = UserViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'delete': 'destroy'
# })


"""
Report views.
"""
# report_detail = ReportViewSet.as_view({
#     'get': 'retrieve'
# })


urlpatterns = format_suffix_patterns([
    url(r'^.*$', not_found_404, name='not_found_404'),
])
