from django.contrib import admin

from .models import Product, ProductItem, Brand, Category, ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')

    class Meta:
        model = Product

admin.site.register(Product)
admin.site.register(ProductItem)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ProductImage)
