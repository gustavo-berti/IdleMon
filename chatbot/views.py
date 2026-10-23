import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from ia.cota import CotaExcedida, dono_da_cota, situacao_da_cota

from .models import MensagemChat
from .services import responder

logger = logging.getLogger(__name__)

MENSAGEM_INDISPONIVEL = "O assistente está indisponível no momento. Tente novamente em instantes."


def _cota_do(usuario):
    return situacao_da_cota(dono_da_cota(usuario)).como_dict()


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "chatbot/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mensagens"] = MensagemChat.objects.filter(usuario=self.request.user)
        context["cota"] = _cota_do(self.request.user)
        return context


class EnviarView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        try:
            dados = json.loads(request.body)
            mensagem = dados["mensagem"]
            if not isinstance(mensagem, str):
                raise TypeError
        except (ValueError, KeyError, TypeError):
            return self._erro("Não foi possível entender o envio. Tente novamente.", 400)

        try:
            resposta = responder(request.user, mensagem)
        except ValueError as exc:
            return self._erro(str(exc), 400)
        except CotaExcedida as exc:
            return self._erro(exc.mensagem_esgotada(), 429)
        except Exception:
            logger.exception("Falha ao responder no chatbot (usuário %s)", request.user.pk)
            return self._erro(MENSAGEM_INDISPONIVEL, 503)

        return JsonResponse({"sucesso": True, "resposta": resposta.texto, "cota": _cota_do(request.user)})

    @staticmethod
    def _erro(mensagem, status):
        return JsonResponse({"sucesso": False, "erro": mensagem}, status=status)


class LimparView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        MensagemChat.objects.filter(usuario=request.user).delete()
        messages.success(request, "Conversa apagada.")
        return redirect("chatbot:chat")
