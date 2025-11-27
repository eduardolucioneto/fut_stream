# 🚀 Guia de Deploy no Render

## ⚠️ IMPORTANTE: Configure o PostgreSQL!

**NÃO pule a etapa do banco de dados PostgreSQL!**

Se você não configurar o PostgreSQL:
- ❌ **Todos os usuários serão perdidos** a cada deploy
- ❌ **Todos os jogos cadastrados serão apagados**
- ❌ **Todas as configurações serão resetadas**

O SQLite **NÃO funciona** em produção no Render porque o sistema de arquivos é efêmero.

**Leia:** `POSTGRESQL_MIGRATION.md` para entender melhor.

---

## ✅ Pré-requisitos Concluídos
- [x] Código commitado e enviado para o GitHub
- [x] `build.sh` configurado
- [x] `requirements.txt` atualizado
- [x] `settings.py` configurado para produção
- [x] `.gitignore` configurado

## 📋 Passos para Deploy

### 1. Acessar o Render
1. Acesse: https://render.com/
2. Faça login ou crie uma conta (pode usar sua conta do GitHub)

### 2. Criar um Novo Web Service
1. No dashboard, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub: `eduardoneto/fut_stream`
3. Clique em **"Connect"** ao lado do repositório

### 3. Configurar o Web Service

Preencha os campos conforme abaixo:

**Nome:**
```
fut-stream
```
(ou qualquer nome que preferir)

**Region:**
```
Oregon (US West)
```
(ou a região mais próxima)

**Branch:**
```
main
```

**Root Directory:**
```
(deixe em branco)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
./build.sh
```

**Start Command:**
```
gunicorn fut_stream.wsgi:application
```

**Instance Type:**
```
Free
```

### 4. Configurar Variáveis de Ambiente

Clique em **"Advanced"** e adicione as seguintes **Environment Variables**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `django-insecure-GERE_UMA_CHAVE_ALEATORIA_AQUI` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `fut-stream.onrender.com` |
| `DATABASE_URL` | *(será preenchido automaticamente após criar o banco)* |

**⚠️ IMPORTANTE:** Gere uma SECRET_KEY segura. Você pode usar este comando no Python:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Criar um Banco de Dados PostgreSQL

1. No dashboard do Render, clique em **"New +"** → **"PostgreSQL"**
2. Preencha:
   - **Name:** `fut-stream-db`
   - **Database:** `fut_stream`
   - **User:** `fut_stream_user`
   - **Region:** *(mesma região do web service)*
   - **PostgreSQL Version:** `16`
   - **Instance Type:** `Free`

3. Clique em **"Create Database"**
4. Aguarde a criação (pode levar alguns minutos)

### 6. Conectar o Banco ao Web Service

1. Após o banco ser criado, copie a **Internal Database URL**
2. Volte para o seu Web Service
3. Vá em **"Environment"** → **"Environment Variables"**
4. Edite a variável `DATABASE_URL` e cole a URL copiada
5. Clique em **"Save Changes"**

### 7. Deploy Automático

O Render vai detectar as mudanças e iniciar o deploy automaticamente.

Você pode acompanhar o progresso nos **Logs**.

### 8. Criar um Superusuário

Após o deploy ser concluído com sucesso:

1. No dashboard do Render, vá para o seu Web Service
2. Clique em **"Shell"** (no menu lateral)
3. Execute o comando:
```bash
python manage.py createsuperuser
```
4. Preencha:
   - Username: `admin` (ou o que preferir)
   - Email: `eduardolucioneto@gmail.com`
   - Password: *(escolha uma senha segura)*

### 9. Acessar a Aplicação

Sua aplicação estará disponível em:
```
https://fut-stream.onrender.com
```
(ou o nome que você escolheu)

Para acessar o admin:
```
https://fut-stream.onrender.com/admin/
```

## 🔧 Configurações Adicionais (Opcional)

### Configurar Domínio Personalizado
1. No Web Service, vá em **"Settings"** → **"Custom Domain"**
2. Adicione seu domínio personalizado
3. Configure os registros DNS conforme instruído

### Configurar Email (para formulário de contato)
Adicione estas variáveis de ambiente:

| Key | Value |
|-----|-------|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | `seu-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `sua-senha-de-app` |
| `EMAIL_USE_TLS` | `True` |

**Nota:** Para Gmail, você precisa criar uma "Senha de App" em:
https://myaccount.google.com/apppasswords

## 🐛 Troubleshooting

### Erro: "Application failed to respond"
- Verifique se o comando de start está correto: `gunicorn fut_stream.wsgi:application`
- Verifique os logs para mais detalhes

### Erro: "Static files not found"
- Certifique-se de que `./build.sh` está sendo executado
- Verifique se `whitenoise` está instalado no `requirements.txt`

### Erro de Banco de Dados
- Verifique se a variável `DATABASE_URL` está configurada corretamente
- Certifique-se de que o banco PostgreSQL está rodando

## 📝 Notas Importantes

1. **Free Tier do Render:**
   - O serviço "dorme" após 15 minutos de inatividade
   - Pode levar até 1 minuto para "acordar" na primeira requisição
   - Banco de dados expira após 90 dias (faça backup!)

2. **Atualizações Futuras:**
   - Basta fazer `git push` que o Render fará deploy automaticamente
   - Você pode desabilitar auto-deploy se preferir

3. **Logs:**
   - Sempre verifique os logs em caso de erro
   - Acesse em: Dashboard → Seu Web Service → Logs

## ✅ Checklist Final

- [ ] Web Service criado e rodando
- [ ] Banco de dados PostgreSQL criado e conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Superusuário criado
- [ ] Aplicação acessível via URL do Render
- [ ] Admin panel funcionando
- [ ] Teste de criação de jogo
- [ ] Teste de transmissão

## 🎉 Pronto!

Sua aplicação está no ar! Qualquer dúvida, consulte a documentação do Render:
https://render.com/docs

---

**Última atualização:** 23/11/2025
