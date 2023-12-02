from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post
class SignUpForm(UserCreationForm):
    # email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'tags', 'is_flagged']
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 800px;'}),     # Adjust width as needed
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 105}),  # Adjust rows and cols as needed
            'category': forms.RadioSelect(),
        }