"""Provedor Google Gemini (pacote google-genai). É o único lugar que importa esse pacote."""

from ..excecoes import ErroIA, IaIndisponivel
from .base import ProvedorBase, RespostaIA

_CODIGOS_TEMPORARIOS = {408, 429, 500, 502, 503, 504}


class ProvedorGemini(ProvedorBase):
    nome = "gemini"

    def gerar(self, pedido, config):
        try:
            from google import genai
            from google.genai import errors, types
        except ImportError as exc:
            raise ErroIA("Pacote google-genai não instalado.") from exc

        if not config.chave_api:
            raise ErroIA("Chave da IA não configurada.")

        conteudos = [
            types.Content(role=m.papel, parts=[types.Part(text=m.conteudo)])
            for m in pedido.historico
        ]
        conteudos.append(types.Content(role="user", parts=[types.Part(text=pedido.texto)]))

        try:
            cliente = genai.Client(
                api_key=config.chave_api,
                http_options=types.HttpOptions(timeout=config.timeout_segundos * 1000),
            )
            resposta = cliente.models.generate_content(
                model=config.modelo,
                contents=conteudos,
                config=types.GenerateContentConfig(
                    system_instruction=pedido.instrucoes,
                    temperature=config.temperatura,
                    max_output_tokens=config.max_tokens_saida,
                ),
            )
        except errors.APIError as exc:
            if getattr(exc, "code", None) in _CODIGOS_TEMPORARIOS:
                raise IaIndisponivel(f"Gemini indisponível (código {exc.code}).") from exc
            raise ErroIA(f"Gemini recusou o pedido (código {getattr(exc, 'code', '?')}).") from exc
        except Exception as exc:  # rede, timeout, SSL...
            raise IaIndisponivel(f"Falha de comunicação com o Gemini ({type(exc).__name__}).") from exc

        texto = (resposta.text or "").strip()
        if not texto:
            raise ErroIA("O Gemini devolveu uma resposta vazia.")

        uso = resposta.usage_metadata
        return RespostaIA(
            texto=texto,
            tokens_entrada=getattr(uso, "prompt_token_count", 0) or 0,
            tokens_saida=getattr(uso, "candidates_token_count", 0) or 0,
        )
