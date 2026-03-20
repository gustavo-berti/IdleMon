from django.contrib import admin

from .models import Box, Especie, Ovo, PokemonInstancia, TipoPokemon


@admin.register(TipoPokemon)
class TipoPokemonAdmin(admin.ModelAdmin):
	list_display = ("id", "nome", "valor_base_geracao")
	search_fields = ("nome",)


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
	list_display = ("id", "nome", "estagio_evolucao")
	search_fields = ("nome",)
	filter_horizontal = ("tipos",)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
	list_display = ("id", "nome", "perfil_treinador", "slots_max")
	search_fields = ("nome", "perfil_treinador__user__username")


@admin.register(PokemonInstancia)
class PokemonInstanciaAdmin(admin.ModelAdmin):
	list_display = ("id", "apelido", "especie", "box", "data_nascimento")
	search_fields = ("apelido", "especie__nome", "box__nome")


@admin.register(Ovo)
class OvoAdmin(admin.ModelAdmin):
	list_display = ("id", "nome", "perfil_treinador", "tipo", "especie", "preco")
	search_fields = ("nome", "perfil_treinador__user__username", "especie__nome", "tipo__nome")
