from django.contrib import admin
from .models import Expense


class ExpenseAdmin(admin.ModelAdmin):
    model = Expense
    list_display = ('date', 'amount')

admin.site.register(Expense, ExpenseAdmin)
