# 🚀 Guia de Deploy Gratuito no Koyeb + Neon.tech

Este guia ensina como fazer o deploy gratuito do **fut_stream** no **Koyeb** com banco de dados PostgreSQL grátis no **Neon.tech**.

---

## Passo 1: Criar o Banco de Dados Grátis no Neon.tech

1. Acesse [neon.tech](https://neon.tech/) e faça cadastro (pode entrar com sua conta do GitHub).
2. Clique em **Create Project**.
3. Dê um nome para o projeto (ex: `fut-stream-db`) e clique em **Create Project**.
4. Quando o banco for criado, você verá uma tela com a **Connection String** (string de conexão).
   - Exemplo: `postgres://usuario:senha@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require`
5. **Copie essa URL** (você usará ela no Koyeb como `DATABASE_URL`).

---

## Passo 2: Fazer o Deploy no Koyeb

1. Acesse [koyeb.com](https://www.koyeb.com/) e crie uma conta gratuita (pode entrar com GitHub).
2. No painel do Koyeb, clique em **Create App** ou **Deploy Service**.
3. Escolha a opção **GitHub**:
   - Autorize o Koyeb a acessar seu repositório `fut_stream`.
   - Selecione o repositório `fut_stream` e a branch `main` (ou `master`).

4. Configure o Build & Deployment:
   - **Builder:** Escolha **Buildpack** (ou Docker se preferir).
   - **Build Command:** `./build.sh` (ou `chmod +x build.sh && ./build.sh`)
   - **Run Command:** `gunicorn fut_stream.wsgi --log-file -`

5. Adicione as **Environment Variables** (Variáveis de Ambiente):
   Clique em **Add Variable** para cada uma das variáveis abaixo:

   | Nome da Variável | Valor |
   | :--- | :--- |
   | `DATABASE_URL` | *(Cole a URL do Neon.tech que você copiou no Passo 1)* |
   | `SECRET_KEY` | `uma_chave_secreta_super_segura_aqui_123` |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `.koyeb.app,localhost,127.0.0.1` |
   | `DJANGO_SUPERUSER_USERNAME` | `admin` *(ou o usuário admin que desejar)* |
   | `DJANGO_SUPERUSER_EMAIL` | `seuemail@exemplo.com` |
   | `DJANGO_SUPERUSER_PASSWORD` | `suasenha123` |

6. Clique em **Deploy**.

---

## Passo 3: Pronto!

O Koyeb vai baixar o código do GitHub, instalar as dependências, rodar as migrações no banco Neon.tech, coletar os arquivos estáticos e colocar o site no ar.

Em 1 a 2 minutos seu site estará rodando no endereço fornecido pelo Koyeb (ex: `https://fut-stream-seuusuario.koyeb.app`).

Toda vez que você fizer um `git push` no GitHub, o Koyeb atualizará seu site automaticamente!
