# 🚀 Guia de Deploy Gratuito no Vercel + Neon.tech

O **Vercel** é 100% gratuito, ultra rápido, não exige cartão de crédito e faz deploy automático direto do GitHub em poucos segundos!

---

## Passo 1: Obter a URL do Banco de Dados no Neon.tech

Você já criou o banco no **Neon.tech**.
Copie a sua **Connection String** que começa com `postgres://...` ou `postgresql://...`.

---

## Passo 2: Fazer o Deploy no Vercel

1. Acesse [vercel.com](https://vercel.com/) e faça login/cadastro com sua conta do GitHub.
2. No painel (Dashboard), clique no botão **Add New...** ➔ **Project**.
3. Em **Import Git Repository**, selecione o seu repositório `fut_stream` e clique em **Import**.
4. Na tela de configuração **Configure Project**:
   - **Framework Preset:** Deixe em `Other`.
   - Expandir a seção **Environment Variables** e adicione as seguintes variáveis:

   | Name | Value |
   | :--- | :--- |
   | `DATABASE_URL` | *(Cole a URL do Neon.tech)* |
   | `SECRET_KEY` | `uma_chave_secreta_super_segura_123` |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `.vercel.app,localhost,127.0.0.1` |

5. Clique no botão **Deploy**.

---

## Passo 3: Executar Migrações e Coletar Estáticos

Como a Vercel é Serverless, você pode rodar as migrações no banco Neon.tech diretamente do seu computador 1 única vez apontando para a URL do Neon.tech:

No seu terminal local (no VS Code):
```bash
$env:DATABASE_URL="sua_url_do_neon_aqui"
python manage.py migrate
python manage.py collectstatic --noinput
python create_superuser.py
```

---

## Passo 4: Pronto!

O Vercel gera um link público HTTPS (ex: `https://fut-stream.vercel.app`).
Toda vez que você fizer `git push` no seu GitHub, o Vercel atualiza seu site automaticamente em 10 segundos! 🚀
