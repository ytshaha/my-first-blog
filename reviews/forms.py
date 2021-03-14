from django import forms

from .models import Review, Comment, ReviewImage

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('title', 'rating', 'text', 
                  'image1', 'image2', 'image3', 'image4', 'image5',)
        widgets = {'title': forms.TextInput(attrs={'class':'form-control',}),
                   'rating': forms.Select(attrs={'class':'form-control',}),
                #    'product_item': forms.Select(attrs={'class':'form-control',}),
                   'text': forms.Textarea(attrs={'rows':6, 'cols':22,'class':'form-control',}),
        
        }


class CommentForm(forms.ModelForm):
    # text = forms.CharField(label='댓글작성')
    text = forms.CharField(label='댓글작성', max_length=200, required=True, widget=forms.Textarea(attrs={'rows':6, 'cols':22,'class':'form-control',}))
    
    class Meta:
        model = Comment
        fields = ('text',)
        # widgets = {'text': forms.Textarea(label='댓글작성', attrs={'rows':6, 'cols':22,'class':'form-control',}),
        # }
class ReviewImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ReviewImage
        fields = ('image', )