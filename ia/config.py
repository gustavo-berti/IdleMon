from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class ConfigIA:
    """Configuração lida de settings a cada chamada (assim override_settings funciona nos testes)."""

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
    return ConfigIA(
        provedor=settings.IA_PROVEDOR,
        modelo=settings.IA_MODELO,
        chave_api=settings.IA_CHAVE_API,
        timeout_segundos=settings.IA_TIMEOUT_SEGUNDOS,
        tentativas=max(1, settings.IA_TENTATIVAS),
        espera_segundos=settings.IA_ESPERA_RETENTATIVA_SEGUNDOS,
        max_tokens_saida=settings.IA_MAX_TOKENS_SAIDA,
        temperatura=settings.IA_TEMPERATURA,
        cota_mensal_tokens=settings.IA_COTA_MENSAL_TOKENS,
        cota_alerta_percentual=settings.IA_COTA_ALERTA_PERCENTUAL,
    )
