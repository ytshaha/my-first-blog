
import random
import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from .utils import unique_slug_generator
from django.db.models.signals import pre_save, post_save
from django.db.models import Q

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(filepath)
    return name, ext

def upload_image_path(instance, filename):
    print(instance)
    print(filename)
    new_filename = random.randint(1, 39111111)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)

class ProductQuerySet(models.query.QuerySet):
    def featured(self):
        return self.filter(featured=True)
    
    def active(self):
        return self.filter(active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) | 
                  Q(description__icontains=query) |
                  Q(brand__name__icontains=query) |
                  Q(category__name__icontains=query) |
                  Q(tag__title__icontains=query)
                  )
                  
        return self.filter(lookups).distinct() # distinct 안하면 저위의 lookup들이 중복으로 검색되는 것들을 다 표시하게된다. 그냥 누적하되 중복은안되야하는게 맞을때 하므.

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self, option):
        return self.get_queryset().filter(category=option)

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None
    
    def search(self, query):
        return self.get_queryset().active().search(query)

class Product(models.Model):
    number = models.CharField(max_length=10, blank=True, null=True, help_text=u'상품관리용코드') # product 네임이 아닌 number로 데이터 베이스관리를 위함.
    title = models.CharField(max_length=200, help_text=u'상품명')
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, help_text=u'브랜드명')
    start_price = models.PositiveIntegerField(default=0, help_text=u'경매시작가격')
    limit_price = models.PositiveIntegerField(default=0, help_text=u'경매한도가격')
    description = models.TextField(blank=True, null=True, help_text=u'정보') 
    amount = models.IntegerField(default=0, help_text=u'수량')
    created_date = models.DateTimeField(default=timezone.now, help_text=u'물품생성일')
    bidding = models.BooleanField(default=False, help_text=u'경매여부')
    bidding_date = models.DateTimeField(default=timezone.now, help_text=u'경매시작일')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, help_text=u'카테고리')
    image = models.FileField(upload_to=upload_image_path, null=True, blank=True)
    # image, 이것은 썸네일이든 그냥 이미지든 다른 Model에서 ForeignKey로 참조할 것.(조영일 슬라이드 참고)
    # category, 나중에 추가, 2-depth 이상일경우 Django-mptt라이브러리사용(조영일 슬라이드 참고)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, unique=True, allow_unicode=True)
    
    objects = ProductManager()

    def get_absolute_url(self):
        # return "products/{slug}".format(slug=self.slug)
        return "detail/{slug}/".format(slug=self.slug)

    def __str__(self):
        return self.title

def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)


class Brand(models.Model):
    name = models.CharField(max_length=200, help_text=u'브랜드명')
    website = models.CharField(blank=True, null=True, max_length=200, help_text=u'홈페이지')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, help_text=u'카테고리명')

    def __str__(self):
        return self.name