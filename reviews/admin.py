from django.contrib import admin

from .models import Review, Comment, ReviewImages
# Register your models here.
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(ReviewImages)
