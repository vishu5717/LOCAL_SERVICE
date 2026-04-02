from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','role','password1','password2','first_name','last_name','mobile_number','gender']

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

