import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils import timezone
from django.http import JsonResponse


from mysite.mixin import StaffRequiredView
from .models import Product, ProductItem, Brand, Category, ProductImage, SizeOption
from biddings.models import Bidding
from orders.models import Order
from .forms import ProductForm, ProductItemForm, ProductImageForm
from biddings.forms import BiddingForm
from carts.models import Cart

CATEGORY_CHOICES = (
    ('woman', '여성의류'),
    ('man', '남성의류'),
    ('shoes', '신발'),
    ('bag', '가방'),
    ('acc', '명품잡화'),
    ('kid', '키즈'),
)

# 노말 물품은 아래것으로 통일
class ProductNormalListView(generic.ListView):
    '''
    Featured = True이고 product_type= Noraml인 물품들을 표시함.(active와 다른 개념. active는 구매가능여부.)
    '''
    template_name = 'products/product_list.html'
    context_object_name = 'product_items'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductNormalListView, self).get_context_data(*args, **kwargs)
        brands = Brand.objects.all()
        context['brands'] = brands
        context['is_staff_check'] = False

        try: 
            context['brand'] = self.kwargs['brand']
        except:
            pass
        try:
            context['category'] = self.kwargs['category']
        except:
            pass    

        context['category_qs'] = CATEGORY_CHOICES
        # if self.request.method == 'GET':
        #     brand = self.request.GET.get('brand', None)
        #     category = self.request.GET.get('category', None)
        # context['brand'] = brand
        # context['category'] = category
        
        
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request

        product_item_qs = ProductItem.objects.featured().get_normal()

        #정렬기준을 세션에 저장했으면 그기준. 아니면 아닌걸로.    
        print(request.method, '요청됨.')
        
        if request.method == 'GET':
            post_purpose = request.GET.get('post_purpose', None)
            if post_purpose == 'filter_product':
                category_selected = request.GET.getlist('category_selected', None)
                brand_selected = request.GET.getlist('brand_selected', None)
                product_item_qs = product_item_qs.filter(product__category__name__in=category_selected).filter(product__brand__name__in=brand_selected)           
            elif post_purpose =='ordering_method':
                request.session['ordering'] = request.GET.get('ordering', None)
        # product_item_obj = ProductItem.objects.get(slug=slug)
        
        try:
            ordering = request.session['ordering']
            print('ordering', ordering)
        except:
            ordering = None

        if post_purpose is None:
            # brand 받았나
            try:
                brand = self.kwargs['brand']
            except:
                brand = None
            # category 받았나
            try:
                category = self.kwargs['category']
            except:
                category = None
            
            # 필터링
            if not brand is None:
                product_item_qs = product_item_qs.filter(product__brand__name=brand) # 두개 합친건데 되는지 확인. 
            elif not category is None:
                product_item_qs = product_item_qs.filter(product__category__name=category) # 두개 합친건데 되는지 확인. 
        # 전체 쿼리셋 저장 및 업데이트
        for product_item_obj in product_item_qs:
            product_item_obj.save()

        if ordering is not None:
            product_item_qs = product_item_qs.order_by(ordering)
        # if ordering is not None:
        #     if ordering == '-price':
        #         product_item_qs = product_item_qs.order_by(ordering)
        #     elif ordering == 'price':
        #         product_item_qs = product_item_qs.order_by(ordering)
        #     elif ordering == '-updated':
        #         product_item_qs = product_item_qs.order_by(ordering)
        #     else:
        #         pass

        return product_item_qs

