---
name: mensagem-commit
description: Padroniza mensagens de commit do IdleMon (tipo: descrição em português). Use antes de qualquer git commit neste repositório ou quando pedirem para escrever, revisar ou dividir commits.
---

# Mensagem de commit

Formato, igual ao histórico do repositório (`git log --oneline`):

```
<tipo>: <descrição>

[corpo opcional: o porquê, em frases curtas]
```

## Regras

1. **Tipo** (minúsculo), um destes:
   | Tipo | Quando |
   |---|---|
   | `feat` | funcionalidade nova para o usuário |
   | `fix` | correção de bug |
   | `perf` | melhora de desempenho (ex.: menos consultas) |
   | `refactor` | muda código sem mudar comportamento |
   | `test` | só testes ou configuração de testes |
   | `docs` | só documentação (`AGENTS.md`, `context.md`, skills) |
   | `style` | só visual/CSS ou formatação |
   | `chore` | dependências, banco, configuração, deploy |
2. **Descrição** em português, toda minúscula, sem ponto final, até ~72 caracteres.
3. Comece com **verbo na 3ª pessoa do presente**: "adiciona", "arruma", "corrige", "remove", "exibe",
   "restringe", "reduz", "usa", "atualiza", "define".
4. Diga **o que muda para quem usa**, não o arquivo: `feat: adiciona filtros na loja de ovos`,
   não `feat: altera views.py`.
5. Um assunto por commit. Se a mudança tem "e" juntando coisas independentes, divida em commits.
   Migrações vão no mesmo commit do model que as gerou.
6. Acentos são permitidos (o histórico tem os dois jeitos); não use emojis.
7. Mantenha as linhas de coautoria que o ambiente pedir (ex.: `Co-Authored-By:`) no fim do corpo.

## Exemplos do próprio histórico

```
feat: restringe views administrativas ao grupo administradores
perf: reduz consultas nas listagens de ovos e boxes
fix: define url de login para as views restritas
test: usa banco de testes com nome proprio e sem migracoes
chore: transforma pasta de projeto em repositorio raiz
```

## Passo a passo

1. `git status` e `git diff --staged` para ver o que entra.
2. Escolha o tipo pela tabela; se houver mais de um assunto, separe com `git add <arquivos>` por assunto.
3. Escreva a descrição seguindo as regras 2 a 4 e confira o tamanho.
4. Faça o commit com HEREDOC para preservar o corpo:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat: adiciona paginação que preserva os filtros

   EOF
   )"
   ```
