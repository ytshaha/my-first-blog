from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required 
def staff_home(request):
    return render(request, "staff/home.html", {})


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


def upload_product_with_excel(request):
    pass