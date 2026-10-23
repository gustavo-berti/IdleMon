from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from pokemon.models import Box, Especie, PokemonInstancia, TipoPokemon

User = get_user_model()


class HomeTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ash', password='x')
        self.client.force_login(self.usuario)

    def test_menu_admin_so_para_o_grupo_administradores(self):
        self.assertNotContains(self.client.get(reverse('home')), reverse('ovo_list'))
        self.usuario.groups.add(Group.objects.create(name='administradores'))
        r = self.client.get(reverse('home'))
        self.assertContains(r, reverse('ovo_list'))
        self.assertContains(r, reverse('ia:configuracao'))

    def test_equipe_ativa_e_rendimento(self):
        tipo = TipoPokemon.objects.create(name='Fogo', base_generation_value=20)
        especie = Especie.objects.create(name='Moltres', bst_final=580, max_evolution_stage=1)
        especie.types.add(tipo)
        box = Box.objects.create(trainer_profile=self.usuario.trainer_profile, name='Principal')
        PokemonInstancia.objects.create(box=box, species=especie, nickname='Fênix', box_position=0, is_active_team=True)
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Rendimento atual: 160,00 moedas / hora')
        self.assertEqual(len(r.context['vagas_equipe']), 5)

    def test_consultas_da_home_nao_crescem_com_os_pokemons(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        tipo = TipoPokemon.objects.create(name='Fogo', base_generation_value=20)
        box = Box.objects.create(trainer_profile=self.usuario.trainer_profile, name='Principal')

        def consultas_com(total):
            for i in range(total):
                especie = Especie.objects.create(name=f'Especie {total}-{i}')
                especie.types.add(tipo)
                PokemonInstancia.objects.create(box=box, species=especie, nickname='P', box_position=i, is_active_team=i < 3)
            with CaptureQueriesContext(connection) as ctx:
                self.client.get(reverse('home'))
            PokemonInstancia.objects.all().delete()
            return len(ctx.captured_queries)

        self.assertEqual(consultas_com(2), consultas_com(8))
