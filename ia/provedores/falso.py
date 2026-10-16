"""Provedor falso para testes e desenvolvimento sem internet (IA_PROVEDOR = "falso")."""

from .base import ProvedorBase, RespostaIA


class ProvedorFalso(ProvedorBase):
    nome = "falso"

    resposta = "Resposta de teste."
    tokens_entrada = 10
    tokens_saida = 5
    # Fila de erros: cada chamada consome o primeiro item (exceção ou None para dar sucesso).
    erros = []
    # Todos os PedidoIA recebidos, na ordem.
    pedidos = []

    @classmethod
    def reiniciar(cls):
        cls.resposta = "Resposta de teste."
        cls.tokens_entrada = 10
        cls.tokens_saida = 5
        cls.erros = []
        cls.pedidos = []

    def gerar(self, pedido, config):
        type(self).pedidos.append(pedido)
        if type(self).erros:
            erro = type(self).erros.pop(0)
            if erro is not None:
                raise erro
        return RespostaIA(
            texto=type(self).resposta,
            tokens_entrada=type(self).tokens_entrada,
            tokens_saida=type(self).tokens_saida,
        )
