
import random
import os
from decimal import Decimal
import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify

from mysite.utils import unique_slug_generator, unique_product_item_slug_generator
from django.db.models.signals import pre_save, post_save
from django.db.models import Q

DELIVERY_FROM_CHOICE = (
    ('domestic','국내배송'),
    ('overseas','해외배송'),
)

BIDDING_STATUS_CHOICE = (
    ('bidding_ready','경매대기'),
    ('bidding','경매중'),
    ('bidding_end','경매종료'),
)

PRODUCT_TYPE = (
    ('normal','일반물품'),
    ('bidding','경매물품'),
)

PRICE_STEP_CHOICE = (
    (1000,'1,000 원'),
    (5000,'5,000 원'),
    (10000,'10,000 원'),
    
)


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(filepath)
    return name, ext

def upload_main_image_path(instance, filename):
    # new_filename = random.randint(1, 39111111)
    # name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    title = instance.title
    slug = slugify(title)
    return "products/{product_title}/{slug}-{filename}".format(product_title=title, slug=slug, filename=filename)  

def upload_image_path(instance, filename):
    # new_filename = random.randint(1, 39111111)
    # name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    title = instance.product.title
    slug = slugify(title)
    return "products/{product_title}/{slug}-{filename}".format(product_title=title, slug=slug, filename=filename)  

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

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["hours"] = "{:02d}".format(d["hours"])
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["seconds"] = "{:02d}".format(d["seconds"])
    
    return fmt.format(**d)

class Product(models.Model):
    number                  = models.CharField(max_length=40, blank=True, null=True, unique=True, help_text=u'상품관리용코드') # product 네임이 아닌 number로 데이터 베이스관리를 위함.
    title                   = models.CharField(max_length=200, help_text=u'상품명')
    brand                   = models.ForeignKey('Brand', on_delete=models.CASCADE, help_text=u'브랜드명')
    category                = models.ForeignKey('Category', on_delete=models.CASCADE, help_text=u'카테고리')
    
    list_price              = models.PositiveIntegerField(default=0, help_text=u'정가')
    
    info_made_country       = models.CharField(default=0, max_length=30, help_text=u'원산지')
    info_product_number     = models.CharField(default=0, max_length=30, help_text=u'모델명')
    info_delivery           = models.CharField(default='택배', max_length=30, help_text=u'배송방법')
    info_product_kind       = models.CharField(blank=True, null=True, max_length=100, help_text=u'종류_가방에 해당')
    info_material           = models.CharField(max_length=100, blank=True, null=True, help_text=u'제품소재_의류_섬유의 조성 또는 혼용률을 백분율로 표시, 기능성인 경우 성적서 또는 허가서, 운동화_경우에는 겉감, 안감을 구분하여 표시')
    info_feature            = models.CharField(max_length=100,  blank=True, null=True, help_text=u'크기/치수/색상_구두/신발의경우_발길이 해외사이즈 표기시 국내사이즈 병행표기(mm), 굽높이:굽재료를 사용하는 여성화에 한함(cm)')
    info_product_person     = models.CharField(max_length=100,  blank=True, null=True, help_text=u'제조자_수입품인 경우 수입자를 함께 표기(변행수입의 경우 병행수입 여부로 대체 가능)')
    info_alert              = models.CharField(max_length=100, blank=True, null=True, help_text=u'취급시 주의사항_의류는 세탁방법 및 취급시 주의사항')
    info_quality_standard   = models.CharField(max_length=100, blank=True, null=True, help_text=u'품질보증기준')
    info_as                 = models.CharField(max_length=100, blank=True, null=True, help_text=u'A/S 책임자와 전화번호')
    
    
    
    description             = models.TextField(blank=True, null=True, help_text=u'정보')
    created_date            = models.DateTimeField(default=timezone.now, help_text=u'물품생성일')
    
    image                   = models.FileField(upload_to=upload_main_image_path, null=True, blank=True)
    video_link              = models.CharField(max_length=250, blank=True, null=True)
    
    featured                = models.BooleanField(default=False)
    active                  = models.BooleanField(default=True)
    slug                    = models.SlugField(blank=True, unique=True, allow_unicode=True)
    
    objects = ProductManager()

    def get_absolute_url(self):
        # return "products/{slug}".format(slug=self.slug)
        # return "detail/{slug}/".format(slug=self.slug)
        return reverse("products:product_detail_slug", kwargs={"slug":self.slug})

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

