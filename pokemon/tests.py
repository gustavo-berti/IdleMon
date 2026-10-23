import random
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BOX_PRICE, MAX_ACTIVE_TEAM, Box, Especie, Ovo, OvoInventario, PokemonInstancia, TipoPokemon

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ash', password='x')
        self.outro = User.objects.create_user('gary', password='x')
        self.perfil = self.usuario.trainer_profile
        self.fogo = TipoPokemon.objects.create(name='Fogo', base_generation_value=20)
        self.voador = TipoPokemon.objects.create(name='Voador', base_generation_value=10)
        self.box = Box.objects.create(trainer_profile=self.perfil, name='Principal')
        self.client.force_login(self.usuario)

    def especie(self, nome, bst=300, estagio=1, estagio_max=3, tipos=None):
        especie = Especie.objects.create(
            name=nome, bst_final=bst, evolution_stage=estagio, max_evolution_stage=estagio_max
        )
        especie.types.set(tipos or [self.fogo])
        return especie

    def pokemon(self, especie=None, box=None, **extra):
        especie = especie or Especie.objects.filter(name='Charmander').first() or self.especie('Charmander')
        return PokemonInstancia.objects.create(box=box or self.box, species=especie, nickname='Poke', **extra)


class RegrasDoJogoTests(BaseTestCase):
    def test_raridade_pelo_bst_final(self):
        casos = [(300, 'Comum', 1), (420, 'Raro', 2), (519, 'Raro', 2), (520, 'Épico', 3), (580, 'Lendário', 4)]
        for i, (bst, nome, multiplicador) in enumerate(casos):
            especie = self.especie(f'E{i}', bst=bst)
            self.assertEqual((especie.rarity_name, especie.calculate_rarity()), (nome, multiplicador), bst)

    def test_v_base_e_media_dos_tipos(self):
        especie = self.especie('Charizard', tipos=[self.fogo, self.voador])
        self.assertEqual(especie.calculate_type_average(), 15)

    def test_lucro_com_evolucao_usa_o_estagio(self):
        # V_base 20 x Raro 2 x estágio 1
        pokemon = self.pokemon(self.especie('Charmander', bst=434, estagio=1, estagio_max=3))
        self.assertEqual(pokemon.generate_profit(), Decimal('40.00'))

    def test_lucro_de_estagio_unico_dobra(self):
        # V_base 20 x Lendário 4 x 2
        pokemon = self.pokemon(self.especie('Moltres', bst=580, estagio_max=1))
        self.assertEqual(pokemon.generate_profit(), Decimal('160.00'))

    def test_sorteio_respeita_as_chances_de_drop(self):
        ovo = Ovo.objects.create(trainer_profile=self.perfil, type=self.fogo, name='Ovo', price=10)
        comum, lendario = self.especie('Comum', bst=300), self.especie('Lenda', bst=600)
        ovo.species.set([comum, lendario])
        with mock.patch('pokemon.models.random.choices', wraps=random.choices) as choices:
            ovo.draw_species()
        self.assertEqual(choices.call_args.kwargs['weights'], [1, 65])

    def test_chocar_usa_a_primeira_vaga_e_o_nome_da_especie(self):
        self.pokemon(box_position=0)
        ovo = Ovo.objects.create(trainer_profile=self.perfil, type=self.fogo, name='Ovo de Fogo', price=10)
        ovo.species.set([self.especie('Vulpix')])
        pokemon = ovo.hatch(self.box)
        self.assertEqual((pokemon.nickname, pokemon.box_position), ('Vulpix', 1))

    def test_rendimento_acumulado_e_coleta(self):
        self.pokemon(self.especie('Moltres', bst=580, estagio_max=1), is_active_team=True)  # 160/h
        self.perfil.last_income_collection = timezone.now() - timedelta(hours=2)
        self.perfil.save()
        saldo = self.perfil.coin_balance
        self.assertEqual(self.perfil.collect_income(), Decimal('320.00'))
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.coin_balance, saldo + Decimal('320.00'))
        self.assertEqual(self.perfil.pending_income(), Decimal('0.00'))


