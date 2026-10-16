from django.urls import path

from .views import ChatView, EnviarView, LimparView

app_name = "chatbot"

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("enviar/", EnviarView.as_view(), name="enviar"),
    path("limpar/", LimparView.as_view(), name="limpar"),
]
