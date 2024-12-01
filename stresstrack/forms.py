from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Andy',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Apolo',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    dni = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1103982731',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'ejemplo@unl.edu.ec',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '**********',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '**********',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'dni', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'ejemplo@unl.edu.ec',
        'class': 'field fs-6 p-2 border border-2 border-dark rounded-4'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '**********',
        'class': 'field fs-7 p-2 border border-2 border-dark rounded-4'
    }))