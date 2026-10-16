from django.db import transaction

from ia.chamada import MensagemHistorico, PedidoIA, chamar_ia

from .instrucoes import VERSAO_PROMPT, montar_instrucoes
from .models import MensagemChat

LIMITE_PERGUNTA = 2000


def historico_recente(usuario, limite=6):
    """As últimas mensagens do usuário, da mais antiga para a mais nova."""
    recentes = MensagemChat.objects.filter(usuario=usuario).order_by("-criado_em", "-id")[:limite]
    return tuple(MensagemHistorico(m.papel, m.conteudo) for m in reversed(list(recentes)))


def responder(usuario, pergunta):
    """Pergunta à IA e, só se der certo, grava a pergunta e a resposta."""
    pergunta = (pergunta or "").strip()
    if not pergunta:
        raise ValueError("Digite uma pergunta antes de enviar.")
    if len(pergunta) > LIMITE_PERGUNTA:
        raise ValueError(f"A pergunta é muito longa. Use no máximo {LIMITE_PERGUNTA} caracteres.")

    resposta = chamar_ia(
        finalidade="chatbot_resposta",
        usuario=usuario,
        origem="site",
        versao_prompt=VERSAO_PROMPT,
        montar_pedido=lambda config: PedidoIA(
            instrucoes=montar_instrucoes(usuario),
            texto=pergunta,
            historico=historico_recente(usuario),
        ),
    )

    with transaction.atomic():
        MensagemChat.objects.create(usuario=usuario, papel=MensagemChat.PAPEL_USUARIO, conteudo=pergunta)
        MensagemChat.objects.create(usuario=usuario, papel=MensagemChat.PAPEL_ASSISTENTE, conteudo=resposta.texto)
    return resposta
