from datetime import timezone, datetime, timedelta
from pytz import timezone



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
        settings_time_zone = timezone(settings.TIME_ZONE)
        timestamp_localize = self.timestamp.astimezone(settings_time_zone)
        formatted_timestamp = timestamp_localize.strftime(datetime_format)
        return "{}_{}_{}".format(self.user, str(self.amount), formatted_timestamp)


        