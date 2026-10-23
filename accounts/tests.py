from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import STARTING_BALANCE

User = get_user_model()


class ContaTests(TestCase):
    def test_cadastro_da_saldo_inicial_e_mostra_mensagem(self):
        r = self.client.post(reverse('register'), {
            'username': 'ash', 'email': 'ash@exemplo.com',
            'password1': 'pikachu-123', 'password2': 'pikachu-123',
        }, follow=True)
        self.assertContains(r, 'Conta criada!')
        self.assertEqual(User.objects.get(username='ash').trainer_profile.coin_balance, STARTING_BALANCE)

    def test_editar_e_excluir_conta_mostram_mensagem(self):
        usuario = User.objects.create_user('ash', password='x')
        self.client.force_login(usuario)
        r = self.client.post(reverse('account_update'), {'username': 'ash2', 'email': 'a@b.com'}, follow=True)
        self.assertContains(r, 'Conta atualizada com sucesso!')
        r = self.client.post(reverse('account_delete'), follow=True)
        self.assertContains(r, 'Sua conta foi excluída')
        self.assertFalse(User.objects.filter(pk=usuario.pk).exists())
