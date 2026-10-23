from decimal import ROUND_DOWN, Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

# Moedas que todo treinador novo recebe para comprar o primeiro ovo
STARTING_BALANCE = Decimal("1000.00")


class PerfilTreinador(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="trainer_profile",
	)
	coin_balance = models.DecimalField(max_digits=12, decimal_places=2, default=STARTING_BALANCE)
	last_income_collection = models.DateTimeField(default=timezone.now)

	def manage_account(self, amount: Decimal):
		self.coin_balance += Decimal(amount)
		self.save(update_fields=["coin_balance"])

	def hourly_income(self):
		"""Soma do G_moeda de todos os Pokémons da Equipe Ativa."""
		from pokemon.models import PokemonInstancia

		team = (
			PokemonInstancia.objects
			.filter(box__trainer_profile=self, is_active_team=True)
			.select_related("species")
			.prefetch_related("species__types")
		)
		return sum((p.generate_profit() for p in team), Decimal("0.00"))

	def pending_income(self, now=None, hourly=None):
		"""Moedas acumuladas desde a última coleta, pelo rendimento atual da equipe."""
		now = now or timezone.now()
		hourly = self.hourly_income() if hourly is None else hourly
		hours = Decimal(str(max(0.0, (now - self.last_income_collection).total_seconds()) / 3600))
		return (hourly * hours).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

	def collect_income(self):
		"""Credita o rendimento acumulado. Chamar também antes de mudar a equipe, para não
		aplicar o rendimento da equipe nova sobre as horas da equipe antiga."""
		now = timezone.now()
		amount = self.pending_income(now)
		self.coin_balance += amount
		self.last_income_collection = now
		self.save(update_fields=["coin_balance", "last_income_collection"])
		return amount

	def __str__(self):
		return f"Perfil de {self.user.username}"
