import django_filters

from .models import Ovo, OvoInventario, TipoPokemon

TIER_CHOICES = [
    (20, 'S Tier (20)'),
    (15, 'A Tier (15)'),
    (10, 'B Tier (10)'),
    (5, 'C Tier (5)'),
]


class TipoPokemonFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    base_generation_value = django_filters.ChoiceFilter(choices=TIER_CHOICES, label='Tier', empty_label='Todas')

    class Meta:
        model = TipoPokemon
        fields = ('name', 'base_generation_value')


class OvoFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    type = django_filters.ModelChoiceFilter(
        queryset=TipoPokemon.objects.order_by('name'),
        label='Tipo',
        empty_label='Todos',
    )
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Preço máximo')

    class Meta:
        model = Ovo
        fields = ('name', 'type', 'price_max')


class OvoInventarioFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='ovo__name', lookup_expr='icontains', label='Nome do ovo')
    tipo = django_filters.ModelChoiceFilter(
        field_name='ovo__type',
        queryset=TipoPokemon.objects.order_by('name'),
        label='Tipo',
        empty_label='Todos',
    )

    class Meta:
        model = OvoInventario
        fields = ('nome', 'tipo')
