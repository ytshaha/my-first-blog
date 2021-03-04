from datetime import datetime


from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PointManager(models.Manager):
    def new(self, user, amount, details=None):
        return self.model.objects.create(user=user, amount=amount, details=details)



class Point(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    amount          = models.IntegerField(default=0)
    details         = models.CharField(max_length=200, blank=True, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = PointManager()

    def __str__(self):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        formatted_timestamp = self.timestamp.strftime(datetime_format)
        return "{}_{}_{}".format(self.user, str(self.amount), formatted_timestamp)