# 비딩 물품은 아래것으로 통일
class ProductBiddingListView(LoginRequiredMixin, generic.ListView):
    '''
    Featured = True이고 product_type= bidding인 물품들을 표시함.(active와 다른 개념. active는 구매가능여부.)
    bidding_ready와 bidding 두가지에 대하 queryset을 준비해야함.
    '''
    template_name = 'products/product_bidding_list.html'
    context_object_name = 'product_items'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductBiddingListView, self).get_context_data(*args, **kwargs)
        request = self.request
        brands = Brand.objects.all()
        context['brands'] = brands
        context['is_staff_check'] = False

        product_item_qs = ProductItem.objects.featured().get_bidding()

        #정렬기준을 세션에 저장했으면 그기준. 아니면 아닌걸로.    
        
        if request.method == 'GET':
            post_purpose = request.GET.get('post_purpose', None)
            if post_purpose == 'filter_product':
                category_selected = request.GET.getlist('category_selected', None)
                brand_selected = request.GET.getlist('brand_selected', None)
                product_item_qs = product_item_qs.filter(product__category__in=category_selected).filter(product__brand__in=brand_selected)           
            elif post_purpose =='ordering_method':
                request.session['ordering'] = request.GET.get('ordering', None)
        # product_item_obj = ProductItem.objects.get(slug=slug)

        try:
            ordering = request.session['ordering']
        except:
            ordering = None


        else:
            # brand 받았나
            try:
                brand = self.kwargs['brand']
            except:
                brand = None
            # category 받았나
            try:
                category = self.kwargs['category']
            except:
                category = None
           
            # 필터링
            if not brand is None:
                product_item_qs = product_item_qs.filter(product__brand__name=brand) # 두개 합친건데 되는지 확인. 
            elif not category is None:
                product_item_qs = product_item_qs.filter(product__category__name=category) # 두개 합친건데 되는지 확인. 

        # 전체 쿼리셋 저장 및 업데이트
        for product_item_obj in product_item_qs:
            product_item_obj.save()

        if ordering is not None:
            product_item_qs = product_item_qs.order_by(ordering)
        
        # 바딩준비, 비딩중으로 qs 따로 저장.
        bidding_item_qs = product_item_qs.filter(bidding_on='bidding')
        bidding_ready_item_qs = product_item_qs.filter(bidding_on='bidding_ready')

        context['bidding_items'] = bidding_item_qs
        context['bidding_ready_items'] = bidding_ready_item_qs
        context['category_qs'] = CATEGORY_CHOICES
        return context
    def get_queryset(self, *args, **kwargs):
        return ProductItem.objects.get_bidding()


# 이건 그냥 본인 bidding list 에서만 확인하게 해도 충분할듯.
class ProductBiddingCompleteListView(LoginRequiredMixin, generic.ListView):
    '''
    Featured = True이고 product_type = Bidding인 물품들을 표시함.(active와 다른 개념. active는 구매가능여부.)
    '''
    template_name = 'products/product_bidding_list.html'
    context_object_name = 'product_items'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductBiddingCompleteListView, self).get_context_data(*args, **kwargs)

        product_item_qs = ProductItem.objects.featured().get_bidding().filter(bidding_on='bidding_end')

        for product_item_obj in product_item_qs:
            product_item_obj.save()
        
        context['bidding_end_items'] = product_item_qs

        return context
            
    def get_queryset(self, *args, **kwargs):
        request = self.request
        return ProductItem.objects.get_bidding().filter(bidding_on='bidding_end').order_by('-updated') # 두개 합친건데 되는지 확인. 



# 스탭만 들어갈수있는 mixin을만들자.
def product_make_featured(request):
    if request.method == 'POST':
        product_item_id = request.POST.get('product_item_id', None)
        product_item_obj = ProductItem.objects.get(id=product_item_id)
        product_item_obj.featured = True
        print("Product Item {} is featured.".format(product_item_obj.product.title))
        product_item_obj.save()
        return redirect('products:check')

def product_make_unfeatured(request):
    if request.method == 'POST':
        product_type = request.POST.get('product_type', None)
        product_item_id = request.POST.get('product_item_id', None)
        product_item_obj = ProductItem.objects.get(id=product_item_id)
        product_item_obj.featured = False
        print("Product Item {} is unfeatured.".format(product_item_obj.product.title))
        product_item_obj.save()
        if product_type == 'bidding':
            return redirect('products:product_bidding_list')
        elif product_type == 'normal':
            return redirect('products:product_list')
        else:
            raise Http404("직원님...해당물품의 아이디가 이상합니다.")  

