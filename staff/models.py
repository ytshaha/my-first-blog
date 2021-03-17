from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import timezone

from mysite.utils import unique_slug_generator, unique_product_item_slug_generator
User = settings.AUTH_USER_MODEL
# Create your models here.

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(filepath)
    return name, ext

def upload_main_image_path(instance, filename):
    # new_filename = random.randint(1, 39111111)
    # name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    title = instance.full_name
    slug = slugify(title)
    return "test/{product_title}/{slug}-{filename}".format(product_title=title, slug=slug, filename=filename)  

def upload_image_path(instance, filename):
    # new_filename = random.randint(1, 39111111)
    # name, ext = get_filename_ext(filename)
    # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
    title = instance.full_name
    slug = slugify(title)
    return "test/{product_title}/{slug}-{filename}".format(product_title=title, slug=slug, filename=filename)  


class TestManager(models.Manager):
    def get_or_new(self, request, full_name, data):
        user = request.user
        
        qs = self.get_queryset().filter(full_name=full_name)
        if qs.exists(): 
            obj = qs.first()
            new_obj = False
        else:
            obj = self.new(**data)
            new_obj = True
        return obj, new_obj

    def new(self, full_name, phone_number, image):
        return self.model.objects.create(full_name=full_name, phone_number=phone_number, image=image)



class Test(models.Model):
    full_name       = models.CharField(max_length=255, blank=True, null=True)
    phone_number    = models.CharField(max_length=255, blank=True, null=True)
    image           = models.FileField(upload_to=upload_main_image_path, null=True, blank=True)
    
    objects = TestManager()

    def __str__(self):
        return self.full_name
