from django import forms
from .models import TipoPokemon, Ovo, Box, Especie


class TipoPokemonForm(forms.ModelForm):
    class Meta:
        model = TipoPokemon
        fields = ('name', 'base_generation_value')
        widgets = {
            'base_generation_value': forms.Select(choices=[
                (20, 'S Tier (20)'),
                (15, 'A Tier (15)'),
                (10, 'B Tier (10)'),
                (5, 'C Tier (5)'),
            ]),
        }
        labels = {
            'name': 'Nome do Tipo',
            'base_generation_value': 'Valor Base de Geração',
        }
        help_texts = {
            'base_generation_value': 'S Tier (20), A Tier (15), B Tier (10), C Tier (5)',
        }

class OvoForm(forms.ModelForm):
    class Meta:
        model = Ovo
        fields = ('name', 'type', 'species', 'price')
        labels = {
            'name': 'Nome do Ovo',
            'type': 'Tipo Pokémon',
            'species': 'Espécies',
            'price': 'Preço',
        }
    
    def __init__(self, *args, **kwargs):
        perfil_treinador = kwargs.pop('perfil_treinador', None)
        super().__init__(*args, **kwargs)
        self.perfil_treinador = perfil_treinador
