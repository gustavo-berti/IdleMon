from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ConfiguracaoIA(models.Model):
    """Configuração editável na tela "Configuração da IA". Há no máximo um registro (pk=1).

    Sem registro valem os padrões do settings. A chave da API não fica aqui: só no .env.
    """

    PROVEDOR_CHOICES = [
        ("gemini", "Google Gemini"),
        ("falso", "Falso (testes, sem internet)"),
    ]

    ativa = models.BooleanField("IA ativa", default=True, help_text="Desligada, nenhuma tela chama a IA.")
    provedor = models.CharField("provedor", max_length=30, choices=PROVEDOR_CHOICES)
    modelo = models.CharField("modelo", max_length=80)
    timeout_segundos = models.PositiveIntegerField("tempo limite (s)", validators=[MinValueValidator(1)])
    tentativas = models.PositiveSmallIntegerField(
        "tentativas", validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Quantas vezes repetir quando o provedor está indisponível.",
    )
    espera_retentativa_segundos = models.FloatField(
        "espera entre tentativas (s)", validators=[MinValueValidator(0)],
        help_text="Dobra a cada nova tentativa.",
    )
    max_tokens_saida = models.PositiveIntegerField("máximo de tokens na resposta", validators=[MinValueValidator(1)])
    temperatura = models.FloatField("temperatura", validators=[MinValueValidator(0), MaxValueValidator(2)])
    cota_mensal_tokens = models.PositiveIntegerField(
        "cota mensal padrão (tokens)",
        help_text="Vale para quem não tem limite próprio em \"IA por usuário\".",
    )
    cota_alerta_percentual = models.PositiveSmallIntegerField(
        "alerta de cota (%)", validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="atualizado por",
    )

    class Meta:
        verbose_name = "Configuração da IA"
        verbose_name_plural = "Configuração da IA"

    @classmethod
    def padrao(cls):
        """Instância (não salva) com os valores do settings."""
        return cls(
            pk=1,
            ativa=True,
            provedor=settings.IA_PROVEDOR,
            modelo=settings.IA_MODELO,
            timeout_segundos=settings.IA_TIMEOUT_SEGUNDOS,
            tentativas=settings.IA_TENTATIVAS,
            espera_retentativa_segundos=settings.IA_ESPERA_RETENTATIVA_SEGUNDOS,
            max_tokens_saida=settings.IA_MAX_TOKENS_SAIDA,
            temperatura=settings.IA_TEMPERATURA,
            cota_mensal_tokens=settings.IA_COTA_MENSAL_TOKENS,
            cota_alerta_percentual=settings.IA_COTA_ALERTA_PERCENTUAL,
        )

    @classmethod
    def carregar(cls):
        return cls.objects.filter(pk=1).first() or cls.padrao()

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_provedor_display()} · {self.modelo}"


class CotaUsuarioIA(models.Model):
    """Limite mensal próprio de um usuário. Sem registro, vale a cota padrão da configuração."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cota_ia",
        verbose_name="usuário",
    )
    limite_mensal_tokens = models.PositiveIntegerField(
        "limite mensal (tokens)", help_text="0 bloqueia o uso da IA para este usuário."
    )
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Cota de IA do usuário"
        verbose_name_plural = "Cotas de IA dos usuários"

    def __str__(self):
        return f"{self.usuario} · {self.limite_mensal_tokens} tokens/mês"


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
