from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    AccountDeleteView,
    AccountDetailView,
    AccountUpdateView,
    LoginView,
    RegisterView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('account/', AccountDetailView.as_view(), name='account_detail'),
    path('account/edit/', AccountUpdateView.as_view(), name='account_update'),
    path('account/delete/', AccountDeleteView.as_view(), name='account_delete'),
]