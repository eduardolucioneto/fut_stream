# Guia de Deploy - TopTraders

Este guia mostra como fazer o deploy da aplicação TopTraders em diferentes plataformas.

## Opção 1: Deploy no Render (Recomendado - Gratuito)

### Pré-requisitos
1. Conta no [Render](https://render.com)
2. Conta no [GitHub](https://github.com)
3. Git instalado localmente

### Passos

#### 1. Preparar o Repositório Git

```bash
cd k:\testes_python\fut_stream
git init
git add .
git commit -m "Initial commit"
```

#### 2. Criar Repositório no GitHub
1. Acesse https://github.com/new
2. Crie um novo repositório (ex: `toptraders`)
3. **NÃO** inicialize com README, .gitignore ou license

#### 3. Enviar Código para o GitHub

```bash
git remote add origin https://github.com/SEU_USUARIO/toptraders.git
git branch -M main
git push -u origin main
```

#### 4. Configurar no Render

1. Acesse https://dashboard.render.com
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: toptraders
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn fut_stream.wsgi`

#### 5. Adicionar Variáveis de Ambiente

No painel do Render, vá em "Environment" e adicione:

```
SECRET_KEY=sua-chave-secreta-aqui-gere-uma-nova
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
DATABASE_URL=postgresql://... (Render fornece automaticamente se você criar um banco PostgreSQL)
```

**Gerar uma nova SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 6. Criar Banco de Dados PostgreSQL (Opcional mas recomendado)

1. No Render, clique em "New +" → "PostgreSQL"
2. Configure e crie
3. Copie a "Internal Database URL"
4. Cole como valor de `DATABASE_URL` nas variáveis de ambiente do Web Service

#### 7. Deploy!

O Render vai automaticamente:
- Instalar dependências
- Coletar arquivos estáticos
- Executar migrações
- Iniciar a aplicação

Acesse: `https://seu-app.onrender.com`

---

## Opção 2: Deploy no PythonAnywhere (Gratuito)

### Passos

#### 1. Criar Conta
1. Acesse https://www.pythonanywhere.com
2. Crie uma conta gratuita

#### 2. Upload do Código
1. No dashboard, vá em "Files"
2. Faça upload dos arquivos ou clone do GitHub:
```bash
git clone https://github.com/SEU_USUARIO/toptraders.git
```

#### 3. Criar Virtual Environment
No console Bash:
```bash
cd toptraders
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configurar Web App
1. Vá em "Web" → "Add a new web app"
2. Escolha "Manual configuration" → Python 3.11
3. Configure:
   - **Source code**: `/home/SEU_USUARIO/toptraders`
   - **Working directory**: `/home/SEU_USUARIO/toptraders`
   - **Virtualenv**: `/home/SEU_USUARIO/toptraders/venv`

#### 5. Editar WSGI Configuration
Clique no link do arquivo WSGI e substitua por:

```python
import os
import sys

path = '/home/SEU_USUARIO/toptraders'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'fut_stream.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 6. Configurar Variáveis de Ambiente
No arquivo `.env` (crie se não existir):
```
SECRET_KEY=sua-chave-secreta
DEBUG=False
ALLOWED_HOSTS=SEU_USUARIO.pythonanywhere.com
```

#### 7. Executar Migrações e Coletar Estáticos
No console Bash:
```bash
cd toptraders
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Criar admin
```

#### 8. Reload Web App
Clique no botão "Reload" no painel Web

Acesse: `https://SEU_USUARIO.pythonanywhere.com`

---

## Opção 3: Deploy no Railway (Gratuito com limitações)

### Passos

1. Acesse https://railway.app
2. Conecte com GitHub
3. Clique em "New Project" → "Deploy from GitHub repo"
4. Selecione seu repositório
5. Railway detecta automaticamente Django
6. Adicione variáveis de ambiente:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=*.railway.app`
7. Railway cria automaticamente um banco PostgreSQL

---

## Pós-Deploy - Tarefas Importantes

### 1. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 2. Acessar Admin
Acesse: `https://seu-dominio.com/admin`

### 3. Configurar Domínio Customizado (Opcional)
- Render: Configurações → Custom Domain
- PythonAnywhere: Web → Add custom domain (plano pago)

### 4. Monitoramento
- Render: Logs disponíveis no dashboard
- PythonAnywhere: Error log e Server log em "Web"

---

## Troubleshooting

### Erro 500
1. Verifique os logs
2. Confirme que `DEBUG=False`
3. Verifique `ALLOWED_HOSTS`
4. Execute `collectstatic`

### Arquivos Estáticos Não Carregam
1. Execute: `python manage.py collectstatic --noinput`
2. Verifique `STATIC_ROOT` e `STATIC_URL` no settings.py
3. Confirme que WhiteNoise está instalado

### Banco de Dados
1. Execute migrações: `python manage.py migrate`
2. Verifique `DATABASE_URL`

---

## Notas Importantes

⚠️ **Segurança:**
- NUNCA commite o arquivo `.env` (já está no .gitignore)
- Gere uma nova `SECRET_KEY` para produção
- Use `DEBUG=False` em produção
- Configure `ALLOWED_HOSTS` corretamente

⚠️ **WebRTC (PeerJS):**
- A funcionalidade de streaming pode ter limitações em planos gratuitos
- Considere usar um servidor STUN/TURN dedicado para produção
- Teste a funcionalidade após o deploy

⚠️ **Banco de Dados:**
- SQLite funciona mas não é recomendado para produção
- Use PostgreSQL para melhor performance e confiabilidade

---

## Suporte

Se encontrar problemas:
1. Verifique os logs da plataforma
2. Confirme que todas as variáveis de ambiente estão configuradas
3. Teste localmente com `DEBUG=False` antes do deploy
