from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import Http404
# from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView

# from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils import timezone

# from mysite.mixin import StaffRequiredView
from products.models import Product #, ProductItem, Brand, Category, ProductImage
from biddings.models import Bidding
# from orders.models import Order
from .forms import ReviewForm, CommentForm, ReviewImageForm
from .models import Review, Comment, ReviewImage
from biddings.forms import BiddingForm
from carts.models import Cart, CartItem
from points.models import Point

class ReviewListView(LoginRequiredMixin, generic.ListView):
    '''
    Featured = True이고 product_type= Noraml인 물품들을 표시함.(active와 다른 개념. active는 구매가능여부.)
    '''
    template_name = 'reviews/home.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super(ReviewListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        review_qs = Review.objects.all()
        return review_qs.order_by('-created_date')

class ReviewUploadView(generic.CreateView):
    form_class = ReviewForm
    template_name = 'reviews/upload.html'
    success_url = reverse_lazy('reviews:home')
    
    def get_context_data(self, *args, **kwargs):
        context = super(ReviewUploadView, self).get_context_data(*args, **kwargs)
        
        request = self.request
        post_purpose = request.POST.get('post_purpose', None)
        cart_item_id = request.POST.get('cart_item_id', None)
        cart_item_qs = CartItem.objects.filter(id=cart_item_id)
        if cart_item_qs.count() == 1:
            cart_item_obj = cart_item_qs.first()
        else:
            return None
        context['cart_item'] = cart_item_obj
        return context

    

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        cart_item_id = self.request.POST.get('cart_item_id', None)
        cart_item_qs = CartItem.objects.filter(id=cart_item_id)
        if cart_item_qs.count() == 1:
            cart_item_obj = cart_item_qs.first()

        form.instance.user = self.request.user
        form.instance.cart_item = cart_item_obj
        form.instance.save()
        print('form.instance.image1',type(form.instance.image1))
        if form.instance.image1:
            Point.objects.new(user=self.request.user, amount=2000, details='포토리뷰 작성을 통한 +2000포인트적립')
            messages.success(self.request, '포토리뷰 작성을 통해 2000포인트 적립되었습니다.')
        else:
            Point.objects.new(user=self.request.user, amount=1000, details='리뷰 작성을 통한 +1000포인트적립')
            messages.success(self.arequest, '리뷰 작성을 통해 1000포인트 적립되었습니다.')
        cart_item_obj.is_reviewed = True
        cart_item_obj.save()
        return super().form_valid(form)

# def upload_review(request):
#     # ImageFormSet이 멀티이미지 업로드를 가능하게 해줌. extra는 업로드가능개수. 폼이 완성된 갯수만큼만 업로드 하므로 안심.
#     ImageFormSet = modelformset_factory(ReviewImage, form=ReviewImageForm, extra=10)
#     if request.method == 'POST':
#         reviewform = ReviewForm(request.POST, request.FILES)
#         formset = ImageFormSet(request.POST, request.FILES, queryset=ReviewImage.objects.none())

#         if reviewform.is_valid() and formset.is_valid():
#             new_review = reviewform.save(commit=False) # 비딩용 product -> 이미지연결
#             new_review.user = request.user
            
#             new_review.save()
#             print("Review가 저장되었다.")
#             for form in formset.cleaned_data:
#                 if form:
#                     image = form['image']
#                     photo = ReviewImage(review=new_review, image=image)
#                     photo.save()
#                     print("사진이 저장되었다.")
#             messages.success(request, "업로드완료")
#             print("Review images가 저장되었다.")
#             return redirect('reviews:home')
#     else:
#         reviewform = ReviewForm()
#         formset = ImageFormSet(queryset=ReviewImage.objects.none())
#     return render(request, 'reviews/upload_review.html', {'reviewform': reviewform, 'formset': formset})




class ReviewDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'reviews/detail.html'
    context_object_name = 'review'

    def get_context_data(self, *args, **kwargs):
        context = super(ReviewDetailView, self).get_context_data(*args, **kwargs)
        # review_obj = get_object_or_404(Review, pk=pk)
        review_obj = context['review']

        comments_qs = Comment.objects.filter(review=review_obj)
        context['comments'] = comments_qs
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = get_object_or_404(Review, pk=pk) #, active=True)
        return instance

class ReviewEditView(UpdateView):
    form_class = ReviewForm
    model = Review
    # fields = ['title','text', 'image1', 'image2', 'image3', 'image4', 'image5']
    template_name = 'reviews/update.html'
    context_object_name = 'review'


    def get_success_url(self):
        return reverse('reviews:detail', args=(self.object.pk,))

class ReviewRemoveView(DeleteView):
    model = Review
    fields = ['title','text']

    def get_success_url(self):
        return reverse('reviews:home')




@login_required
def add_comment_to_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()
            return redirect('reviews:detail', pk=review.pk)
    else:
        form = CommentForm()
    return render(request, 'reviews/comment_add_review.html', {'form':form})

@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

class CommentEditView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'reviews/comment_edit_review.html'

    def get_success_url(self):
        return reverse('reviews:detail', args=(self.object.review.pk,))

class CommentRemoveView(DeleteView):
    model = Comment
    fields = ['text']

    def get_success_url(self):
        return reverse('reviews:detail', args=(self.object.review.pk,))


    # def get_object(self, *args, **kwargs):
    #     request = self.request
    #     slug = self.kwargs.get('slug')
    #     instance = get_object_or_404(ProductItem, slug=slug, active=True)
    #     try:
    #         instance = ProductItem.objects.get(slug=slug, active=True)
    #     except ProductItem.DoesNotExist:
    #         raise Http404("Not found..")
    #     except ProductItem.MultipleObjectsReturned:
    #         qs = ProductItem.objects.filter(slug=slug, active=True)
    #         instance = qs.first()
    #     except:
    #         raise Http404("Uhmmmmm")
    #     return instance

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