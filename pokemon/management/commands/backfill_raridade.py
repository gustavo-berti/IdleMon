from django.core.management.base import BaseCommand

from pokemon.models import Especie
from pokemon.utils import get_final_evolution_stats


class Command(BaseCommand):
    help = "Busca na PokéAPI o BST da última evolução (raridade) das espécies que ainda não o possuem."

    def add_arguments(self, parser):
        parser.add_argument(
            '--todas',
            action='store_true',
            help="Rebusca o BST de todas as espécies, inclusive as que já possuem um.",
        )

    def handle(self, *args, **options):
        especies = Especie.objects.all().order_by('name')
        if not options['todas']:
            especies = especies.filter(bst_final=0)

        total = especies.count()
        if not total:
            self.stdout.write("Nenhuma espécie pendente de raridade.")
            return

        self.stdout.write(f"Buscando o BST de {total} espécie(s) na PokéAPI...")

        atualizadas = 0
        sem_bst = []

        for especie in especies:
            bst_final, estagio_final = get_final_evolution_stats(especie.name)

            if not bst_final:
                sem_bst.append(especie.name)
                self.stdout.write(self.style.WARNING(f"  - {especie.name}: BST não encontrado"))
                continue

            especie.bst_final = bst_final
            especie.max_evolution_stage = estagio_final
            especie.save(update_fields=['bst_final', 'max_evolution_stage'])
            atualizadas += 1
            self.stdout.write(f"  - {especie.name}: BST {bst_final} ({especie.rarity_name})")

        self.stdout.write(self.style.SUCCESS(f"{atualizadas} espécie(s) atualizada(s)."))
        if sem_bst:
            self.stdout.write(self.style.WARNING(f"Sem BST: {', '.join(sem_bst)}"))
