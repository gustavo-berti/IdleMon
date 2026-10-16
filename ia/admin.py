from django.contrib import admin

from .models import RequisicaoIA


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "usuario",
        "finalidade",
        "status",
        "modelo",
        "tokens_total",
        "duracao_ms",
        "tentativas",
    )
    list_filter = ("finalidade", "status", "provedor", "origem")
    search_fields = ("usuario__username", "finalidade", "erro")
    date_hierarchy = "criado_em"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
