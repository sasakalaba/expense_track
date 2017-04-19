from django.db import models
from django.utils import timezone
from django.conf import settings


def get_current_time():
    return timezone.localtime(timezone.now())


class Expense(models.Model):
    class Meta:
        ordering = ['date', 'amount']

    def __unicode__(self):
        return ' '.join([str(self.date), str(self.amount)])

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField(default=get_current_time)
    time = models.TimeField(default=get_current_time)
    description = models.CharField(max_length=1024, null=True, blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.CharField(max_length=1024, null=True, blank=True, default='')
