from django.urls import path
from .views import (
    TipoPokemonListView,
    TipoPokemonCreateView,
    TipoPokemonUpdateView,
    TipoPokemonDeleteView,
)

urlpatterns = [
    # Admin - TipoPokemon
    path('admin/tipos/', TipoPokemonListView.as_view(), name='tipopokemon_list'),
    path('admin/tipos/novo/', TipoPokemonCreateView.as_view(), name='tipopokemon_create'),
    path('admin/tipos/<int:pk>/editar/', TipoPokemonUpdateView.as_view(), name='tipopokemon_update'),
    path('admin/tipos/<int:pk>/excluir/', TipoPokemonDeleteView.as_view(), name='tipopokemon_delete'),
]
