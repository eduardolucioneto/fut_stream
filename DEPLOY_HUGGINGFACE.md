# 🚀 Guia de Deploy Gratuito no Hugging Face Spaces (Docker)

O **Hugging Face Spaces** oferece hospedagem via **Docker 100% gratuita** com **16GB de RAM**, **2 CPUs** e funcionamento **24/7 sem desligar**.

---

## Passo 1: Criar conta e novo Space no Hugging Face

1. Acesse [huggingface.co](https://huggingface.co/) e crie uma conta gratuita (se ainda não tiver).
2. No menu superior direito (no seu avatar), clique em **New Space**.
3. Configure o Space:
   - **Space name:** `fut-stream` (ou o nome que desejar).
   - **License:** `mit` (ou qualquer outra).
   - **Select the Space SDK:** Escolha **Docker** ➔ selecione a opção **Blank**.
   - **Space hardware:** Escolha **Free (CPU basic · 2 vCPU · 16 GB)**.
   - **Privacy:** Escolha **Public** (para todos acessarem) ou **Private**.
4. Clique em **Create Space**.

---

## Passo 2: Configurar as Variáveis de Ambiente (Secrets)

No seu Space recém-criado:
1. Vá na aba **Settings** no topo da página.
2. Role até a seção **Variables and secrets**.
3. Em **New secret**, adicione cada uma das variáveis:

| Key | Value |
| :--- | :--- |
| `DATABASE_URL` | *(Sua URL do banco Neon.tech que você copiou)* |
| `SECRET_KEY` | `uma_chave_secreta_super_segura_123` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `*` |
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | `suasenha123` |

---

## Passo 3: Enviar o Código para o Hugging Face Space

Você pode enviar o código de duas formas muito simples:

### Opção A: Conectar com seu GitHub (Recomendado)
1. Na aba **Settings** do seu Space no Hugging Face, em **GitHub repository sync**, você pode conectar seu repositório do GitHub para atualizar automaticamente a cada `git push`.

### Opção B: Enviar via Git para o Hugging Face diretamente
No seu terminal local (no VS Code / terminal da máquina):
```bash
git add .
git commit -m "Adiciona Dockerfile para Hugging Face"
git push
```
E depois adicionar o repositório do Hugging Face como remote:
```bash
git remote add hf https://huggingface.co/spaces/SEU_USUARIO_HF/fut-stream
git push hf main --force
```

---

## Passo 4: Pronto!

O Hugging Face vai ler o [Dockerfile](file:///g:/testes_python/fut_stream/Dockerfile), construir a imagem, rodar as migrações no banco Neon.tech, coletar os arquivos estáticos e colocar seu site no ar na porta 7860!

Seu site estará disponível no link direto da Hugging Face Spaces! 🚀
