---
name: deploy-gae
description: Passo a passo para publicar o IdleMon no Google App Engine (app.yaml, estáticos, migrações, variáveis). Use quando pedirem deploy, publicação ou link de acesso.
---

# Deploy no Google App Engine

Deploy é ação externa: só execute quando o dono do projeto pedir, e mostre os comandos antes.

## Arquivos envolvidos

- `app.yaml`: runtime `python312`, gunicorn, `DEBUG: "False"`, `/static` servido de `static_gcloud/`.
- `.gcloudignore`: inclui o `.gitignore`, mas força o envio do `.env` (`!.env`), que tem `DATABASE_URL` e `GEMINI_API_KEY`.
- `requirements.txt`: dependências instaladas pelo build do App Engine (o nome precisa ser exatamente este).
- `idlepokemon/settings.py`: `DEBUG` e `ALLOWED_HOSTS` vêm de variáveis de ambiente (padrão aceita `.appspot.com`);
  `CSRF_TRUSTED_ORIGINS` aceita `https://*.appspot.com`. A Debug Toolbar só carrega com `DEBUG=True`.

## Passo a passo

```bash
source venv/bin/activate
python manage.py test --noinput                 # com TEST_DATABASE_NAME próprio, se precisar
python manage.py check --deploy                 # revise os avisos
python manage.py migrate                        # banco do .env (é o mesmo do deploy)
python manage.py collectstatic --noinput        # gera static_gcloud/
gcloud auth login                               # interativo: peça para o usuário rodar com "! gcloud auth login"
gcloud config set project <ID_DO_PROJETO>
gcloud app deploy app.yaml
gcloud app browse                               # mostra o link https://<ID_DO_PROJETO>.<região>.r.appspot.com
```

## Depois do deploy

1. Abra o link, crie uma conta e faça o fluxo: criar box > comprar ovo > chocar > colocar na equipe > coletar.
2. No Django Admin (`/admin/`), confira se existe o grupo `administradores` com os usuários administradores.
3. Em "⚙️ Admin" > "Configuração da IA", clique em "Testar conexão".
4. Erros: `gcloud app logs tail -s default`.
