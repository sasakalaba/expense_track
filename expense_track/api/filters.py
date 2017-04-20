import django_filters
from expense_trackapp.models import Expense


class ExpenseFilter(django_filters.rest_framework.FilterSet):
    date = django_filters.DateFromToRangeFilter()
    time = django_filters.TimeRangeFilter()
    amount = django_filters.RangeFilter()

    class Meta:
        model = Expense
        fields = ['date', 'time', 'amount']