def product_pre_save_receiver(sender, instance, *args, **kwargs):
    # 슬러그 설정
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    # # 할인율
    # instance.sale_ratio = Decimal(instance.list_price - instance.current_price) / instance.list_price * 100
    # # 남은 비딩타임.
    # now = timezone.now()
    # time_remain = instance.bidding_end_date - now
    # # print(time_remain, type(time_remain))
    # # instance.remain_bidding_time = "{}시간{}분".format(time_remain.hour, time_remain.minute)
    # instance.remain_bidding_time = strfdelta(time_remain, "{hours}:{minutes}:{seconds}")
    # # instance.remain_bidding_time = strfdelta(time_remain, "{days} days {hours}:{minutes}:{seconds}")
    # # instance.remain_bidding_time = time_remain

    # bidding_on = None
    # if now < instance.bidding_start_date:
    #     bidding_on = 'bidding_ready' # 경매 준비중
    # elif now >= instance.bidding_start_date and now < instance.bidding_end_date and instance.current_price < instance.limit_price:
    #     bidding_on = 'bidding'
    # elif now > instance.bidding_end_date or instance.current_price == instance.limit_price:
    #     bidding_on = 'bidding_end'
    # else:
    #     bidding_on = None
    # instance.bidding_on = bidding_on

pre_save.connect(product_pre_save_receiver, sender=Product)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE ,default=None)
    image   = models.ImageField(upload_to=upload_image_path, null=True, blank=True, verbose_name='Image')

    def __str__(self):
        return "{product}_{pk}".format(product=self.product.title, pk=self.pk)



class Brand(models.Model):
    name = models.CharField(max_length=200, help_text=u'브랜드명')
    website = models.CharField(blank=True, null=True, max_length=200, help_text=u'홈페이지')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, help_text=u'카테고리명')

    def __str__(self):
        return self.name


class ProductItemQuerySet(models.query.QuerySet):
    def featured(self):
        return self.filter(featured=True)
    
    def active(self):
        return self.filter(active=True)
    
    def get_normal(self):
        return self.filter(product_type='normal')
    
    def get_bidding(self):
        return self.filter(product_type='bidding')



    def search(self, query):
        lookups = (Q(product__title__icontains=query) | 
                  Q(product__description__icontains=query) |
                  Q(product__brand__name__icontains=query) |
                  Q(product__category__name__icontains=query) |
                  Q(tag__title__icontains=query)
                  )
                  
        return self.filter(lookups).distinct() # distinct 안하면 저위의 lookup들이 중복으로 검색되는 것들을 다 표시하게된다. 그냥 누적하되 중복은안되야하는게 맞을때 하므.



class ProductItemManager(models.Manager):
    '''
    경매현재가격은 맨처음 만들어질떄 product_type검사해서 있다면 start랑 동일하게 하자. blank 가능.
    '''
    
    pass
    def get_queryset(self):
        return ProductItemQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def featured(self):
        return self.get_queryset().featured()

    def get_normal(self):
        return self.featured().get_normal()

    def get_bidding(self):
        return self.featured().get_bidding()

    def get_category(self, category):
        return self.featured().filter(product__category=category)

    # def get_by_id(self, id):
    #     qs = self.get_queryset().filter(id=id)
    #     if qs.count() == 1:
    #         return qs.first()
    #     return None
    
    def search(self, query):
        return self.get_queryset().featured().search(query)


