from django.contrib import admin

from .models import Box, Especie, Ovo, PokemonInstancia, TipoPokemon


@admin.register(TipoPokemon)
class TipoPokemonAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "base_generation_value")
	search_fields = ("name",)


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "evolution_stage")
	search_fields = ("name",)
	filter_horizontal = ("types",)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "trainer_profile", "slots_max")
	search_fields = ("name", "trainer_profile__user__username")


@admin.register(PokemonInstancia)
class PokemonInstanciaAdmin(admin.ModelAdmin):
	list_display = ("id", "nickname", "species", "box", "birth_date")
	search_fields = ("nickname", "species__name", "box__name")


@admin.register(Ovo)
class OvoAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "trainer_profile", "type", "species", "price")
	search_fields = ("name", "trainer_profile__user__username", "species__name", "type__name")
