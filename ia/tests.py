from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .chamada import chamar_ia
from .config import carregar_config
from .cota import dono_da_cota, situacao_da_cota
from .excecoes import CotaExcedida, ErroIA, IaIndisponivel
from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA
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


@override_settings(
    IA_PROVEDOR="falso",
    IA_TENTATIVAS=1,
    IA_ESPERA_RETENTATIVA_SEGUNDOS=0,
    IA_COTA_MENSAL_TOKENS=100,
)
class ConfiguracaoNoBancoTests(TestCase):
    def setUp(self):
        ProvedorFalso.reiniciar()
        self.addCleanup(ProvedorFalso.reiniciar)
        self.usuario = User.objects.create_user("ash", password="x")

    def chamar(self):
        return chamar_ia(
            finalidade="t", usuario=self.usuario, origem="t", versao_prompt="",
            montar_pedido=lambda config: PedidoIA(instrucoes="", texto="oi"),
        )

    def test_sem_registro_usa_o_settings(self):
        config = carregar_config()
        self.assertEqual((config.provedor, config.cota_mensal_tokens, config.ativa), ("falso", 100, True))

    def test_registro_salvo_vale_no_lugar_do_settings(self):
        salva = ConfiguracaoIA.padrao()
        salva.cota_mensal_tokens = 500
        salva.modelo = "outro-modelo"
        salva.save()
        config = carregar_config()
        self.assertEqual((config.cota_mensal_tokens, config.modelo), (500, "outro-modelo"))
        self.assertEqual(ConfiguracaoIA.objects.count(), 1)

    def test_ia_desativada_nao_chama_o_provedor_e_registra(self):
        salva = ConfiguracaoIA.padrao()
        salva.ativa = False
        salva.save()
        with self.assertRaises(ErroIA):
            self.chamar()
        self.assertEqual(ProvedorFalso.pedidos, [])
        self.assertEqual(RequisicaoIA.objects.get().erro, "IA desativada na configuração.")

    def test_limite_proprio_do_usuario(self):
        CotaUsuarioIA.objects.create(usuario=self.usuario, limite_mensal_tokens=10)
        self.assertEqual(situacao_da_cota(self.usuario).limite, 10)

    def test_limite_zero_bloqueia(self):
        CotaUsuarioIA.objects.create(usuario=self.usuario, limite_mensal_tokens=0)
        with self.assertRaises(CotaExcedida):
            self.chamar()
        self.assertEqual(ProvedorFalso.pedidos, [])


@override_settings(
    IA_PROVEDOR="falso",
    IA_TENTATIVAS=1,
    IA_ESPERA_RETENTATIVA_SEGUNDOS=0,
    IA_COTA_MENSAL_TOKENS=1000,
)
class TelasIATests(TestCase):
    def setUp(self):
        ProvedorFalso.reiniciar()
        self.addCleanup(ProvedorFalso.reiniciar)
        self.admin = User.objects.create_user("oak", password="x")
        self.admin.groups.add(Group.objects.create(name="administradores"))
        self.usuario = User.objects.create_user("ash", password="x")
        RequisicaoIA.objects.create(
            usuario=self.usuario, finalidade="chatbot_resposta", origem="site", provedor="falso",
            modelo="m", status="sucesso", tokens_total=40,
        )
        RequisicaoIA.objects.create(
            usuario=self.admin, finalidade="teste_conexao", origem="tela", provedor="falso",
            modelo="m", status="erro",
        )

    def test_telas_de_admin_exigem_o_grupo(self):
        self.client.force_login(self.usuario)
        for nome in ["ia:requisicoes", "ia:configuracao", "ia:usuarios"]:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 302, nome)
        self.assertEqual(self.client.get(reverse("ia:cota_usuario", args=[self.usuario.pk])).status_code, 302)
        self.assertEqual(self.client.post(reverse("ia:testar_conexao")).status_code, 302)

    def test_requisicoes_filtra_por_status(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("ia:requisicoes"), {"status": "erro"})
        self.assertEqual([q.finalidade for q in r.context["requisicoes"]], ["teste_conexao"])

    def test_salvar_configuracao(self):
        self.client.force_login(self.admin)
        dados = {
            "ativa": "on", "provedor": "falso", "modelo": "modelo-x", "timeout_segundos": 10,
            "tentativas": 2, "espera_retentativa_segundos": 0, "max_tokens_saida": 256,
            "temperatura": 0.5, "cota_mensal_tokens": 2000, "cota_alerta_percentual": 90,
        }
        r = self.client.post(reverse("ia:configuracao"), dados, follow=True)
        self.assertContains(r, "Configuração da IA salva")
        salva = ConfiguracaoIA.objects.get()
        self.assertEqual((salva.modelo, salva.cota_mensal_tokens, salva.atualizado_por), ("modelo-x", 2000, self.admin))

    def test_testar_conexao(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("ia:testar_conexao"), follow=True)
        self.assertContains(r, "Conexão OK")
        self.assertTrue(RequisicaoIA.objects.filter(finalidade="teste_conexao", status="sucesso").exists())

    def test_testar_conexao_com_falha(self):
        ProvedorFalso.erros = [ErroIA("chave inválida")]
        self.client.force_login(self.admin)
        with self.assertLogs("ia.chamada", level="ERROR"):
            r = self.client.post(reverse("ia:testar_conexao"), follow=True)
        self.assertContains(r, "Falha na conexão: chave inválida")

    def test_ia_por_usuario_mostra_o_consumo_do_mes(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("ia:usuarios"))
        ash = next(u for u in r.context["usuarios"] if u.username == "ash")
        self.assertEqual((ash.tokens_mes, ash.requisicoes_mes, ash.limite, ash.percentual), (40, 1, 1000, 4))

    def test_alterar_e_voltar_para_a_cota_padrao(self):
        self.client.force_login(self.admin)
        url = reverse("ia:cota_usuario", args=[self.usuario.pk])
        self.client.post(url, {"limite_mensal_tokens": "50"})
        self.assertEqual(CotaUsuarioIA.objects.get(usuario=self.usuario).limite_mensal_tokens, 50)
        r = self.client.post(url, {"limite_mensal_tokens": ""}, follow=True)
        self.assertContains(r, "voltou a usar a cota padrão")
        self.assertFalse(CotaUsuarioIA.objects.filter(usuario=self.usuario).exists())

    def test_meu_consumo_mostra_so_as_proprias_requisicoes(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse("ia:meu_consumo"))
        self.assertEqual([q.finalidade for q in r.context["requisicoes"]], ["chatbot_resposta"])
        self.assertContains(r, "Uso de IA no mês: 40 de 1000 tokens")

    def test_meu_consumo_exige_login(self):
        self.assertEqual(self.client.get(reverse("ia:meu_consumo")).status_code, 302)
