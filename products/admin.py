from django.contrib import admin

from .models import Product, Brand, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')

    class Meta:
        model = Product

admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Category)
