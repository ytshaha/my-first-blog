import os
import urllib.request
from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm
from django.utils import timezone
from django.core.files import File
from django.core.files.base import ContentFile, File
from django.urls import reverse_lazy

from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse
# from _compact import JsonResponse
from django.http import JsonResponse

from django import forms
from django.views import generic
import django_excel as excel

from django.template.defaultfilters import slugify

from django.shortcuts import render
from django.shortcuts import redirect
from sqlalchemy import create_engine
# Create your views here.
from django.http import HttpResponse
from django.conf import settings
import pandas as pd
from .models import Test
from products.models import Product, ProductItem, SizeOption, upload_main_image_path
from products.forms import ProductForm, ProductItemForm
from mysite.utils import unique_slug_generator, unique_product_item_slug_generator



# def get_filename_ext(filepath):
#     base_name = os.path.basename(filepath)
#     name, ext = os.path.splitext(filepath)
#     return name, ext

# def upload_main_image_path(instance, filename):
#     print("내가 실행된다.views.py의 업로드 메인이미지")
#     # new_filename = random.randint(1, 39111111)
#     # name, ext = get_filename_ext(filename)
#     # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
#     # return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
#     title = instance.number
#     slug = slugify(title)
#     return "products/{product_title}/{slug}_{filename}".format(product_title=title, slug=slug, filename=filename)  



@staff_member_required 
def staff_home(request):
    return render(request, "staff/home.html", {})



class UploadProductView(generic.CreateView):
    form_class = ProductForm
    template_name = 'staff/upload_product.html'
    success_url = reverse_lazy('products:product_list')

    def get_context_data(self, *args, **kwargs):
        context = super(UploadProductView, self).get_context_data(*args, **kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)
 


class UploadProductItemView(generic.CreateView):
    form_class = ProductItemForm
    template_name = 'staff/upload_product_item.html'
    success_url = reverse_lazy('products:product_list')

    def get_context_data(self, *args, **kwargs):
        context = super(UploadProductItemView, self).get_context_data(*args, **kwargs)
        return context

    def form_valid(self, form):
        if form.instance.product_type == 'bidding':  
            form.instance.current_price = form.instance.start_price
        return super().form_valid(form)


# def upload_product(request):
#     # ImageFormSet이 멀티이미지 업로드를 가능하게 해줌. extra는 업로드가능개수. 폼이 완성된 갯수만큼만 업로드 하므로 안심.
#     ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=10)
#     if request.method == 'POST':
#         productform = ProductForm(request.POST, request.FILES)
#         formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())
#         print("productform.is_valid():", productform.is_valid())
#         print("formset.is_valid():", formset.is_valid())

#         if productform.is_valid() and formset.is_valid():
#             new_product_bidding = productform.save(commit=False) # 비딩용 product -> 이미지연결
#             new_product_bidding.save()

#             for form in formset.cleaned_data:
#                 if form:
#                     image = form['image']
#                     photo = ProductImage(product=new_product_bidding, image=image)
#                     photo.save()
#             messages.success(request, "업로드완료")
#             return redirect('products:product_list')
#     else:
#         productform = ProductForm()
#         formset = ImageFormSet(queryset=ProductImage.objects.none())
#     return render(request, 'products/upload_product.html', {'productform': productform, 'formset': formset})




def upload_product_by_file(request):
    return render(request, 'staff/upload_product_by_file.html', {})

def upload_product_complete(request):
    if request.method == 'POST':
        file = request.FILES['database_file']
    try:
        df = pd.read_excel(file)
        df = df.where(pd.notnull(df), None)

        print('성공적으로 파일 가져옴')
    except:
        raise ObjectDoesNotExist
    
    print(df)
    df.columns=["number", "title", "brand", 'category', 'list_price',  # 필수항목
                'info_made_country', 'info_product_number', 'info_delivery', 'main_image',  # 필수항목
                'image1', 'image2', 'image3', 'image4', 'image5', 
                'image6', 'image7', 'image8', 'image9',
                'info_product_kind', 'info_material', 'info_feature', 'info_product_person', 'info_alert', # 비필수
                'info_quality_standard', 'info_as', 'description', 'video_link' # 비필수
                ]
    no_updated_dict = {}
    engine = create_engine('sqlite://', echo=False)
    now1 = timezone.now()
    for index, row in df.iterrows():
        data = dict(row)
        number = data['number']
        brand = data['brand']
        # obj = Test.objects.create(full_name=row['full_name'], phone_number=row['phone_number'])
        obj, created = Product.objects.get_or_new(request, number=number, data=data)
        if not created:
            no_updated_dict[data['number']] = 'Already Exist'
        elif created == 'Brand DoesNotExist':
            no_updated_dict[data['number']] = created
        elif created == 'Category DoesNotExist':
            no_updated_dict[data['number']] = created

        image_cols = ['main_image', 'image1', 'image2', 'image3', 'image4', 'image5', 
                      'image6', 'image7', 'image8', 'image9']
        obj_images = [obj.main_image, obj.image1, obj.image2, obj.image3, obj.image4, obj.image5, 
                      obj.image6, obj.image7, obj.image8, obj.image9]
                    
        if created:
            for i, col in enumerate(image_cols):
                if data[col] is not None:
                    try:
                        with open(data[col], 'rb') as f:
                            filename = upload_main_image_path(obj, os.path.basename(f.name))
                            obj_images[i] = File(f, name=filename)
                            # obj.save()
                            # self.license_file.save(upload_main_image_path, File(f))
                    except OSError:
                        response = urllib.request.urlretrieve(data[col])
                        # print("response", response)
                        

                        # contents = open(response[0]).read()
                        with open(response[0], 'rb') as f:
                            file_url = urlparse(data[col])
                            filename = os.path.basename(file_url.path)
                            obj_images[i].save(filename, f)
                            print(i, "이미지 확인", obj_images[i])
                            obj.save()
                            # obj.save()
            obj.save()

    product_qs = Product.objects.all()
    now2 = timezone.now()
    print(now2-now1)
    context = {
        'qs' : product_qs,
        'no_updated_dict': no_updated_dict
    }
    return render(request, 'staff/upload_product_complete.html', context)

