from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TipoPokemon(models.Model):
	nome = models.CharField(max_length=80, unique=True)
	valor_base_geracao = models.FloatField()

	def __str__(self):
		return self.nome


class Especie(models.Model):
	nome = models.CharField(max_length=80, unique=True)
	estagio_evolucao = models.PositiveSmallIntegerField(default=1)
	tipos = models.ManyToManyField(TipoPokemon, related_name="especies")

	def clean(self):
		super().clean()
		total_tipos = self.tipos.count() if self.pk else 0
		if total_tipos and not 1 <= total_tipos <= 2:
			raise ValidationError("Uma especie deve ter entre 1 e 2 tipos.")

	def calcular_media_tipo(self):
		valores = list(self.tipos.values_list("valor_base_geracao", flat=True))
		if not valores:
			return 0.0
		return sum(valores) / len(valores)

	def __str__(self):
		return self.nome


class Box(models.Model):
	perfil_treinador = models.ForeignKey(
		"accounts.PerfilTreinador",
		on_delete=models.CASCADE,
		related_name="boxes",
	)
	nome = models.CharField(max_length=80)
	slots_max = models.PositiveIntegerField(default=30)

	def __str__(self):
		return f"{self.nome} ({self.perfil_treinador.user.username})"


class PokemonInstancia(models.Model):
	box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="pokemons")
	especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name="instancias")
	apelido = models.CharField(max_length=80)
	data_nascimento = models.DateTimeField(default=timezone.now)

	def gerar_lucro(self):
		return Decimal(str(self.especie.calcular_media_tipo()))

	def __str__(self):
		return self.apelido


class Ovo(models.Model):
	perfil_treinador = models.ForeignKey(
		"accounts.PerfilTreinador",
		on_delete=models.CASCADE,
		related_name="ovos",
	)
	tipo = models.ForeignKey(TipoPokemon, on_delete=models.PROTECT, related_name="ovos")
	especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name="ovos")
	nome = models.CharField(max_length=80)
	preco = models.DecimalField(max_digits=12, decimal_places=2)

	def chocar(self, box: Box, apelido: str = "Pokemon"):
		pokemon = PokemonInstancia.objects.create(
			box=box,
			especie=self.especie,
			apelido=apelido,
		)
		self.delete()
		return pokemon

	def __str__(self):
		return self.nome
