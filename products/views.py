from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils import timezone


from .models import Product, Brand, Category, ProductImage
from biddings.models import Bidding
from orders.models import Order
from .forms import ProductForm, ProductImageForm
from biddings.forms import BiddingForm
from carts.models import Cart

class ProductFeaturedListView(LoginRequiredMixin, generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductCategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductCategoryListView, self).get_context_data(*args, **kwargs)
        print(context)
        brands = Brand.objects.all()
        context['brands'] = brands
        return context

    def get_queryset(self):
        print("self.kwargs:", self.kwargs)
        category = self.kwargs['category']
        if category is not None:
            return Product.objects.filter(category__name__icontains=category)
        return Product.objects.all()

class ProductBrandListView(LoginRequiredMixin, generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductBrandListView, self).get_context_data(*args, **kwargs)
        print(context)
        brands = Brand.objects.all()
        context['brands'] = brands
        return context

    def get_queryset(self):
        print("self.kwargs:", self.kwargs)
        brand = self.kwargs['brand']
        if brand is not None:
            # print('brand.name', brand.name)
            return Product.objects.filter(brand__name__icontains=brand)
        return Product.objects.all()



class ProductFeaturedDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'products/product_featured-detail.html'
    context_object_name = 'product'

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Product.objects.all().featured

class ProductListView(LoginRequiredMixin, generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        print(context)
        brands = Brand.objects.all()
        context['brands'] = brands
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.order_by('-bidding_start_date')

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
class ProductDetailSlugView(LoginRequiredMixin, generic.DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        slug = self.kwargs.get('slug')
        is_stock = True
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        product_images_qs = ProductImage.objects.filter(product__title=slug)
        product_obj = Product.objects.get(slug=slug)
        product_obj.save()
        bidding_obj_up_to_10 = Bidding.objects.filter(product=product_obj).order_by('-timestamp')[:10]
        bidding_obj = Bidding.objects.filter(product=product_obj).order_by('-timestamp')
        # 경매준비 경매중 경매종료 여부확인
        now = timezone.now()
        bidding_on = None
        if now < product_obj.bidding_start_date:
            bidding_on = 'bidding_ready' # 경매 준비중
        elif now >= product_obj.bidding_start_date and now < product_obj.bidding_end_date and product_obj.current_price < product_obj.limit_price:
            bidding_on = 'bidding'
        elif now > product_obj.bidding_end_date or product_obj.current_price == product_obj.limit_price:
            bidding_on = 'bidding_end'
        else:
            bidding_on = None
        # 상시판매물품 재고여부
        if product_obj.amount_always_on < 1:
            is_stock = False
            amount_select_list = 0
        else:
            amount_select_list = range(1, product_obj.amount_always_on + 1)
        
    
        
        context['amount_select_list'] = amount_select_list
        context['is_stock'] = is_stock
        context['bidding_on'] = bidding_on
        context['cart'] = cart_obj
        context['images'] = product_images_qs
        context['bidding_obj_up_to_10'] = bidding_obj_up_to_10
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found..")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slub, active=True)
            instance = qs.first()
        except:
            raise Http404("Uhmmmmm")
        return instance

# 사용안함.
class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        product_obj = Product.objects.filter(pk=pk)
        request.session['product_number'] = product_obj.number
        return product_obj

        
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
def product_upload(request):
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
    return render(request, 'products/product_upload.html', {'productform': productform, 'formset': formset})





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


