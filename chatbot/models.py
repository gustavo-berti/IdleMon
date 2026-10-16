from django.conf import settings
from django.db import models


class MensagemChat(models.Model):
    PAPEL_USUARIO = "user"
    PAPEL_ASSISTENTE = "model"
    PAPEL_CHOICES = [
        (PAPEL_USUARIO, "Usuário"),
        (PAPEL_ASSISTENTE, "Assistente"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensagens_chat",
        verbose_name="usuário",
    )
    papel = models.CharField("papel", max_length=10, choices=PAPEL_CHOICES)
    conteudo = models.TextField("conteúdo")
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Mensagem do chat"
        verbose_name_plural = "Mensagens do chat"
        ordering = ["criado_em", "id"]
        indexes = [models.Index(fields=["usuario", "criado_em"])]

    def __str__(self):
        return f"{self.usuario} · {self.get_papel_display()} · {self.criado_em:%d/%m/%Y %H:%M}"
