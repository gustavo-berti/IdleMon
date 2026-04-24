from django.urls import path
from .views import (
    TipoPokemonListView,
    TipoPokemonCreateView,
    TipoPokemonUpdateView,
    TipoPokemonDeleteView,
    OvoListView,
    OvoCreateView,
    OvoUpdateView,
    OvoDeleteView,
)

urlpatterns = [
    # Admin - TipoPokemon
    path('admin/tipos/', TipoPokemonListView.as_view(), name='tipopokemon_list'),
    path('admin/tipos/novo/', TipoPokemonCreateView.as_view(), name='tipopokemon_create'),
    path('admin/tipos/<int:pk>/editar/', TipoPokemonUpdateView.as_view(), name='tipopokemon_update'),
    path('admin/tipos/<int:pk>/excluir/', TipoPokemonDeleteView.as_view(), name='tipopokemon_delete'),
    
    # Admin - Ovo
    path('admin/ovos/', OvoListView.as_view(), name='ovo_list'),
    path('admin/ovos/novo/', OvoCreateView.as_view(), name='ovo_create'),
    path('admin/ovos/<int:pk>/editar/', OvoUpdateView.as_view(), name='ovo_update'),
    path('admin/ovos/<int:pk>/excluir/', OvoDeleteView.as_view(), name='ovo_delete'),
]
