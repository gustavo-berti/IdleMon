from django.urls import path

from .views import (
    ConfiguracaoView,
    CotaUsuarioView,
    MeuConsumoView,
    RequisicoesView,
    TestarConexaoView,
    UsuariosIAView,
)

app_name = "ia"

urlpatterns = [
    path("requisicoes/", RequisicoesView.as_view(), name="requisicoes"),
    path("configuracao/", ConfiguracaoView.as_view(), name="configuracao"),
    path("configuracao/testar/", TestarConexaoView.as_view(), name="testar_conexao"),
    path("usuarios/", UsuariosIAView.as_view(), name="usuarios"),
    path("usuarios/<int:pk>/cota/", CotaUsuarioView.as_view(), name="cota_usuario"),
    path("meu-consumo/", MeuConsumoView.as_view(), name="meu_consumo"),
]
