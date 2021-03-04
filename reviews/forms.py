from django import forms

from .models import Review, Comment, ReviewImages

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('title', 'rating', 'product_item', 'text',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('user', 'review', 'text',)

class ReviewImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ReviewImages
        fields = ('image', )