from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.files.storage import FileSystemStorage

from .models import Product, Brand, Category
from .forms import ProductForm

class ProductFeaturedListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductFeaturedDetailView(generic.DetailView):
    template_name = 'products/product_featured-detail.html'
    context_object_name = 'product'

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Product.objects.all().featured


class ProductListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.order_by('-bidding_date')

class ProductDetailSlugView(generic.DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

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

class ProductDetailView(generic.DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        return Product.objects.filter(pk=pk)

        
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
def product_search(request):
    search = request.GET.get('search','')
    products = Product.objects.filter(product__exact=search)
    return render(request, 'shop/product_list.html', {'products':products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product':product})

@login_required
def product_upload(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/product_upload.html', {'form':form})