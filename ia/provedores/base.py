"""Contrato entre o app ia e os provedores de IA."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MensagemHistorico:
    papel: str  # "user" ou "model"
    conteudo: str


@dataclass(frozen=True)
class PedidoIA:
    instrucoes: str
    texto: str
    historico: tuple = field(default_factory=tuple)  # tuple[MensagemHistorico], do mais antigo ao mais novo


@dataclass(frozen=True)
class RespostaIA:
    texto: str
    tokens_entrada: int = 0
    tokens_saida: int = 0

    @property
    def tokens_total(self):
        return self.tokens_entrada + self.tokens_saida


class ProvedorBase:
    """Um provedor recebe um PedidoIA e devolve uma RespostaIA.

    Deve levantar IaIndisponivel para falhas temporárias (serão repetidas) e
    ErroIA para as demais. Não conhece cota, registro nem retentativa.
    """

    nome = "base"

    def gerar(self, pedido, config):
        raise NotImplementedError
