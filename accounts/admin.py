from django.contrib import admin

from .models import PerfilTreinador


@admin.register(PerfilTreinador)
class PerfilTreinadorAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "coin_balance")
	search_fields = ("user__username", "user__email")
