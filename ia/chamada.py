"""Único caminho para chamar a IA no projeto: chamar_ia().

    resposta = chamar_ia(
        finalidade="chatbot_resposta", usuario=request.user, origem="site",
        versao_prompt="chatbot-1",
        montar_pedido=lambda config: PedidoIA(instrucoes=..., texto=...),
    )

Faz, nesta ordem: confere se a IA está ativa e a cota, monta o pedido, chama o provedor com retentativas,
registra a RequisicaoIA e devolve a RespostaIA. Levanta CotaExcedida, IaIndisponivel ou ErroIA.
"""

import logging
import time

from .config import carregar_config
from .cota import dono_da_cota, verificar_cota
from .excecoes import CotaExcedida, ErroIA, IaIndisponivel
from .models import RequisicaoIA
from .provedores.base import MensagemHistorico, PedidoIA, RespostaIA

__all__ = [
    "chamar_ia",
    "PedidoIA",
    "MensagemHistorico",
    "RespostaIA",
    "CotaExcedida",
    "IaIndisponivel",
    "ErroIA",
]

logger = logging.getLogger(__name__)


def _obter_provedor(config):
    if config.provedor == "gemini":
        from .provedores.gemini import ProvedorGemini

        return ProvedorGemini()
    if config.provedor == "falso":
        from .provedores.falso import ProvedorFalso

        return ProvedorFalso()
    raise ErroIA(f"Provedor de IA desconhecido: {config.provedor!r}.")


def _registrar(config, usuario, finalidade, origem, versao_prompt, status, tentativas, inicio, resposta=None, erro=""):
    RequisicaoIA.objects.create(
        usuario=usuario,
        finalidade=finalidade,
        origem=origem,
        versao_prompt=versao_prompt,
        provedor=config.provedor,
        modelo=config.modelo,
        status=status,
        tentativas=tentativas,
        tokens_entrada=resposta.tokens_entrada if resposta else 0,
        tokens_saida=resposta.tokens_saida if resposta else 0,
        tokens_total=resposta.tokens_total if resposta else 0,
        duracao_ms=int((time.monotonic() - inicio) * 1000),
        erro=erro[:300],
    )


def chamar_ia(*, finalidade, usuario, origem, versao_prompt, montar_pedido):
    config = carregar_config()
    inicio = time.monotonic()
    dados = (config, usuario, finalidade, origem, versao_prompt)

    if not config.ativa:
        _registrar(*dados, RequisicaoIA.ERRO, 0, inicio, erro="IA desativada na configuração.")
        raise ErroIA("A IA está desativada na configuração.")

    try:
        verificar_cota(dono_da_cota(usuario))
    except CotaExcedida:
        _registrar(*dados, RequisicaoIA.COTA_EXCEDIDA, 0, inicio, erro="Cota mensal esgotada.")
        raise

    pedido = montar_pedido(config)
    provedor = _obter_provedor(config)

    tentativas = 0
    while True:
        tentativas += 1
        try:
            resposta = provedor.gerar(pedido, config)
            break
        except IaIndisponivel as exc:
            if tentativas >= config.tentativas:
                logger.warning("IA indisponível em %s após %s tentativa(s): %s", finalidade, tentativas, exc)
                _registrar(*dados, RequisicaoIA.ERRO, tentativas, inicio, erro=str(exc))
                raise
            time.sleep(config.espera_segundos * 2 ** (tentativas - 1))
        except ErroIA as exc:
            logger.error("Erro de IA em %s: %s", finalidade, exc)
            _registrar(*dados, RequisicaoIA.ERRO, tentativas, inicio, erro=str(exc))
            raise
        except Exception as exc:
            logger.exception("Erro inesperado do provedor de IA em %s", finalidade)
            _registrar(*dados, RequisicaoIA.ERRO, tentativas, inicio, erro=type(exc).__name__)
            raise ErroIA("Erro inesperado ao chamar a IA.") from exc

    _registrar(*dados, RequisicaoIA.SUCESSO, tentativas, inicio, resposta=resposta)
    return resposta
