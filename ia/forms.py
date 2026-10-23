from django import forms

from .models import ConfiguracaoIA


class ConfiguracaoIAForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoIA
        fields = (
            "ativa",
            "provedor",
            "modelo",
            "timeout_segundos",
            "tentativas",
            "espera_retentativa_segundos",
            "max_tokens_saida",
            "temperatura",
            "cota_mensal_tokens",
            "cota_alerta_percentual",
        )
        widgets = {
            # Texto (e não number) para a máscara do jQuery Mask funcionar
            "cota_mensal_tokens": forms.TextInput(attrs={"class": "mascara-inteiro", "inputmode": "numeric"}),
            "max_tokens_saida": forms.TextInput(attrs={"class": "mascara-inteiro", "inputmode": "numeric"}),
        }


class CotaUsuarioForm(forms.Form):
    limite_mensal_tokens = forms.IntegerField(
        label="Limite mensal (tokens)",
        min_value=0,
        required=False,
        widget=forms.TextInput(attrs={"class": "mascara-inteiro", "inputmode": "numeric"}),
    )

    def __init__(self, *args, cota_padrao, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["limite_mensal_tokens"].help_text = (
            f"Deixe em branco para usar a cota padrão ({cota_padrao} tokens). 0 bloqueia a IA para este usuário."
        )
