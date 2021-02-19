from django import forms

from .models import Post, Comment, TestImages

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)

class TestImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = TestImages
        fields = ('image', )