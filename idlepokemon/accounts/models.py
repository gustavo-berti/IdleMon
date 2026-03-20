from decimal import Decimal

from django.conf import settings
from django.db import models


class PerfilTreinador(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="perfil_treinador",
	)
	saldo_moedas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

	def gerenciar_conta(self, valor: Decimal):
		self.saldo_moedas += Decimal(valor)
		self.save(update_fields=["saldo_moedas"])

	def __str__(self):
		return f"Perfil de {self.user.username}"
