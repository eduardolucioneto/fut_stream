# 🚀 Guia de Deploy no Render - TopTraders

## ✅ Pré-requisitos Concluídos

- ✅ Código enviado para GitHub: https://github.com/eduardolneto/fut_stream
- ✅ Arquivo `build.sh` criado
- ✅ `requirements.txt` configurado
- ✅ `settings.py` preparado para produção

---

## 📋 Passos para Deploy no Render

### 1️⃣ Acessar o Render

1. Acesse: https://dashboard.render.com
2. Faça login (ou crie uma conta se ainda não tiver)

### 2️⃣ Criar um Novo Web Service

1. Clique no botão **"New +"** (canto superior direito)
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub:
   - Clique em **"Connect account"** se ainda não conectou o GitHub
   - Procure por: `eduardolneto/fut_stream`
   - Clique em **"Connect"**

### 3️⃣ Configurar o Web Service

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Name** | `toptraders` (ou o nome que preferir) |
| **Region** | `Oregon (US West)` (ou mais próximo) |
| **Branch** | `main` |
| **Root Directory** | (deixe em branco) |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn fut_stream.wsgi:application` |

### 4️⃣ Escolher o Plano

- Selecione **"Free"** (plano gratuito)
- Clique em **"Create Web Service"**

⚠️ **Importante**: O serviço vai começar a fazer o build, mas vai falhar porque faltam as variáveis de ambiente. Isso é normal!

### 5️⃣ Configurar Variáveis de Ambiente

1. No painel do seu Web Service, vá em **"Environment"** (menu lateral esquerdo)
2. Clique em **"Add Environment Variable"**
3. Adicione as seguintes variáveis:

#### Variável 1: SECRET_KEY
```
Key: SECRET_KEY
Value: [GERAR UMA NOVA - veja instruções abaixo]
```

**Como gerar uma SECRET_KEY:**
Execute no seu terminal local:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copie o resultado e cole como valor.

#### Variável 2: DEBUG
```
Key: DEBUG
Value: False
```

#### Variável 3: ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: .onrender.com
```

⚠️ **Nota**: Após o deploy, você vai atualizar isso com o domínio real (ex: `toptraders.onrender.com`)

#### Variável 4: DATABASE_URL (Opcional - Recomendado)
```
Key: DATABASE_URL
Value: [URL do PostgreSQL - veja próximo passo]
```

### 6️⃣ Criar Banco de Dados PostgreSQL (Recomendado)

1. Volte ao Dashboard do Render: https://dashboard.render.com
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `toptraders-db`
   - **Database**: `toptraders`
   - **User**: `toptraders`
   - **Region**: Mesma região do Web Service
   - **Plan**: **Free**
4. Clique em **"Create Database"**
5. Aguarde a criação (1-2 minutos)
6. Copie a **"Internal Database URL"**
7. Volte ao seu Web Service → Environment
8. Adicione/Edite a variável `DATABASE_URL` com a URL copiada

### 7️⃣ Configurar Email (Opcional)

Se quiser que o formulário de contato envie emails:

```
Key: EMAIL_BACKEND
Value: django.core.mail.backends.smtp.EmailBackend

Key: EMAIL_HOST
Value: smtp.gmail.com

Key: EMAIL_PORT
Value: 587

Key: EMAIL_USE_TLS
Value: True

Key: EMAIL_HOST_USER
Value: seu-email@gmail.com

Key: EMAIL_HOST_PASSWORD
Value: sua-senha-de-app-do-gmail

Key: DEFAULT_FROM_EMAIL
Value: noreply@toptraders.com
```

⚠️ **Gmail**: Use uma "Senha de App", não sua senha normal. Gere em: https://myaccount.google.com/apppasswords

### 8️⃣ Fazer o Deploy

1. Após adicionar todas as variáveis de ambiente, clique em **"Save Changes"**
2. O Render vai automaticamente fazer um novo deploy
3. Aguarde o build completar (5-10 minutos na primeira vez)

### 9️⃣ Atualizar ALLOWED_HOSTS

1. Após o deploy bem-sucedido, copie a URL do seu app (ex: `https://toptraders.onrender.com`)
2. Vá em **Environment**
3. Edite a variável `ALLOWED_HOSTS`
4. Atualize para: `toptraders.onrender.com` (substitua pelo seu domínio real)
5. Clique em **"Save Changes"**

### 🔟 Criar Superusuário (Admin)

1. No painel do Render, vá em **"Shell"** (menu lateral)
2. Execute:
```bash
python manage.py createsuperuser
```
3. Siga as instruções para criar o admin

---

## ✅ Verificar o Deploy

### Acessar a Aplicação
- URL: `https://seu-app.onrender.com`

### Acessar o Admin
- URL: `https://seu-app.onrender.com/admin`
- Use as credenciais do superusuário criado

### Verificar Logs
- No painel do Render, vá em **"Logs"** para ver os logs em tempo real

---

## 🔧 Troubleshooting

### Erro: "Application failed to respond"
- Verifique se o `Start Command` está correto: `gunicorn fut_stream.wsgi:application`
- Verifique os logs para ver o erro específico

### Erro 500
- Verifique se `DEBUG=False`
- Verifique se `ALLOWED_HOSTS` está correto
- Verifique os logs

### Arquivos Estáticos Não Carregam
- O `build.sh` já executa `collectstatic`
- Verifique se WhiteNoise está em `MIDDLEWARE` no settings.py (já está!)

### Banco de Dados
- Se usar SQLite (não recomendado), os dados serão perdidos a cada deploy
- Use PostgreSQL para persistência

---

## ⚠️ Notas Importantes

### Plano Gratuito do Render
- ✅ Gratuito para sempre
- ⚠️ O serviço "dorme" após 15 minutos de inatividade
- ⚠️ Primeira requisição após "acordar" pode levar 30-60 segundos
- ⚠️ 750 horas/mês de uso (suficiente para testes)

### WebRTC e Streaming
- ✅ PeerJS funciona no Render
- ⚠️ Pode ter limitações de performance no plano gratuito
- ⚠️ Para produção séria, considere um servidor TURN dedicado

### Próximos Passos
1. Testar a funcionalidade de streaming
2. Criar alguns jogos de teste
3. Testar o sistema de pagamento (mock)
4. Configurar domínio customizado (opcional)

---

## 🎯 Resumo das Variáveis de Ambiente Necessárias

**Mínimo para funcionar:**
```
SECRET_KEY=<gerar-nova>
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
```

**Recomendado (com PostgreSQL):**
```
SECRET_KEY=<gerar-nova>
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
DATABASE_URL=<url-do-postgresql>
```

**Completo (com Email):**
```
SECRET_KEY=<gerar-nova>
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
DATABASE_URL=<url-do-postgresql>
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=noreply@toptraders.com
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os **Logs** no painel do Render
2. Verifique se todas as **variáveis de ambiente** estão configuradas
3. Teste localmente com `DEBUG=False` antes

**Boa sorte com o deploy! 🚀**
