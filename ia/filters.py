import django_filters
from django import forms
from django.contrib.auth import get_user_model

from .models import RequisicaoIA

User = get_user_model()


class RequisicaoIAFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(field_name="usuario__username", lookup_expr="icontains", label="Usuário")
    finalidade = django_filters.CharFilter(lookup_expr="icontains", label="Finalidade")
    status = django_filters.ChoiceFilter(choices=RequisicaoIA.STATUS_CHOICES, label="Status", empty_label="Todos")
    desde = django_filters.DateFilter(
        field_name="criado_em", lookup_expr="date__gte", label="Desde",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    ate = django_filters.DateFilter(
        field_name="criado_em", lookup_expr="date__lte", label="Até",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = RequisicaoIA
        fields = ("usuario", "finalidade", "status", "desde", "ate")


class UsuarioIAFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains", label="Usuário")

    class Meta:
        model = User
        fields = ("username",)
