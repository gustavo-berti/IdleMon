from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from .chamada import chamar_ia
from .cota import dono_da_cota, situacao_da_cota
from .excecoes import CotaExcedida, ErroIA, IaIndisponivel
from .models import RequisicaoIA
from .provedores.base import MensagemHistorico, PedidoIA
from .provedores.falso import ProvedorFalso

User = get_user_model()


@override_settings(
    IA_PROVEDOR="falso",
    IA_TENTATIVAS=3,
    IA_ESPERA_RETENTATIVA_SEGUNDOS=0,
    IA_COTA_MENSAL_TOKENS=100,
    IA_COTA_ALERTA_PERCENTUAL=80,
)
class ChamarIATests(TestCase):
    def setUp(self):
        ProvedorFalso.reiniciar()
        self.addCleanup(ProvedorFalso.reiniciar)
        self.usuario = User.objects.create_user("ash", password="x")

    def chamar(self, texto="oi", **extra):
        return chamar_ia(
            finalidade="teste",
            usuario=self.usuario,
            origem="testes",
            versao_prompt="t-1",
            montar_pedido=lambda config: PedidoIA(
                instrucoes="seja breve",
                texto=texto,
                historico=(MensagemHistorico("user", "a"), MensagemHistorico("model", "b")),
            ),
            **extra,
        )

    def test_sucesso_devolve_resposta_e_registra(self):
        resposta = self.chamar()
        self.assertEqual(resposta.texto, "Resposta de teste.")
        self.assertEqual(resposta.tokens_total, 15)
        req = RequisicaoIA.objects.get()
        self.assertEqual(
            (req.status, req.finalidade, req.origem, req.versao_prompt, req.tokens_total, req.tentativas),
            ("sucesso", "teste", "testes", "t-1", 15, 1),
        )
        self.assertEqual(req.usuario, self.usuario)

    def test_provedor_recebe_o_pedido_montado(self):
        self.chamar("pergunta")
        pedido = ProvedorFalso.pedidos[0]
        self.assertEqual(pedido.texto, "pergunta")
        self.assertEqual(pedido.instrucoes, "seja breve")
        self.assertEqual(len(pedido.historico), 2)

    def test_repete_quando_ia_indisponivel(self):
        ProvedorFalso.erros = [IaIndisponivel("x"), IaIndisponivel("y"), None]
        resposta = self.chamar()
        self.assertEqual(resposta.texto, "Resposta de teste.")
        self.assertEqual(len(ProvedorFalso.pedidos), 3)
        self.assertEqual(RequisicaoIA.objects.get().tentativas, 3)

    def test_desiste_depois_das_tentativas(self):
        ProvedorFalso.erros = [IaIndisponivel("fora")] * 3
        with self.assertRaises(IaIndisponivel):
            self.chamar()
        req = RequisicaoIA.objects.get()
        self.assertEqual((req.status, req.tentativas, req.tokens_total), ("erro", 3, 0))

    def test_erro_nao_temporario_nao_repete(self):
        ProvedorFalso.erros = [ErroIA("chave inválida")]
        with self.assertRaises(ErroIA):
            self.chamar()
        self.assertEqual(len(ProvedorFalso.pedidos), 1)
        self.assertEqual(RequisicaoIA.objects.get().erro, "chave inválida")

    def test_excecao_inesperada_vira_erro_ia_sem_vazar_texto(self):
        ProvedorFalso.erros = [RuntimeError("segredo")]
        with self.assertRaises(ErroIA):
            self.chamar()
        self.assertEqual(RequisicaoIA.objects.get().erro, "RuntimeError")

    def test_cota_esgotada_nao_chama_o_provedor(self):
        RequisicaoIA.objects.create(
            usuario=self.usuario, finalidade="teste", origem="t", provedor="falso",
            modelo="m", status="sucesso", tokens_total=100,
        )
        with self.assertRaises(CotaExcedida) as ctx:
            self.chamar()
        self.assertEqual(ProvedorFalso.pedidos, [])
        self.assertIn("limite", ctx.exception.mensagem_esgotada())
        self.assertEqual(RequisicaoIA.objects.filter(status="cota_excedida").count(), 1)

    def test_montar_pedido_nao_roda_com_cota_esgotada(self):
        RequisicaoIA.objects.create(
            usuario=self.usuario, finalidade="teste", origem="t", provedor="falso",
            modelo="m", status="sucesso", tokens_total=100,
        )
        montar = mock.Mock()
        with self.assertRaises(CotaExcedida):
            chamar_ia(finalidade="t", usuario=self.usuario, origem="t", versao_prompt="", montar_pedido=montar)
        montar.assert_not_called()

    @override_settings(IA_PROVEDOR="inexistente")
    def test_provedor_desconhecido(self):
        with self.assertRaises(ErroIA):
            self.chamar()


@override_settings(IA_COTA_MENSAL_TOKENS=100, IA_COTA_ALERTA_PERCENTUAL=80)
class CotaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("misty", password="x")
        self.outro = User.objects.create_user("brock", password="x")

    def gasto(self, usuario, tokens, status="sucesso", criado_em=None):
        req = RequisicaoIA.objects.create(
            usuario=usuario, finalidade="t", origem="t", provedor="falso",
            modelo="m", status=status, tokens_total=tokens,
        )
        if criado_em:
            RequisicaoIA.objects.filter(pk=req.pk).update(criado_em=criado_em)

    def test_dono_da_cota_e_o_proprio_usuario(self):
        self.assertEqual(dono_da_cota(self.usuario), self.usuario)

    def test_sem_uso(self):
        s = situacao_da_cota(self.usuario)
        self.assertEqual(s.como_dict(), {"usado": 0, "limite": 100, "percentual": 0, "em_alerta": False})

    def test_soma_so_sucessos_do_proprio_usuario(self):
        self.gasto(self.usuario, 30)
        self.gasto(self.usuario, 20)
        self.gasto(self.usuario, 50, status="erro")
        self.gasto(self.outro, 90)
        s = situacao_da_cota(self.usuario)
        self.assertEqual((s.usado, s.percentual, s.em_alerta, s.esgotada), (50, 50, False, False))

    def test_alerta_a_partir_de_80_por_cento(self):
        self.gasto(self.usuario, 80)
        self.assertTrue(situacao_da_cota(self.usuario).em_alerta)

    def test_percentual_nunca_passa_de_100(self):
        self.gasto(self.usuario, 250)
        s = situacao_da_cota(self.usuario)
        self.assertEqual(s.percentual, 100)
        self.assertTrue(s.esgotada)

    def test_mes_anterior_nao_conta(self):
        self.gasto(self.usuario, 90, criado_em=timezone.now() - timedelta(days=40))
        self.assertEqual(situacao_da_cota(self.usuario).usado, 0)
