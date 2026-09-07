# 🚀 Guia de Deploy Gratuito no PythonAnywhere

Este guia explica como hospedar o projeto **fut_stream** (Django) gratuitamente no **PythonAnywhere** sem necessidade de cartão de crédito.

---

## 1. Criar Conta no PythonAnywhere
1. Acesse [pythonanywhere.com](https://www.pythonanywhere.com/).
2. Clique em **Pricing & signup** -> **Create a Beginner account** (Gratuito).
3. Escolha seu nome de usuário (seu site ficará em `seuusuario.pythonanywhere.com`).

---

## 2. Enviar o Projeto para o GitHub
Certifique-se de que o seu código atualizado esteja publicado no seu repositório do GitHub.

---

## 3. Clonar o Projeto no PythonAnywhere
1. No painel do PythonAnywhere, vá na aba **Consoles** e abra um console **Bash**.
2. Execute os seguintes comandos para clonar o projeto:
```bash
git clone https://github.com/SEU_USUARIO_GITHUB/fut_stream.git
cd fut_stream
```

---

## 4. Criar o Ambiente Virtual (Virtualenv)
No mesmo terminal Bash no PythonAnywhere, crie e instale as dependências:

```bash
mkvirtualenv --python=/usr/bin/python3.10 futenv
pip install -r requirements.txt
```

---

## 5. Configurar as Variáveis de Ambiente (`.env`)
No terminal Bash:
```bash
nano .env
```
Cole o seguinte conteúdo (ajuste com seus dados):
```env
SECRET_KEY=uma_chave_secreta_super_segura_aqui
DEBUG=False
ALLOWED_HOSTS=seuusuario.pythonanywhere.com,localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
```
*(Para salvar no nano: aperte `Ctrl + O`, depois `Enter`, e depois `Ctrl + X` para sair)*.

Execute as migrações do banco de dados e a coleta de arquivos estáticos:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python create_superuser.py
```

---

## 6. Configurar a Aplicação Web no Painel do PythonAnywhere
1. Vá para a aba **Web** no menu superior.
2. Clique em **Add a new web app**.
3. Escolha **Manual Configuration** (NÃO escolha Django automático) e selecione **Python 3.10**.
4. Após criar, configure as seções na aba Web:

### **Virtualenv**
- Clique no caminho do Virtualenv e digite:
  `/home/seuusuario/.virtualenvs/futenv`

### **Code**
- **Source code:** `/home/seuusuario/fut_stream`
- **Working directory:** `/home/seuusuario/fut_stream`

---

## 7. Configurar o Arquivo WSGI
1. Na aba **Web**, sob a seção **Code**, clique no link do **WSGI configuration file** (caminho no formato `/var/www/seuusuario_pythonanywhere_com_wsgi.py`).
2. Apague **todo** o conteúdo desse arquivo e cole:

```python
import os
import sys

# Caminho do projeto
path = '/home/seuusuario/fut_stream'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'fut_stream.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Lembre-se de substituir `seuusuario` pelo seu usuário real do PythonAnywhere!)*

3. Clique em **Save** no topo da tela.

---

## 8. Configurar Arquivos Estáticos (Static Files)
Na aba **Web**, role até a seção **Static files** e adicione:
- **URL:** `/static/`
- **Directory:** `/home/seuusuario/fut_stream/staticfiles`

---

## 9. Finalizar e Recarregar
1. No topo da aba **Web**, clique no botão verde **Reload seuusuario.pythonanywhere.com**.
2. Acesse no seu navegador: `https://seuusuario.pythonanywhere.com`

🎉 **Seu site está no ar gratuitamente!**
