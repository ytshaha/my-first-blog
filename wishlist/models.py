from django.db import models
from django.conf import settings
from products.models import ProductItem
User = settings.AUTH_USER_MODEL

# Create your models here.
class Wish(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item    = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}_{}".format(self.user, self.product_item.product.title)