class DonoDosRegistrosTests(BaseTestCase):
    """Box e PokemonInstancia: só o dono lista, vê, altera e exclui."""

    def setUp(self):
        super().setUp()
        self.box_alheia = Box.objects.create(trainer_profile=self.outro.trainer_profile, name='Box do Gary')
        self.pokemon_alheio = self.pokemon(box=self.box_alheia)

    def test_box_alheia_responde_404(self):
        for nome in ['box_detail', 'box_update', 'box_delete']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.box_alheia.pk])).status_code, 404, nome)
        self.assertEqual(self.client.post(reverse('box_delete', args=[self.box_alheia.pk])).status_code, 404)
        self.assertTrue(Box.objects.filter(pk=self.box_alheia.pk).exists())

    def test_lista_de_boxes_mostra_so_as_proprias(self):
        r = self.client.get(reverse('box_list'))
        self.assertContains(r, 'Principal')
        self.assertNotContains(r, 'Box do Gary')

    def test_pokemon_alheio_responde_404(self):
        for nome in ['pokemon_detail', 'pokemon_update', 'pokemon_delete']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.pokemon_alheio.pk])).status_code, 404, nome)
        self.assertEqual(self.client.post(reverse('pokemon_equipe', args=[self.pokemon_alheio.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('pokemon_delete', args=[self.pokemon_alheio.pk])).status_code, 404)

    def test_mover_para_box_alheia_e_invalido(self):
        meu = self.pokemon()
        r = self.client.post(reverse('pokemon_update', args=[meu.pk]), {'nickname': 'X', 'box': self.box_alheia.pk})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)
        meu.refresh_from_db()
        self.assertEqual(meu.box, self.box)

    def test_mover_de_box_vai_para_a_primeira_vaga(self):
        meu = self.pokemon(box_position=5)
        nova = Box.objects.create(trainer_profile=self.perfil, name='Segunda')
        r = self.client.post(reverse('pokemon_update', args=[meu.pk]), {'nickname': 'Faísca', 'box': nova.pk})
        self.assertRedirects(r, reverse('pokemon_detail', args=[meu.pk]))
        meu.refresh_from_db()
        self.assertEqual((meu.nickname, meu.box, meu.box_position), ('Faísca', nova, 0))

    def test_libertar_apaga_e_avisa(self):
        meu = self.pokemon()
        r = self.client.post(reverse('pokemon_delete', args=[meu.pk]), follow=True)
        self.assertFalse(PokemonInstancia.objects.filter(pk=meu.pk).exists())
        self.assertContains(r, 'foi libertado')


class EquipeAtivaTests(BaseTestCase):
    def test_colocar_e_retirar_da_equipe(self):
        meu = self.pokemon()
        url = reverse('pokemon_equipe', args=[meu.pk])
        self.client.post(url)
        meu.refresh_from_db()
        self.assertTrue(meu.is_active_team)
        self.client.post(url)
        meu.refresh_from_db()
        self.assertFalse(meu.is_active_team)

    def test_equipe_tem_no_maximo_6(self):
        especie = self.especie('Charmander')
        for _ in range(MAX_ACTIVE_TEAM):
            self.pokemon(especie, is_active_team=True)
        setimo = self.pokemon(especie)
        r = self.client.post(reverse('pokemon_equipe', args=[setimo.pk]), follow=True)
        self.assertContains(r, 'já tem 6 Pokémons')
        setimo.refresh_from_db()
        self.assertFalse(setimo.is_active_team)

    def test_coletar_credita_o_saldo(self):
        self.pokemon(self.especie('Moltres', bst=580, estagio_max=1), is_active_team=True)
        self.perfil.last_income_collection = timezone.now() - timedelta(hours=1)
        self.perfil.save()
        r = self.client.post(reverse('coletar_rendimento'), follow=True)
        self.assertContains(r, 'Você coletou 160')


class BoxTests(BaseTestCase):
    def test_segunda_box_custa_e_desconta(self):
        saldo = self.perfil.coin_balance
        r = self.client.post(reverse('box_create'), {'name': 'Nova'}, follow=True)
        self.assertContains(r, 'comprada por')
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.coin_balance, saldo - BOX_PRICE)

    def test_primeira_box_e_gratuita(self):
        self.box.delete()
        saldo = self.perfil.coin_balance
        self.client.post(reverse('box_create'), {'name': 'Primeira'})
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.coin_balance, saldo)

    def test_sem_saldo_nao_cria_box(self):
        self.perfil.coin_balance = 0
        self.perfil.save()
        r = self.client.post(reverse('box_create'), {'name': 'Nova'})
        self.assertContains(r, 'Saldo insuficiente')
        self.assertEqual(Box.objects.filter(trainer_profile=self.perfil).count(), 1)

    def test_renomear_e_excluir_mostram_mensagem(self):
        r = self.client.post(reverse('box_update', args=[self.box.pk]), {'name': 'Renomeada'}, follow=True)
        self.assertContains(r, "Box renomeada para &#x27;Renomeada&#x27;.")
        r = self.client.post(reverse('box_delete', args=[self.box.pk]), follow=True)
        self.assertContains(r, 'excluída')


class FiltrosEPaginacaoTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user('oak', password='x', is_staff=True)
        self.admin.groups.add(Group.objects.create(name='administradores'))
        agua = TipoPokemon.objects.create(name='Água', base_generation_value=15)
        for i in range(12):
            Ovo.objects.create(trainer_profile=self.admin.trainer_profile, type=self.fogo, name=f'Ovo Fogo {i:02}', price=10 + i)
        Ovo.objects.create(trainer_profile=self.admin.trainer_profile, type=agua, name='Ovo Água', price=5)

    def test_loja_filtra_por_tipo(self):
        r = self.client.get(reverse('loja_ovos'), {'type': self.fogo.pk})
        nomes = [o.name for o in r.context['ovos_disponiveis']]
        self.assertEqual(len(nomes), 9)
        self.assertNotIn('Ovo Água', nomes)
        self.assertEqual(r.context['paginator'].count, 12)

    def test_paginacao_preserva_os_filtros(self):
        r = self.client.get(reverse('loja_ovos'), {'type': self.fogo.pk, 'name': 'Fogo'})
        self.assertContains(r, f'?type={self.fogo.pk}&amp;name=Fogo&amp;page=2')

    def test_meus_ovos_filtra_e_so_mostra_o_proprio_inventario(self):
        ovo_fogo, ovo_agua = Ovo.objects.get(name='Ovo Fogo 00'), Ovo.objects.get(name='Ovo Água')
        OvoInventario.objects.create(trainer_profile=self.perfil, ovo=ovo_fogo)
        OvoInventario.objects.create(trainer_profile=self.perfil, ovo=ovo_agua)
        OvoInventario.objects.create(trainer_profile=self.outro.trainer_profile, ovo=ovo_fogo, quantidade=3)
        r = self.client.get(reverse('meus_ovos'), {'nome': 'água'})
        self.assertEqual([i.ovo.name for i in r.context['inventario']], ['Ovo Água'])
        r = self.client.get(reverse('meus_ovos'))
        self.assertEqual(r.context['paginator'].count, 2)

    def test_lista_admin_de_ovos_filtra(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('ovo_list'), {'price_max': 11})
        self.assertEqual(sorted(o.name for o in r.context['eggs']), ['Ovo Fogo 00', 'Ovo Fogo 01', 'Ovo Água'])

    def test_tag_parametros_url(self):
        request = RequestFactory().get('/', {'type': '1', 'page': '3'})
        html = Template('{% load paginacao %}{% parametros_url page=4 %}').render(Context({'request': request}))
        self.assertEqual(html, 'type=1&amp;page=4')


class AdminViewsTests(BaseTestCase):
    def test_usuario_fora_do_grupo_nao_acessa(self):
        r = self.client.get(reverse('tipopokemon_list'))
        self.assertEqual(r.status_code, 302)

    def test_crud_de_tipo_mostra_mensagens(self):
        admin = User.objects.create_user('oak', password='x')
        admin.groups.add(Group.objects.create(name='administradores'))
        self.client.force_login(admin)
        r = self.client.post(reverse('tipopokemon_create'), {'name': 'Gelo', 'base_generation_value': 5}, follow=True)
        self.assertContains(r, 'criado com sucesso')
        Ovo.objects.create(trainer_profile=admin.trainer_profile, type=self.fogo, name='Ovo', price=1)
        r = self.client.post(reverse('tipopokemon_delete', args=[self.fogo.pk]), follow=True)
        self.assertContains(r, 'não pode ser excluído')
        self.assertTrue(TipoPokemon.objects.filter(pk=self.fogo.pk).exists())


class TelasTests(BaseTestCase):
    def test_telas_do_treinador_abrem(self):
        staff = User.objects.create_user('oak', password='x', is_staff=True)
        ovo = Ovo.objects.create(trainer_profile=staff.trainer_profile, type=self.fogo, name='Ovo de Fogo', price=10)
        ovo.species.set([self.especie('Vulpix', bst=505)])
        inventario = OvoInventario.objects.create(trainer_profile=self.perfil, ovo=ovo)
        meu = self.pokemon(box_position=0)
        urls = [
            reverse('home'),
            reverse('box_list'),
            reverse('box_detail', args=[self.box.pk]),
            reverse('box_create'),
            reverse('pokemon_detail', args=[meu.pk]),
            reverse('pokemon_update', args=[meu.pk]),
            reverse('pokemon_delete', args=[meu.pk]),
            reverse('loja_ovos'),
            reverse('comprar_ovo', args=[ovo.pk]),
            reverse('meus_ovos'),
            reverse('chocar_ovo', args=[inventario.pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_chocar_leva_ao_detalhe_do_pokemon(self):
        staff = User.objects.create_user('oak', password='x', is_staff=True)
        ovo = Ovo.objects.create(trainer_profile=staff.trainer_profile, type=self.fogo, name='Ovo de Fogo', price=10)
        ovo.species.set([self.especie('Vulpix', bst=505)])
        inventario = OvoInventario.objects.create(trainer_profile=self.perfil, ovo=ovo)
        r = self.client.post(reverse('chocar_ovo', args=[inventario.pk]), {'box': self.box.pk, 'nickname': ''}, follow=True)
        self.assertContains(r, 'Você recebeu um(a) Vulpix (Raro)!')
        self.assertFalse(OvoInventario.objects.filter(pk=inventario.pk).exists())
