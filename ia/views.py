from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, UpdateView
from django_filters.views import FilterView

from .chamada import CotaExcedida, ErroIA, PedidoIA, chamar_ia
from .config import carregar_config
from .cota import dono_da_cota, inicio_do_mes, situacao_da_cota
from .filters import RequisicaoIAFilter, UsuarioIAFilter
from .forms import ConfiguracaoIAForm, CotaUsuarioForm
from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA

User = get_user_model()


class RequisicoesView(GroupRequiredMixin, FilterView):
    group_required = ["administradores"]
    model = RequisicaoIA
    filterset_class = RequisicaoIAFilter
    template_name = "ia/requisicoes.html"
    context_object_name = "requisicoes"
    paginate_by = 20

    def get_queryset(self):
        return RequisicaoIA.objects.select_related("usuario")


class ConfiguracaoView(GroupRequiredMixin, UpdateView):
    group_required = ["administradores"]
    model = ConfiguracaoIA
    form_class = ConfiguracaoIAForm
    template_name = "ia/configuracao.html"
    success_url = reverse_lazy("ia:configuracao")

    def get_object(self, queryset=None):
        return ConfiguracaoIA.carregar()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chave_configurada"] = bool(carregar_config().chave_api)
        context["salva"] = ConfiguracaoIA.objects.filter(pk=1).exists()
        return context

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        messages.success(self.request, "Configuração da IA salva. Ela já vale para as próximas chamadas.")
        return super().form_valid(form)


class TestarConexaoView(GroupRequiredMixin, View):
    group_required = ["administradores"]
    http_method_names = ["post"]

    def post(self, request):
        try:
            resposta = chamar_ia(
                finalidade="teste_conexao",
                usuario=request.user,
                origem="tela_configuracao",
                versao_prompt="teste-1",
                montar_pedido=lambda config: PedidoIA(
                    instrucoes="Responda apenas com a palavra OK.",
                    texto="Teste de conexão.",
                ),
            )
        except CotaExcedida:
            messages.warning(request, "Sua cota mensal de IA acabou: não foi possível testar a conexão.")
        except ErroIA as exc:
            messages.error(request, f"Falha na conexão: {exc}")
        else:
            config = carregar_config()
            messages.success(
                request,
                f"Conexão OK com {config.modelo}: \"{resposta.texto[:80]}\" ({resposta.tokens_total} tokens).",
            )
        return redirect("ia:configuracao")


class UsuariosIAView(GroupRequiredMixin, FilterView):
    group_required = ["administradores"]
    model = User
    filterset_class = UsuarioIAFilter
    template_name = "ia/usuarios.html"
    context_object_name = "usuarios"
    paginate_by = 20

    def get_queryset(self):
        do_mes = Q(requisicoes_ia__criado_em__gte=inicio_do_mes())
        return (
            User.objects
            .select_related("cota_ia")
            .annotate(
                tokens_mes=Coalesce(
                    Sum("requisicoes_ia__tokens_total", filter=do_mes & Q(requisicoes_ia__status=RequisicaoIA.SUCESSO)),
                    0,
                ),
                requisicoes_mes=Count("requisicoes_ia", filter=do_mes),
            )
            .order_by("-tokens_mes", "username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cota_padrao = carregar_config().cota_mensal_tokens
        context["cota_padrao"] = cota_padrao
        for usuario in context["usuarios"]:
            # Sem CotaUsuarioIA o acesso levanta RelatedObjectDoesNotExist (um AttributeError)
            proprio = getattr(usuario, "cota_ia", None)
            usuario.limite_proprio = proprio.limite_mensal_tokens if proprio else None
            usuario.limite = cota_padrao if proprio is None else proprio.limite_mensal_tokens
            usuario.percentual = min(100, int(usuario.tokens_mes * 100 / usuario.limite)) if usuario.limite else 100
        return context


class CotaUsuarioView(GroupRequiredMixin, FormView):
    group_required = ["administradores"]
    form_class = CotaUsuarioForm
    template_name = "ia/cota_form.html"
    success_url = reverse_lazy("ia:usuarios")

    def dispatch(self, request, *args, **kwargs):
        self.usuario = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["cota_padrao"] = carregar_config().cota_mensal_tokens
        return kwargs

    def get_initial(self):
        proprio = CotaUsuarioIA.objects.filter(usuario=self.usuario).first()
        return {"limite_mensal_tokens": proprio.limite_mensal_tokens if proprio else None}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.usuario
        context["cota"] = situacao_da_cota(dono_da_cota(self.usuario)).como_dict()
        return context

    def form_valid(self, form):
        limite = form.cleaned_data["limite_mensal_tokens"]
        if limite is None:
            CotaUsuarioIA.objects.filter(usuario=self.usuario).delete()
            messages.success(self.request, f"{self.usuario.username} voltou a usar a cota padrão.")
        else:
            CotaUsuarioIA.objects.update_or_create(usuario=self.usuario, defaults={"limite_mensal_tokens": limite})
            messages.success(self.request, f"Limite de {self.usuario.username} alterado para {limite} tokens por mês.")
        return super().form_valid(form)


class MeuConsumoView(LoginRequiredMixin, ListView):
    template_name = "ia/meu_consumo.html"
    context_object_name = "requisicoes"
    paginate_by = 15

    def get_queryset(self):
        return RequisicaoIA.objects.filter(usuario=self.request.user, criado_em__gte=inicio_do_mes())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cota"] = situacao_da_cota(dono_da_cota(self.request.user)).como_dict()
        return context