# 스탭이 PRODUCT 올리기전에 맞는지 실제 뷰로 확인하고 맞으면 간단한 버튼으로 Featured되게 하는 뷰
class ProductStaffCheckView(LoginRequiredMixin, StaffRequiredView, generic.ListView):
    '''
    Featured = False인 Bidding과 normal 모두를 표시함.
    직접 detail 들어가보고 괜찮으면 버튼하나 만들어서 해당 물품의 featured를 True로 변하게함.
    역으로 일반 list 뷰에서도 해당 버튼 누르면 다시 False로 변하게 하여 안보이게 가능.
    얘도 날짜로 필터링가능하게해야할듯.
    '''
    template_name = 'products/product_list.html'
    context_object_name = 'product_items'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductStaffCheckView, self).get_context_data(*args, **kwargs)
        brands = Brand.objects.all()
        context['brands'] = brands
        context['is_staff_check'] = True
        normal_product_items_qs = ProductItem.objects.filter(featured=False).filter(product_type='normal')
        bidding_product_items_qs = ProductItem.objects.filter(featured=False).filter(product_type='bidding')

        for product_item_obj in normal_product_items_qs:
            product_item_obj.save()
        for product_item_obj in bidding_product_items_qs:
            product_item_obj.save()
        
        try:
            select_date = self.kwargs['date']
        except:
            context['normal_product_items'] = normal_product_items_qs
            context['bidding_product_items'] = bidding_product_items_qs
            return context

        start_date = timezone.now().date()
        end_date = timezone.now().date() + timezone.timedelta(days=1)
        start_year, start_month, start_day  = start_date.year, start_date.month, start_date.day
        end_year, end_month, end_day = end_date.year, end_date.month, end_date.day
        start_datetime = timezone.make_aware(timezone.datetime(start_year, start_month, start_day, 0, 0, 0))
        end_datetime = timezone.make_aware(timezone.datetime(end_year, end_month, end_day, 0, 0, 0))

        context['normal_product_items'] = normal_product_items_qs.filter(updated__gte=start_datetime, updated__lt=end_datetime)
        context['bidding_product_items'] = bidding_product_items_qs.filter(updated__gte=start_datetime, updated__lt=end_datetime)
        

        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        
        # brand 받았나
        try:
            brand = self.kwargs['brand']
        except:
            brand = None
        # category 받았나
        try:
            category = self.kwargs['category']
        except:
            category = None
        
        product_item_qs = ProductItem.objects.filter(featured=False)
        
        # 필터링
        if not brand is None:
            product_item_qs = product_item_qs.filter(product__brand__name=brand).order_by('-updated') # 두개 합친건데 되는지 확인. 
        elif not category is None:
            product_item_qs = product_item_qs.filter(product__category__name=category).order_by('-updated') # 두개 합친건데 되는지 확인. 
        else:
            product_item_qs = product_item_qs.order_by('-updated') # 두개 합친건데 되는지 확인. 

        # 전체 쿼리셋 저장 및 업데이트
        if product_item_qs.count() == 1:
            product_item_qs.first().save()
        elif product_item_qs.count() > 1:
            for product_item_obj in product_item_qs:
                product_item_obj.save()
        else:
            pass

        # 날짜받았냐?
        try:
            select_date = self.kwargs['date']
        except:
            return product_item_qs
        
        start_date = timezone.now().date()
        end_date = timezone.now().date() + timezone.timedelta(days=1)
        start_year, start_month, start_day  = start_date.year, start_date.month, start_date.day
        end_year, end_month, end_day = end_date.year, end_date.month, end_date.day
        start_datetime = timezone.make_aware(timezone.datetime(start_year, start_month, start_day, 0, 0, 0))
        end_datetime = timezone.make_aware(timezone.datetime(end_year, end_month, end_day, 0, 0, 0))

        return product_item_qs.filter(updated__gte=start_datetime, updated__lt=end_datetime)
    

class ProductFeaturedDetailView(generic.DetailView):
    template_name = 'products/product_featured-detail.html'
    context_object_name = 'product'

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Product.objects.all().featured



# class UserProductHistoryView(LoginRequiredMixin, generic.ListView):
#     template_name = 'products/product_list.html'
#     context_object_name = 'products'

