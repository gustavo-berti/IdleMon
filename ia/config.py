from dataclasses import dataclass

from django.conf import settings

from .models import ConfiguracaoIA


@dataclass(frozen=True)
class ConfigIA:
    """Configuração lida a cada chamada: a salva em tela (ConfiguracaoIA) ou, sem ela, a do settings
    (assim override_settings funciona nos testes)."""

    ativa: bool
    provedor: str
    modelo: str
    chave_api: str
    timeout_segundos: int
    tentativas: int
    espera_segundos: float
    max_tokens_saida: int
    temperatura: float
    cota_mensal_tokens: int
    cota_alerta_percentual: int


def carregar_config():
    salva = ConfiguracaoIA.carregar()
    return ConfigIA(
        ativa=salva.ativa,
        provedor=salva.provedor,
        modelo=salva.modelo,
        chave_api=settings.IA_CHAVE_API,
        timeout_segundos=salva.timeout_segundos,
        tentativas=max(1, salva.tentativas),
        espera_segundos=salva.espera_retentativa_segundos,
        max_tokens_saida=salva.max_tokens_saida,
        temperatura=salva.temperatura,
        cota_mensal_tokens=salva.cota_mensal_tokens,
        cota_alerta_percentual=salva.cota_alerta_percentual,
    )
