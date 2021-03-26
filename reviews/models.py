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
    (0, '☆☆☆☆☆'),
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
)

def get_image_filename(instance, filename):
    title = "{}_{}".format(instance.user.username, instance.created_date)
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename)  



class Review(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_item    = models.ForeignKey(CartItem, on_delete=models.CASCADE, verbose_name= '구매물품')
    title           = models.CharField(max_length=200, verbose_name= '제목')
    text            = models.TextField(max_length=200, blank=True, null=True, verbose_name= '내용')
    rating          = models.IntegerField(default=5, choices=RATING_CHOICES, verbose_name= '평점')
    created_date    = models.DateTimeField(auto_now_add=True)

    image1          = models.ImageField(upload_to=get_image_filename, verbose_name='Image', blank=True, null=True)
    image2          = models.ImageField(upload_to=get_image_filename, verbose_name='Image', blank=True, null=True)
    image3          = models.ImageField(upload_to=get_image_filename, verbose_name='Image', blank=True, null=True)
    image4          = models.ImageField(upload_to=get_image_filename, verbose_name='Image', blank=True, null=True)
    image5          = models.ImageField(upload_to=get_image_filename, verbose_name='Image', blank=True, null=True)
    
    # def publish(self):
    #     self.published_date = timezone.now()
    #     self.save()

    # def approved_comments(self):
        # return self.comments.filter(approved_comment=True)

    def __str__(self):
        return self.title





class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE ,default=None)
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