#     def get_context_data(self, *args, **kwargs):
#         context = super(ProductListView, self).get_context_data(*args, **kwargs)
#         print(context)
#         brands = Brand.objects.all()
#         context['brands'] = brands
#         return context

#     def get_queryset(self, *args, **kwargs):
#         request = self.request
#         return Product.objects.order_by('-bidding_start_date')


# 실질적으로 사용하는 detail View
class ProductDetailSlugView(generic.DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product_item'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        slug = self.kwargs.get('slug')
        product_item_obj = ProductItem.objects.get(slug=slug)
        product_obj = product_item_obj.product
        product_type = product_item_obj.product_type
        
        cart_obj, new_obj = Cart.objects.new_or_get(request) #??
        
        # 이미지들을 리스트로 미리 만들기.
        images = [product_obj.main_image,
                  product_obj.image1,
                  product_obj.image2,
                  product_obj.image3,
                  product_obj.image4,
                  product_obj.image5,
                  product_obj.image6,
                  product_obj.image7,
                  product_obj.image8,
                  product_obj.image9,
                  ]

        # product_images_qs = ProductImage.objects.filter(product=product_obj)
        product_obj.save()
        
        if product_type == 'bidding':
            bidding_obj_up_to_10 = Bidding.objects.filter(product_item=product_item_obj).order_by('-timestamp')[:10]
            bidding_obj = Bidding.objects.filter(product_item=product_item_obj).order_by('-timestamp')
            now = timezone.now()
            bidding_on = None
            if now < product_item_obj.bidding_start_date:
                bidding_on = 'bidding_ready' # 경매 준비중
            elif now >= product_item_obj.bidding_start_date and now < product_item_obj.bidding_end_date and product_item_obj.current_price < product_item_obj.price:
                bidding_on = 'bidding'
            elif now > product_item_obj.bidding_end_date or product_item_obj.current_price == product_item_obj.price:
                bidding_on = 'bidding_end'
            else:
                bidding_on = None

        else:
            bidding_obj_up_to_10 = None
            bidding_on = None

        # 경매준비 경매중 경매종료 여부확인
        
        # 재고여부
        # 1) 옵션없을 경우 - amount select list도 생성
        # 2) 옵션있는 경우 - size_option.. 아 근데 amount select list 도 jquery로 변경시켜줘야겠네...
        is_stock = None
        size_option = None
        if product_item_obj.option:
            # 사이즈옵션있는경우
            is_stock = False
            size_option = SizeOption.objects.filter(product_item=product_item_obj)
            amount_select_list = None
            for size in size_option:
                if size.amount > 0:
                    is_stock = True
        else:
            # 사이즈 옵션 없는경우
            is_stock = True
            if product_item_obj.amount < 1:
                is_stock = False
                amount_select_list = 0
            elif product_item_obj.amount > 10:
                amount_select_list = range(1, 11)
            else:
                amount_select_list = range(1, product_item_obj.amount + 1)
                    
        # if request.method == 'POST':
        #     if post_purpose == 'size_changed':
        #         size = request.POST.get('size')
        #         print('size:',size)
        #         if not size:

        #             json_data = {
        #                 'amount_select_list': None
        #                 }
        #             JsonResponse(json_data, statis=200)
        #         size_obj = SizeOption.objects.get(product_item=product_item_obj, size=size)
        #         size_amount = size_obj.amount
        #         if size_amount > 10:
        #             amount_select_list = range(1, 11)
        #         else:
        #             amount_select_list = range(1, size_amount + 1)
                
        #         print("Ajax_Size change request")
        #         json_data = {
        #             'amount_select_list': amount_select_list
        #         }
        #         JsonResponse(json_data, statis=200)
        #     else:
        #         pass

        context['size_option'] = size_option
        context['product_item'] = product_item_obj
        context['product_type'] = product_type
        context['amount_select_list'] = amount_select_list
        context['is_stock'] = is_stock
        context['bidding_on'] = bidding_on
        context['cart'] = cart_obj
        context['images'] = images
        context['bidding_obj_up_to_10'] = bidding_obj_up_to_10
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = get_object_or_404(ProductItem, slug=slug, active=True)
        try:
            instance = ProductItem.objects.get(slug=slug, active=True)
        except ProductItem.DoesNotExist:
            raise Http404("Not found..")
        except ProductItem.MultipleObjectsReturned:
            qs = ProductItem.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404("Uhmmmmm")
        return instance

    def post(self, request, *args, **kwargs):
        # context = self.get_context_data(object=self.object)
        # context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        slug = self.kwargs.get('slug')
        product_item_obj = ProductItem.objects.get(slug=slug)
        post_purpose = request.POST.get('post_purpose')
        

        if request.method == 'POST' and request.is_ajax():
            if post_purpose == 'size_changed':
                option = request.POST.get('option', None)
                print('option:',option, type(option))
                # try:
                #     option = int(option)
                # except:
                #     print('option를 인트화하지 못했다ㅃ!!!')
                #     json_data = {
                #         'amount_select_list': None,
                #     'amount_value': None
                #         }
                #     return JsonResponse(json_data)
                #     # print("사이즈가 None으로 선택되었다.")
                #     # return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")
                # print('그냥 넘어갔다. 일반 숫자가 돼었다.')
                size_obj = SizeOption.objects.get(product_item=product_item_obj, option=option)
                size_amount = size_obj.amount
                if size_amount == 0:
                    amount_select_list = ['---']
                    amount_value = 0
                elif size_amount > 10:
                    amount_select_list = list(range(1, 11))
                    amount_value = 10
                else:
                    amount_select_list = list(range(1, size_amount + 1))
                    amount_value = size_amount
                    
                amount_select_list_json = json.dumps(amount_select_list)

                
                print("Ajax_Size change request")
                json_data = {
                    'amount_select_list': amount_select_list_json,
                    'amount_value': amount_value
                }
                return JsonResponse(json_data)
            else:
                pass
        return self.object


        
    # def get_object(self, *args, **kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     instance = Product.objects.get_by_id(pk)
    #     if instance is None:
    #         raise Http404("Product doesn't exist")
    #     return instance

    
# @login_required
# def product_list(request, option=False):
#     if not option:
#         products = Product.objects.all()
#     else: 
#         products = Product.objects.filter(category__name=option)
#     return render(request, 'shop/product_list.html', {'products':products})


# 아직 잘안되므로 꼭 확인하자.......

# @login_required
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, 'products/product_detail.html', {'product':product})

