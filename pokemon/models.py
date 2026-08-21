from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TipoPokemon(models.Model):
	name = models.CharField(max_length=80, unique=True)
	base_generation_value = models.FloatField()

	def __str__(self):
		return self.name


class Especie(models.Model):
	name = models.CharField(max_length=80, unique=True)
	evolution_stage = models.PositiveSmallIntegerField(default=1)
	types = models.ManyToManyField(TipoPokemon, related_name="species")

	def clean(self):
		super().clean()
		total_types = self.types.count() if self.pk else 0
		if total_types and not 1 <= total_types <= 2:
			raise ValidationError("Uma especie deve ter entre 1 e 2 tipos.")

	def calculate_type_average(self):
		values = list(self.types.values_list("base_generation_value", flat=True))
		if not values:
			return 0.0
		return sum(values) / len(values)

	def __str__(self):
		return self.name


class Box(models.Model):
	trainer_profile = models.ForeignKey(
		"accounts.PerfilTreinador",
		on_delete=models.CASCADE,
		related_name="boxes",
	)
	name = models.CharField(max_length=80)
	slots_max = models.PositiveIntegerField(default=30)

	def __str__(self):
		return f"{self.name} ({self.trainer_profile.user.username})"


class PokemonInstancia(models.Model):
	box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="pokemon_instances")
	species = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name="instances")
	nickname = models.CharField(max_length=80)
	birth_date = models.DateTimeField(default=timezone.now)
	box_position = models.PositiveSmallIntegerField(null=True, blank=True)
	is_active_team = models.BooleanField(default=False)

	def generate_profit(self):
		return Decimal(str(self.species.calculate_type_average()))

	def __str__(self):
		return self.nickname


class Ovo(models.Model):
	trainer_profile = models.ForeignKey(
		"accounts.PerfilTreinador",
		on_delete=models.CASCADE,
		related_name="eggs",
	)
	type = models.ForeignKey(TipoPokemon, on_delete=models.PROTECT, related_name="eggs")
	species = models.ManyToManyField(Especie, related_name="eggs")
	name = models.CharField(max_length=80)
	price = models.DecimalField(max_digits=12, decimal_places=2)

	def hatch(self, box: Box, nickname: str = "Pokemon", species: Especie | None = None):
		selected_species = species or self.species.order_by('?').first()
		if selected_species is None:
			raise ValidationError("O ovo precisa ter pelo menos uma especie para chocar.")

		pokemon_instance = PokemonInstancia.objects.create(
			box=box,
			species=selected_species,
			nickname=nickname,
		)
		return pokemon_instance

	def __str__(self):
		return self.name


class OvoInventario(models.Model):
	"""Tabela intermediária que representa ovos no inventário do jogador."""
	trainer_profile = models.ForeignKey(
		"accounts.PerfilTreinador",
		on_delete=models.CASCADE,
		related_name="ovo_inventario",
	)
	ovo = models.ForeignKey(Ovo, on_delete=models.CASCADE, related_name="inventarios")
	quantidade = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = ("trainer_profile", "ovo")

	def __str__(self):
		return f"{self.trainer_profile.user.username} - {self.ovo.name} x{self.quantidade}"