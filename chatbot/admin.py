from django.contrib import admin

from .models import MensagemChat


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "usuario", "papel", "conteudo")
    list_filter = ("papel",)
    search_fields = ("usuario__username", "conteudo")
    date_hierarchy = "criado_em"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
