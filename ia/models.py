from django.conf import settings
from django.db import models


class RequisicaoIA(models.Model):
    """Registro de cada chamada à IA. Não guarda o texto das perguntas nem das respostas."""

    SUCESSO = "sucesso"
    ERRO = "erro"
    COTA_EXCEDIDA = "cota_excedida"
    STATUS_CHOICES = [
        (SUCESSO, "Sucesso"),
        (ERRO, "Erro"),
        (COTA_EXCEDIDA, "Cota excedida"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requisicoes_ia",
        verbose_name="usuário",
    )
    finalidade = models.CharField("finalidade", max_length=60)
    origem = models.CharField("origem", max_length=60)
    versao_prompt = models.CharField("versão do prompt", max_length=60, blank=True)
    provedor = models.CharField("provedor", max_length=30)
    modelo = models.CharField("modelo", max_length=80)
    status = models.CharField("status", max_length=20, choices=STATUS_CHOICES)
    tentativas = models.PositiveSmallIntegerField("tentativas", default=0)
    tokens_entrada = models.PositiveIntegerField("tokens de entrada", default=0)
    tokens_saida = models.PositiveIntegerField("tokens de saída", default=0)
    tokens_total = models.PositiveIntegerField("tokens no total", default=0)
    duracao_ms = models.PositiveIntegerField("duração (ms)", default=0)
    erro = models.CharField("erro", max_length=300, blank=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Requisição de IA"
        verbose_name_plural = "Requisições de IA"
        ordering = ["-criado_em", "-id"]
        indexes = [models.Index(fields=["usuario", "criado_em"])]

    def __str__(self):
        return f"{self.finalidade} · {self.get_status_display()} · {self.criado_em:%d/%m/%Y %H:%M}"
