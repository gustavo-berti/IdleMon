from django import forms
from django.db.models import Count, F
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
        fields = ('name', 'type', 'price')
        labels = {
            'name': 'Nome do Ovo',
            'type': 'Tipo Pokémon',
            'price': 'Preço',
        }
        help_texts = {
            'type': 'As espécies serão automaticamente adicionadas baseadas no tipo selecionado',
        }
    
    def __init__(self, *args, **kwargs):
        perfil_treinador = kwargs.pop('perfil_treinador', None)
        super().__init__(*args, **kwargs)
        self.perfil_treinador = perfil_treinador

class ChocarOvoForm(forms.Form):
    box = forms.ModelChoiceField(
        queryset=Box.objects.none(),
        label='Box de Destino',
        help_text='Apenas boxes com espaço disponível são listadas.',
        empty_label='--- Selecione uma Box ---',
    )
    nickname = forms.CharField(
        max_length=80,
        label='Apelido',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Deixe em branco para usar o nome da espécie'}),
    )

    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil')
        super().__init__(*args, **kwargs)
        self.fields['box'].queryset = (
            Box.objects
            .filter(trainer_profile=perfil)
            .annotate(uso=Count('pokemon_instances'))
            .filter(uso__lt=F('slots_max'))
            .order_by('name')
        )


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ('name',)
        labels = {
            'name': 'Nome da Box',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Box Principal'}),
        }