class ProductItem(models.Model):
    # 일반항목(필수)
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    info_delivery_from  = models.CharField(default='domestic', max_length=30, choices=DELIVERY_FROM_CHOICE, help_text=u'배송방법_국내해외')
    amount              = models.IntegerField(default=0, help_text=u'판매수량(경매 or 일반)')
    option              = models.BooleanField(default=False, help_text=u'옵션유무여부')    # 용도: 보여지게하기
    # size_option         = models.ForeignKey(SizeOption, blank=True, null=True, on_delete=models.CASCADE)
    
    sale_ratio          = models.DecimalField(default=0, max_digits=100, decimal_places=1, help_text=u'할인율')
    # limit_price         = models.PositiveIntegerField(default=0, help_text=u'가격(일반가격 & 경매한도가)')
    price               = models.PositiveIntegerField(default=0, help_text=u'가격(일반가격 & 경매한도가)') # 기존 limit_price를 price로 개편
    product_type        = models.CharField(max_length=20, default='normal', choices=PRODUCT_TYPE)
    
    info_product_date   = models.CharField(max_length=100, blank=True, null=True, help_text=u'제조연월_의류만 해당')

    updated             = models.DateTimeField(auto_now_add=True) # 업로드날짜.
    featured            = models.BooleanField(default=False)    # 용도: 보여지게하기
    active              = models.BooleanField(default=True)     # 용도: 구매가능여부결정.(보여져도 구매안되게할 수 있다.)
    slug                = models.SlugField(blank=True, unique=True, allow_unicode=True)
    
    # 경매항목(product-type = bidding 시 필수로 입력되게 나중에 업로드 폼 짤 것.)
    start_price         = models.PositiveIntegerField(blank=True, null=True, help_text=u'경매시작가격')
    price_step          = models.IntegerField(default=5000, blank=True, null=True, choices=PRICE_STEP_CHOICE, help_text=u'경매가격상승단위')
    current_price       = models.PositiveIntegerField(default=0,  blank=True, null=True, help_text=u'경매현재가격')  # 경매현재가격은 맨처음 만들어질떄 product_type검사해서 있다면 start랑 동일하게 하자. blank 가능.
    bidding_start_date  = models.DateTimeField(default=timezone.now,  blank=True, null=True, help_text=u'경매시작일')
    bidding_end_date    = models.DateTimeField(default=timezone.now,  blank=True, null=True, help_text=u'경매종료일')
    remain_bidding_time = models.CharField(default=0, max_length=200, blank=True, null=True, help_text=u'남은경매시간')
    bidding_on          = models.CharField(default=0, max_length=200,  blank=True, null=True, choices=BIDDING_STATUS_CHOICE, help_text=u'경매여부')
    

    objects = ProductItemManager()

    def __str__(self):
        updated = self.updated
        year = updated.year
        month = updated.month
        day = updated.day
        formmated_updated = "{:04d}{:02d}{:02d}".format(year, month, day)
        return "{}_{}_{}".format(formmated_updated, self.product_type, self.product.title)

    def get_absolute_url(self):
        # return "products/{slug}".format(slug=self.slug)
        # return "detail/{slug}/".format(slug=self.slug)
        if self.product_type == 'bidding':
            return reverse("products:product_bidding_detail", kwargs={"slug":self.slug})
        else:
            return reverse("products:product_detail", kwargs={"slug":self.slug})
            


    @property
    def limit_price(self): # 경매시에는 price가 limit_price가 되므로 겸용가능하게 설정.
        return self.price

def product_item_pre_save_receiver(sender, instance, *args, **kwargs):
    # 슬러그 설정
    if not instance.slug:
        instance.slug = unique_product_item_slug_generator(instance)
    # 기본 current_price 설정
    if instance.current_price is None:
        instance.current_price= instance.price
    # 할인율
    if instance.product_type == 'normal':
        instance.sale_ratio = (instance.product.list_price - instance.price) / instance.product.list_price * 100
    elif instance.product_type == 'bidding':
        instance.sale_ratio = (instance.product.list_price - instance.current_price) / instance.product.list_price * 100 
    # 남은 비딩타임.
    now = timezone.now()
    time_remain = instance.bidding_end_date - now
    # print(time_remain, type(time_remain))
    # instance.remain_bidding_time = "{}시간{}분".format(time_remain.hour, time_remain.minute)
    instance.remain_bidding_time = strfdelta(time_remain, "{hours}:{minutes}:{seconds}")
    # instance.remain_bidding_time = strfdelta(time_remain, "{days} days {hours}:{minutes}:{seconds}")
    # instance.remain_bidding_time = time_remain

    bidding_on = None
    if now < instance.bidding_start_date:
        bidding_on = 'bidding_ready' # 경매 준비중
    elif now >= instance.bidding_start_date and now < instance.bidding_end_date and instance.current_price < instance.limit_price:
        bidding_on = 'bidding'
    elif now > instance.bidding_end_date or instance.current_price == instance.limit_price:
        bidding_on = 'bidding_end'
    else:
        bidding_on = None
    instance.bidding_on = bidding_on

pre_save.connect(product_item_pre_save_receiver, sender=ProductItem)



class SizeOption(models.Model):
    product_item    = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    size            = models.IntegerField(default=0, help_text=u'사이즈')
    amount          = models.IntegerField(default=0, help_text=u'사이즈별수량')

    def __str__(self):
        return "{}_{}".format(self.product_item, self.size)