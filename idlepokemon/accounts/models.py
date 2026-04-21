from decimal import Decimal

from django.conf import settings
from django.db import models


class PerfilTreinador(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="trainer_profile",
	)
	coin_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

	def manage_account(self, amount: Decimal):
		self.coin_balance += Decimal(amount)
		self.save(update_fields=["coin_balance"])

	def __str__(self):
		return f"Perfil de {self.user.username}"
