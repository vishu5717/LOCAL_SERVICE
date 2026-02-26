from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'role', 'password1', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'role': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())