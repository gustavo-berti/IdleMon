import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse

from ia.excecoes import IaIndisponivel
from ia.models import RequisicaoIA
from ia.provedores.falso import ProvedorFalso

from .instrucoes import carregar_contexto, montar_instrucoes
from .models import MensagemChat
from .services import historico_recente

User = get_user_model()


@override_settings(
    IA_PROVEDOR="falso",
    IA_TENTATIVAS=1,
    IA_ESPERA_RETENTATIVA_SEGUNDOS=0,
    IA_COTA_MENSAL_TOKENS=1000,
)
class ChatbotTests(TestCase):
    def setUp(self):
        ProvedorFalso.reiniciar()
        self.addCleanup(ProvedorFalso.reiniciar)
        self.usuario = User.objects.create_user("ash", password="x", email="ash@exemplo.com", first_name="Ash Ketchum")
        self.outro = User.objects.create_user("misty", password="x")
        self.client.force_login(self.usuario)

    def enviar(self, mensagem="Como compro um ovo?", cru=None):
        corpo = cru if cru is not None else json.dumps({"mensagem": mensagem})
        return self.client.post(reverse("chatbot:enviar"), data=corpo, content_type="application/json")

    # --- envio ---

    def test_sucesso_grava_duas_mensagens_e_devolve_a_resposta(self):
        ProvedorFalso.resposta = "Vá em **Loja de Ovos**."
        r = self.enviar()
        self.assertEqual(r.status_code, 200)
        dados = r.json()
        self.assertTrue(dados["sucesso"])
        self.assertEqual(dados["resposta"], "Vá em **Loja de Ovos**.")
        self.assertEqual(dados["cota"], {"usado": 15, "limite": 1000, "percentual": 1, "em_alerta": False})
        msgs = list(MensagemChat.objects.filter(usuario=self.usuario))
        self.assertEqual([(m.papel, m.conteudo) for m in msgs], [
            ("user", "Como compro um ovo?"),
            ("model", "Vá em **Loja de Ovos**."),
        ])
        self.assertEqual(RequisicaoIA.objects.get().finalidade, "chatbot_resposta")

    def test_pedido_leva_contexto_e_no_maximo_5_mensagens_em_ordem(self):
        for i in range(10):
            MensagemChat.objects.create(usuario=self.usuario, papel="user" if i % 2 == 0 else "model", conteudo=f"m{i}")
        MensagemChat.objects.create(usuario=self.outro, papel="user", conteudo="de outro usuário")
        self.enviar("nova pergunta")
        pedido = ProvedorFalso.pedidos[0]
        self.assertIn("## 1. O que é o sistema", pedido.instrucoes)
        self.assertIn("PERFIL DO USUÁRIO", pedido.instrucoes)
        self.assertEqual(pedido.texto, "nova pergunta")
        self.assertEqual([m.conteudo for m in pedido.historico], ["m5", "m6", "m7", "m8", "m9"])

    def test_erro_da_ia_nao_grava_e_responde_503_amigavel(self):
        ProvedorFalso.erros = [IaIndisponivel("detalhe técnico secreto")]
        with self.assertLogs("chatbot.views", level="ERROR"):
            r = self.enviar()
        self.assertEqual(r.status_code, 503)
        dados = r.json()
        self.assertFalse(dados["sucesso"])
        self.assertNotIn("secreto", dados["erro"])
        self.assertEqual(MensagemChat.objects.count(), 0)

    def test_cota_esgotada_responde_429_sem_chamar_o_provedor(self):
        RequisicaoIA.objects.create(
            usuario=self.usuario, finalidade="x", origem="t", provedor="falso",
            modelo="m", status="sucesso", tokens_total=1000,
        )
        r = self.enviar()
        self.assertEqual(r.status_code, 429)
        self.assertFalse(r.json()["sucesso"])
        self.assertIn("limite", r.json()["erro"])
        self.assertEqual(ProvedorFalso.pedidos, [])
        self.assertEqual(MensagemChat.objects.count(), 0)

    def test_pergunta_vazia_responde_400(self):
        for texto in ["", "   \n "]:
            r = self.enviar(texto)
            self.assertEqual(r.status_code, 400)
            self.assertFalse(r.json()["sucesso"])
        self.assertEqual(ProvedorFalso.pedidos, [])

    def test_pergunta_longa_demais_responde_400(self):
        self.assertEqual(self.enviar("a" * 2001).status_code, 400)
        self.assertEqual(self.enviar("a" * 2000).status_code, 200)

    def test_json_invalido_responde_400(self):
        self.assertEqual(self.enviar(cru="não é json").status_code, 400)
        self.assertEqual(self.enviar(cru=json.dumps({"outra": "coisa"})).status_code, 400)
        self.assertEqual(self.enviar(cru=json.dumps({"mensagem": 123})).status_code, 400)

    def test_enviar_exige_post_e_csrf(self):
        self.assertEqual(self.client.get(reverse("chatbot:enviar")).status_code, 405)
        cliente = self.client_class(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        r = cliente.post(reverse("chatbot:enviar"), data="{}", content_type="application/json")
        self.assertEqual(r.status_code, 403)

    # --- acesso ---

    def test_anonimo_vai_para_o_login(self):
        self.client.logout()
        for nome, metodo in [("chat", "get"), ("enviar", "post"), ("limpar", "post")]:
            r = getattr(self.client, metodo)(reverse(f"chatbot:{nome}"))
            self.assertEqual(r.status_code, 302, nome)
            self.assertIn("/login/", r["Location"], nome)

    def test_limpar_apaga_so_as_mensagens_do_proprio_usuario(self):
        MensagemChat.objects.create(usuario=self.usuario, papel="user", conteudo="a")
        MensagemChat.objects.create(usuario=self.outro, papel="user", conteudo="b")
        r = self.client.post(reverse("chatbot:limpar"))
        self.assertRedirects(r, reverse("chatbot:chat"))
        self.assertEqual(MensagemChat.objects.filter(usuario=self.usuario).count(), 0)
        self.assertEqual(MensagemChat.objects.filter(usuario=self.outro).count(), 1)

    # --- tela ---

    def test_tela_mostra_titulo_cota_e_so_as_proprias_mensagens(self):
        MensagemChat.objects.create(usuario=self.usuario, papel="user", conteudo="minha pergunta")
        MensagemChat.objects.create(usuario=self.outro, papel="user", conteudo="pergunta alheia")
        r = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Assistente virtual")
        self.assertContains(r, "Uso de IA no mês: 0 de 1000 tokens")
        self.assertContains(r, "minha pergunta")
        self.assertNotContains(r, "pergunta alheia")

    def test_conteudo_das_mensagens_sai_escapado(self):
        MensagemChat.objects.create(usuario=self.usuario, papel="model", conteudo="<script>alert(1)</script>")
        r = self.client.get(reverse("chatbot:chat"))
        self.assertNotContains(r, "<script>alert(1)</script>")

    def test_menu_mostra_assistente_so_para_logado(self):
        self.assertContains(self.client.get(reverse("home")), reverse("chatbot:chat"))
        self.client.logout()
        self.assertNotContains(self.client.get(reverse("home")), reverse("chatbot:chat"))

    # --- instruções e histórico ---

    def test_instrucoes_so_levam_dados_minimos_do_usuario(self):
        grupo = Group.objects.create(name="administradores")
        self.usuario.groups.add(grupo)
        texto = montar_instrucoes(self.usuario)
        self.assertIn("- Nome: Ash", texto)
        self.assertIn("- Administrador: não", texto)
        self.assertIn("- Grupos: administradores", texto)
        self.assertNotIn("ash@exemplo.com", texto)
        self.assertNotIn("Ketchum", texto)
        regras = texto.index("Você é o assistente virtual")
        perfil = texto.index("\n\nPERFIL DO USUÁRIO\n")
        contexto = texto.index("\n\nCONTEXTO DO SISTEMA\n")
        self.assertLess(regras, perfil)
        self.assertLess(perfil, contexto)

    def test_instrucoes_usam_username_sem_primeiro_nome(self):
        self.assertIn("- Nome: misty", montar_instrucoes(self.outro))

    def test_contexto_e_relido_quando_o_arquivo_muda(self):
        from . import instrucoes

        original = carregar_contexto()
        mtime = instrucoes.CAMINHO_CONTEXTO.stat().st_mtime_ns
        try:
            instrucoes._cache["mtime"] = mtime - 1
            instrucoes._cache["conteudo"] = "velho"
            self.assertEqual(carregar_contexto(), original)  # mtime diferente -> relê
            instrucoes._cache["conteudo"] = "em cache"
            self.assertEqual(carregar_contexto(), "em cache")  # mesmo mtime -> usa o cache
        finally:
            instrucoes._cache["mtime"] = mtime
            instrucoes._cache["conteudo"] = original

    def test_historico_recente_respeita_o_limite(self):
        for i in range(8):
            MensagemChat.objects.create(usuario=self.usuario, papel="user", conteudo=str(i))
        self.assertEqual([m.conteudo for m in historico_recente(self.usuario)], ["3", "4", "5", "6", "7"])
        self.assertEqual(len(historico_recente(self.usuario, limite=2)), 2)