# @login_required
def upload_product(request):
    # ImageFormSet이 멀티이미지 업로드를 가능하게 해줌. extra는 업로드가능개수. 폼이 완성된 갯수만큼만 업로드 하므로 안심.
    ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=10)
    if request.method == 'POST':
        productform = ProductForm(request.POST, request.FILES)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())
        print("productform.is_valid():", productform.is_valid())
        print("formset.is_valid():", formset.is_valid())

        if productform.is_valid() and formset.is_valid():
            new_product_bidding = productform.save(commit=False) # 비딩용 product -> 이미지연결
            new_product_bidding.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = ProductImage(product=new_product_bidding, image=image)
                    photo.save()
            messages.success(request, "업로드완료")
            return redirect('products:product_list')
    else:
        productform = ProductForm()
        formset = ImageFormSet(queryset=ProductImage.objects.none())
    return render(request, 'products/upload_product.html', {'productform': productform, 'formset': formset})


class UploadProductItemView(generic.CreateView):
    form_class = ProductItemForm
    template_name = 'products/upload_product_item.html'
    success_url = reverse_lazy('products:product_list')

    def get_context_data(self, *args, **kwargs):
        context = super(UploadProductItemView, self).get_context_data(*args, **kwargs)
        return context

    def form_valid(self, form):
        if form.instance.product_type == 'bidding':  
            form.instance.current_price = form.instance.start_price
        return super().form_valid(form)
 


class BiddingDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'biddings/bidding_new.html'
    context_object_name = 'bidding'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(BiddingDetailView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

    def get_queryset(self, *args, **kwargs):#3333333333333333# 2021. 02. 18 출근하면서 여기까지 편집함.
        request = self.request
        pk = self.kwargs.get('pk')
        return Product.objects.filter(pk=pk)



# 그냥 나중에 쓸수도 있는 json이기에 남겨둠.
def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    cart_items = [{
            "id": x.id,
            "url": x.product.get_absolute_url(),
            "name": x.product.name, 
            # "price":x.product.current_price,
            "price":select_price(x),
            "amount":x.amount
            } for x in cart_obj.cart_items.all()] # [<object>, <object>, <object>] 그래서 제이슨 형태로 건내줘야힘.
    cart_data = {"cart_items":cart_items, "subtotal":cart_obj.subtotal, "total":cart_obj.total}
    return JsonResponse(cart_data)



def product_item_featured_update_api_view(request):
    product_item_slug = request.POST.get('product_item_slug')
    product_item_obj = ProductItem.objects.filter(slug=product_item_slug)
    if product_item_obj.featured:
        product_item_obj.featured = False
        featured = False
    else:
        product_item_obj.featured = True
        featured = True
    if request.is_ajax(): # Asyncronous JavaScripts ANd XM
        print("Ajax feature form request")
        json_data = {
            "featured": added,
        }
        return JsonResponse(json_data, status=200)

# 새로운 비딩을 시작하고 혹은 있는 비딩이 있으면 가격과 timestam[를 업뎃하는 것.]
# 시간안에 끝났는지를 product의 비딩끝타임으로 확인하여 비딩참여가능한지 홛ㄱ인.
# new_or_get으로하다.
# 기본적으로 유저만 넣었으므로 product와 price등을 입력해야함.
# product에서 비딩참여를 눌렀으므로 form의 post로 product의 슬러그를확인하여 하자. 슬러그로 들어가려고하니까.
# def bidding_new(request):

# def bidding_new(request, slug):
#     # product_slug = request.session.get('slug')
#     if request.method == 'POST':
#         form = BiddingForm(request.POST)
#         if form.is_valid():
#             bidding_obj, new_obj = Bidding.objects.new_or_get(request, slug=slug)
#             product_id = request.POST.get('product', None)
#             bidding_price = request.POST.get('bidding_price', None)
#             product_obj = Product.objects.get(id=product_id)
            
#             bidding_obj.bidding_price = bidding_price
#             bidding_obj.product = product_obj
#             bidding_obj.timestamp = timezone.now()
#             bidding_obj.save()
#             return redirect('products:product_detail_slug', slug=slug)
#     else:
#         form = BiddingForm()
#         context = {
#             'form': form,
#             'slug': slug
#         }
#     # return render(request, 'biddings/bidding_new.html', {'form':form, 'product_slug':product_slug})
#     return render(request, 'biddings/bidding_new.html', context)


#  fields = ('product','bidding_price',)

# class Bidding(models.Model):
#     bidding_id      = models.CharField(max_length=100) # 얘또한 아이디+slug조합으로 만들자.
# xx    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user            = models.ForeignKey(User, on_delete=models.CASCADE)
# xx    bidding_price   = models.PositiveIntegerField(default=0, help_text=u'경매참여가격') # 얘보다 높아야 참여가능하겠지.
#     timestamp       = models.DateTimeField(auto_now_add=True)
#     win             = models.BooleanField(default=False)
#     def __str__(self):
#         return self.bidding_id


# class BiddingManager(models.Manager):
#     def new_or_get(self, request):
#         user = request.user
#         bidding_id = request.session.get("bidding_id", None)
#         qs = self.get_queryset().filter(id=bidding_id)
#         # 일단 티켓이 엑티베이트인지 확인
#         ticket_qs = Ticket.objects.filter(user=user, status='activate')
#         if qs.count() == 1:
#             new_obj = False
#             bidding_obj = qs.first()
#             if request.user.is_authenticated and ticket_qs.exists(): # 로긴한것과 activate 티켓있는지 확인.나중에는 일정등급 user인지만 확인하게하자. 
#                 return bidding_obj, new_obj
#         else:
#             bidding_obj = self.new(user=request.user)
#             new_obj = True
#             request.session['bidding_id'] = bidding_obj.id
#         return bidding_obj, new_obj

#     def new(self, user=None):
#         user_obj = None
#         if user is not None:
#             if user.is_authenticated:
#                 user_obj = user
#         return self.model.objects.create(user=user_obj)


