from django.core.management.base import BaseCommand

from pokemon.models import Especie
from pokemon.utils import get_pokemon_details, get_sprite_url


class Command(BaseCommand):
    help = "Busca na PokéAPI o sprite das espécies que ainda não possuem imagem."

    def add_arguments(self, parser):
        parser.add_argument(
            '--todas',
            action='store_true',
            help="Rebusca o sprite de todas as espécies, inclusive as que já possuem um.",
        )

    def handle(self, *args, **options):
        especies = Especie.objects.all().order_by('name')
        if not options['todas']:
            especies = especies.filter(sprite_url='')

        total = especies.count()
        if not total:
            self.stdout.write("Nenhuma espécie pendente de sprite.")
            return

        self.stdout.write(f"Buscando sprites de {total} espécie(s) na PokéAPI...")

        atualizadas = 0
        sem_sprite = []

        for especie in especies:
            detalhes = get_pokemon_details(especie.name)
            sprite_url = get_sprite_url(detalhes)

            if not sprite_url:
                sem_sprite.append(especie.name)
                self.stdout.write(self.style.WARNING(f"  - {especie.name}: sprite não encontrado"))
                continue

            especie.sprite_url = sprite_url
            especie.save(update_fields=['sprite_url'])
            atualizadas += 1
            self.stdout.write(f"  - {especie.name}: ok")

        self.stdout.write(self.style.SUCCESS(f"{atualizadas} espécie(s) atualizada(s)."))
        if sem_sprite:
            self.stdout.write(self.style.WARNING(f"Sem sprite: {', '.join(sem_sprite)}"))
