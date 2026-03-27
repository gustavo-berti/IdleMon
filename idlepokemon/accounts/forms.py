from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Nome de Usuário', max_length=150, required=True)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=True)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nome de Usuário',
            'password1': 'Senha',
            'password2': 'Confirmar Senha',
        }


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        labels = {
            'username': 'Nome de Usuário',
            'email': 'Email',
        }
