"""Exceções do app ia. Quem chama a IA só precisa conhecer estas."""


class ErroIA(Exception):
    """Falha da IA que não adianta repetir (chave inválida, pedido recusado, resposta vazia...)."""


class IaIndisponivel(ErroIA):
    """Falha temporária (rede, tempo esgotado, limite do provedor, erro 5xx). Pode ser repetida."""


class CotaExcedida(Exception):
    """A cota mensal de tokens de quem pediu já foi usada por inteiro."""

    def mensagem_esgotada(self):
        from .cota import mensagem_esgotada

        return mensagem_esgotada()
