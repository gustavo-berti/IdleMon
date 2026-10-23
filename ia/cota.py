"""Cota mensal de tokens. O consumo é a soma dos tokens das requisições bem-sucedidas do mês.

O limite é o próprio do usuário (CotaUsuarioIA, tela "IA por usuário") ou a cota padrão da configuração.
"""

from dataclasses import dataclass

from django.db.models import Sum
from django.utils import timezone

from .config import carregar_config
from .excecoes import CotaExcedida
from .models import CotaUsuarioIA, RequisicaoIA

__all__ = [
    "CotaExcedida",
    "SituacaoCota",
    "dono_da_cota",
    "inicio_do_mes",
    "limite_do",
    "situacao_da_cota",
    "verificar_cota",
    "mensagem_esgotada",
]


@dataclass(frozen=True)
class SituacaoCota:
    usado: int
    limite: int
    alerta_percentual: int

    @property
    def percentual(self):
        if self.limite <= 0:
            return 100
        return min(100, int(self.usado * 100 / self.limite))

    @property
    def em_alerta(self):
        return self.percentual >= self.alerta_percentual

    @property
    def esgotada(self):
        return self.usado >= self.limite

    def como_dict(self):
        return {
            "usado": self.usado,
            "limite": self.limite,
            "percentual": self.percentual,
            "em_alerta": self.em_alerta,
        }


def dono_da_cota(usuario):
    """Quem paga a cota de uma chamada. Hoje é o próprio usuário."""
    return usuario


def inicio_do_mes():
    agora = timezone.localtime()
    return agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def limite_do(dono, config=None):
    """Limite mensal do dono: o próprio, se houver, senão a cota padrão."""
    config = config or carregar_config()
    proprio = CotaUsuarioIA.objects.filter(usuario=dono).values_list("limite_mensal_tokens", flat=True).first()
    return config.cota_mensal_tokens if proprio is None else proprio


def situacao_da_cota(dono):
    config = carregar_config()
    usado = (
        RequisicaoIA.objects.filter(
            usuario=dono,
            status=RequisicaoIA.SUCESSO,
            criado_em__gte=inicio_do_mes(),
        ).aggregate(total=Sum("tokens_total"))["total"]
        or 0
    )
    return SituacaoCota(
        usado=usado,
        limite=limite_do(dono, config),
        alerta_percentual=config.cota_alerta_percentual,
    )


def verificar_cota(dono):
    """Devolve a situação da cota ou levanta CotaExcedida se ela já acabou."""
    situacao = situacao_da_cota(dono)
    if situacao.esgotada:
        raise CotaExcedida()
    return situacao


def mensagem_esgotada():
    return (
        "Você usou todo o limite de IA deste mês. "
        "O assistente volta a responder no início do próximo mês."
    )
