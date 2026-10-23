# AGENTS.md — IdleMon / PokéSystem

Guia para agentes de IA (Claude Code, Codex, Copilot etc.) que trabalham neste repositório.
Regras de negócio completas: `CLAUDE.md` (local) e `context.md`.

## O projeto

Jogo idle de coleção de Pokémon em Django 5.2 (projeto acadêmico). O treinador compra ovos,
choca Pokémon sorteados pela raridade, guarda em Boxes e monta uma Equipe Ativa que rende moedas por hora.

| App | Responsabilidade |
|---|---|
| `accounts` | Login, cadastro, conta e `PerfilTreinador` (saldo, coleta de rendimento) |
| `pokemon` | Tipos, espécies, ovos, inventário, boxes, `PokemonInstancia`, loja e chocagem |
| `website` | Home/dashboard, sobre, template base, navbar, templatetag `paginacao`, partials de filtro e paginação |
| `ia` | **Única porta de entrada para a IA** (`chamar_ia`), configuração, auditoria, cota e telas de IA |
| `chatbot` | Assistente virtual que usa `chamar_ia` com o contexto de `chatbot/contexto_projeto.md` |

## Comandos

```bash
source venv/bin/activate
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py backfill_sprites       # sprites das espécies (PokéAPI)
python manage.py backfill_raridade      # BST da última evolução (raridade) das espécies
TEST_DATABASE_NAME=test_idlepokemon_<algo> python manage.py test --noinput
```

- O banco é Postgres (Neon) via `DATABASE_URL` no `.env`. Os testes criam um banco próprio sem rodar migrações
  (`TEST.MIGRATE = False`). Se o banco de testes estiver "em uso por outra sessão", troque `TEST_DATABASE_NAME`.
  O erro no "Destroying test database" vem do pooler do Neon e não indica falha nos testes.
- Nunca rode `migrate` nem apague dados no banco do `.env` sem o dono do projeto pedir: é o mesmo banco do deploy.

## Convenções de código

- **Idioma:** interface, mensagens, comentários e docstrings em português do Brasil.
  Models e métodos de `pokemon`/`accounts` usam nomes em inglês (`hatch`, `generate_profit`, `coin_balance`);
  `ia` e `chatbot` usam português (`chamar_ia`, `situacao_da_cota`). Siga o padrão do arquivo que você editar.
- **Indentação:** `pokemon/models.py`, `pokemon/admin.py`, `accounts/models.py` e `accounts/admin.py` usam **tab**;
  o resto usa 4 espaços. Aspas simples em `pokemon`, `accounts` e `website`; aspas duplas em `ia` e `chatbot`.
- **Views:** Class-Based Views genéricas (`ListView`, `CreateView`, `UpdateView`, `DeleteView`, `DetailView`, `FilterView`).
  - Admin: `GroupRequiredMixin` (django-braces) com `group_required = ['administradores']`.
  - Treinador: `LoginRequiredMixin` e `get_queryset()` filtrado pelo dono (`trainer_profile__user=self.request.user`).
    Registro de outro usuário deve dar 404, nunca 403 nem vazamento.
  - Toda criação, alteração e exclusão mostra mensagem (`messages` ou `SuccessMessageMixin`).
  - Listagens com filtro: `FilterView` + `filterset_class` em `<app>/filters.py`, e no template
    `{% include 'website/partials/filtro.html' %}` e `{% include 'website/partials/paginacao.html' %}`.
- **Consultas:** use `select_related`/`prefetch_related` para o que o template acessa. Em relação já pré-carregada
  use `.all()` (não `.first()`/`.values_list()`, que refazem a consulta). Confira com a Django Debug Toolbar.
- **Regras matemáticas** (CLAUDE.md §3) ficam nos models: `Especie.calculate_rarity()`, `PokemonInstancia.generate_profit()`,
  `Ovo.draw_species()`, `PerfilTreinador.collect_income()`.
- **Front-end:** Bootstrap 5 + jQuery. Confirmações com Bootbox (`<form data-confirmar="...">`) e máscaras com
  jQuery Mask (classes `mascara-preco` e `mascara-inteiro`), ambos em `static/js/site.js`.
- **IA:** nunca importe `google.genai` fora de `ia/provedores/gemini.py`. Chame sempre `ia.chamada.chamar_ia`.
  A chave da API fica só no `.env` (`GEMINI_API_KEY`).
- Cada mudança de comportamento vem com teste no `tests.py` do app.

## Skills

As skills ficam em `.claude/skills/`:

| Skill | Quando usar |
|---|---|
| `mensagem-commit` | Antes de qualquer `git commit`: padroniza a mensagem |
| `nova-tela-crud` | Criar uma tela de listagem/cadastro/edição/exclusão |
| `usar-ia` | Qualquer funcionalidade que chame a IA |
| `deploy-gae` | Publicar no Google App Engine |

## Commits

Siga a skill `mensagem-commit`. Resumo: `tipo: descrição curta no presente`, em português, minúsculas,
sem ponto final. Um commit por assunto. Só faça commit ou push quando o dono do projeto pedir.