def upload_product_item_by_file(request):
    return render(request, 'staff/upload_product_item_by_file.html', {})

def upload_product_item_complete(request):
    if request.method == 'POST':
        file = request.FILES['database_file']
    try:
        df = pd.read_excel(file)
        df = df.where(pd.notnull(df), None)

        print('성공적으로 파일 가져옴')
    except:
        raise ObjectDoesNotExist
    
    print(df)
    df.columns=["product", "info_delivery_from", "amount", 'option', 'price', 'info_product_date', 'description', 'product_type', # 필수항목 
                'start_price', 'price_step', 'bidding_start_date', 'bidding_end_date',  # 경매항목
                'option_1', 'option_1_amount', 'option_2', 'option_2_amount', 'option_3', 'option_3_amount', 'option_4', 'option_4_amount', 'option_5', 'option_5_amount', # 옵션 및 옵션 재고 
                'option_6', 'option_6_amount', 'option_7', 'option_7_amount', 'option_8', 'option_8_amount', 'option_9', 'option_9_amount', 'option_10', 'option_10_amount'  # 옵션 및 옵션 재고
                ]
    option_cols = ['option_1', 'option_2', 'option_3', 'option_4', 'option_5', # 옵션 
                   'option_6', 'option_7', 'option_8', 'option_9', 'option_10']
    no_updated_dict = {}
    engine = create_engine('sqlite://', echo=False)
    now1 = timezone.now()
    for index, row in df.iterrows():
        data = dict(row)
        # obj = Test.objects.create(full_name=row['full_name'], phone_number=row['phone_number'])
        
        obj, created = ProductItem.objects.new(data)

        

        for option in option_cols:
            if data[option]:
                SizeOption.objects.create(product_item=obj, option=data[option], amount=data[option + '_amount'])
        # if not created:
        #     no_updated_dict[data['number']] = 'Already Exist'
        # elif created == 'Brand DoesNotExist':
        #     no_updated_dict[row['number']] = created
        # elif created == 'Category DoesNotExist':
        #     no_updated_dict[row['number']] = created

        # image_cols = ['main_image', 'image1', 'image2', 'image3', 'image4', 'image5', 
        #               'image6', 'image7', 'image8', 'image9']
        # obj_images = [obj.main_image, obj.image1, obj.image2, obj.image3, obj.image4, obj.image5, 
        #               obj.image6, obj.image7, obj.image8, obj.image9]
                    
        # if created:
        #     for i, col in enumerate(image_cols):
        #         if row[col] is not None:
        #             try:
        #                 with open(row[col], 'rb') as f:
        #                     filename = upload_main_image_path(obj, os.path.basename(f.name))
        #                     obj_images[i] = File(f, name=filename)
        #                     # obj.save()
        #                     # self.license_file.save(upload_main_image_path, File(f))
        #             except OSError:
        #                 response = urllib.request.urlretrieve(row[col])
        #                 # print("response", response)
                        

        #                 # contents = open(response[0]).read()
        #                 with open(response[0], 'rb') as f:
        #                     file_url = urlparse(row[col])
        #                     filename = os.path.basename(file_url.path)
        #                     obj_images[i].save(filename, f)
        #                     print(i, "이미지 확인", obj_images[i])
        #                     obj.save()
        #                     # obj.save()
        #     obj.save()

    product_item_qs = ProductItem.objects.all()
    now2 = timezone.now()
    print(now2-now1)
    context = {
        'qs' : product_item_qs
    }
    return render(request, 'staff/upload_product_item_complete.html', context)