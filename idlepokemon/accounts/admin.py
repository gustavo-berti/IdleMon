from django.contrib import admin

from .models import PerfilTreinador


@admin.register(PerfilTreinador)
class PerfilTreinadorAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "saldo_moedas")
	search_fields = ("user__username", "user__email")
