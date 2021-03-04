from django.conf import settings
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from carts.models import CartItem
User = settings.AUTH_USER_MODEL

PRODUCT_TYPE = (
    ('normal','상시상품구매'),
    ('bidding','경매상품구매'),
    ('ticket','경매티켓구매'),
    
)

RATING_CHOICES = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)

class Review(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item    = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    title           = models.CharField(max_length=200)
    text            = models.TextField(blank=True, null=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    rating          = models.IntegerField(default=5, choices=RATING_CHOICES)

    # def publish(self):
    #     self.published_date = timezone.now()
    #     self.save()

    # def approved_comments(self):
        # return self.comments.filter(approved_comment=True)

    def __str__(self):
        return self.title


def get_image_filename(instance, filename):
    title = instance.post.title
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename)  


class ReviewImages(models.Model):
    post = models.ForeignKey(Review, on_delete=models.CASCADE ,default=None)
    image = models.ImageField(upload_to=get_image_filename,
                              verbose_name='Image')


class Comment(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    review              = models.ForeignKey(Review, blank=True, null=True, on_delete=models.CASCADE)
    text                = models.TextField()
    created_date        = models.DateTimeField(auto_now_add=True)
    approved_comment    = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text
