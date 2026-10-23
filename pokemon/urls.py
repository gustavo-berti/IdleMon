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
    BoxListView,
    BoxDetailView,
    BoxCreateView,
    BoxUpdateView,
    BoxDeleteView,
    LojaOvosView,
    ComprarOvoView,
    MeusOvosView,
    ChocarOvoView,
    DescartarOvoView,
    UpdatePokemonPositionView,
    PokemonDetailView,
    PokemonUpdateView,
    PokemonDeleteView,
    PokemonEquipeView,
    ColetarRendimentoView,
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
    
    # User - Box
    path('boxes/', BoxListView.as_view(), name='box_list'),
    path('boxes/<int:pk>/', BoxDetailView.as_view(), name='box_detail'),
    path('boxes/nova/', BoxCreateView.as_view(), name='box_create'),
    path('boxes/<int:pk>/editar/', BoxUpdateView.as_view(), name='box_update'),
    path('boxes/<int:pk>/excluir/', BoxDeleteView.as_view(), name='box_delete'),
    
    # User - Loja de Ovos
    path('loja/', LojaOvosView.as_view(), name='loja_ovos'),
    path('loja/<int:pk>/', ComprarOvoView.as_view(), name='comprar_ovo'),
    path('meus-ovos/', MeusOvosView.as_view(), name='meus_ovos'),
    path('meus-ovos/<int:pk>/chocar/', ChocarOvoView.as_view(), name='chocar_ovo'),
    path('meus-ovos/<int:pk>/descartar/', DescartarOvoView.as_view(), name='descartar_ovo'),
    path('posicao/', UpdatePokemonPositionView.as_view(), name='update_pokemon_position'),

    # User - Pokémon e Equipe Ativa
    path('pokemons/<int:pk>/', PokemonDetailView.as_view(), name='pokemon_detail'),
    path('pokemons/<int:pk>/editar/', PokemonUpdateView.as_view(), name='pokemon_update'),
    path('pokemons/<int:pk>/libertar/', PokemonDeleteView.as_view(), name='pokemon_delete'),
    path('pokemons/<int:pk>/equipe/', PokemonEquipeView.as_view(), name='pokemon_equipe'),
    path('equipe/coletar/', ColetarRendimentoView.as_view(), name='coletar_rendimento'),
]