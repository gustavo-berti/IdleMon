from django import forms
from django.db.models import Count, F, Q
from .models import MAX_ACTIVE_TEAM, TipoPokemon, Ovo, Box, PokemonInstancia


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
        widgets = {
            # Texto (e não number) para a máscara do jQuery Mask funcionar
            'price': forms.TextInput(attrs={'class': 'mascara-preco', 'placeholder': '0.00', 'inputmode': 'decimal'}),
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


class PokemonInstanciaForm(forms.ModelForm):
    class Meta:
        model = PokemonInstancia
        fields = ('nickname', 'box', 'is_active_team')
        labels = {
            'nickname': 'Apelido',
            'box': 'Box',
            'is_active_team': 'Na Equipe Ativa (gerando moedas)',
        }
        help_texts = {
            'box': 'Mudar de box coloca o Pokémon na primeira vaga livre da box escolhida.',
            'is_active_team': f'A equipe comporta até {MAX_ACTIVE_TEAM} Pokémons.',
        }

    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil')
        super().__init__(*args, **kwargs)
        self.perfil = perfil
        self.fields['box'].empty_label = None
        # Boxes do próprio treinador com vaga, mais a box atual do Pokémon
        self.fields['box'].queryset = (
            Box.objects
            .filter(trainer_profile=perfil)
            .annotate(uso=Count('pokemon_instances'))
            .filter(Q(uso__lt=F('slots_max')) | Q(pk=self.instance.box_id))
            .order_by('name')
        )

    def clean_is_active_team(self):
        is_active_team = self.cleaned_data['is_active_team']
        if is_active_team and not self.instance.is_active_team:
            em_equipe = PokemonInstancia.objects.filter(
                box__trainer_profile=self.perfil, is_active_team=True
            ).count()
            if em_equipe >= MAX_ACTIVE_TEAM:
                raise forms.ValidationError(
                    f'Sua Equipe Ativa já tem {MAX_ACTIVE_TEAM} Pokémons. Retire um antes de adicionar outro.'
                )
        return is_active_team