from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, UpdateView
from .forms import AccountPasswordChangeForm, AccountUpdateForm, LoginForm, RegisterForm

User = get_user_model()

class LoginView(FormView):
    template_name = 'accounts/form.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')
    extra_context = {
        'form_action': 'login',
        'form_title': 'Entrar',
        'submit_label': 'Entrar',
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)
    
class RegisterView(FormView):
    template_name = 'accounts/form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')
    extra_context = {
        'form_action': 'register',
        'form_title': 'Formulário de Cadastro',
        'submit_label': 'Registrar',
    }

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/account_detail.html'
    context_object_name = 'account'

    def get_object(self, queryset=None):
        return self.request.user


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountUpdateForm
    template_name = 'accounts/form.html'
    success_url = reverse_lazy('account_detail')
    extra_context = {
        'form_action': 'account_update',
        'form_title': 'Atualizar Conta',
        'submit_label': 'Salvar Alterações',
    }

    def get_object(self, queryset=None):
        return self.request.user


class AccountPasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    form_class = AccountPasswordChangeForm
    template_name = 'accounts/form.html'
    success_url = reverse_lazy('account_detail')
    extra_context = {
        'form_action': 'account_password_change',
        'form_title': 'Alterar Senha',
        'submit_label': 'Alterar Senha',
    }


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('home')
    extra_context = {
        'form_title': 'Excluir Conta',
        'submit_label': 'Excluir Conta',
    }

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        logout(self.request)
        return super().form_valid(form)