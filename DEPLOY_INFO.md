# 🔐 Informações de Deploy - TopTraders

## ✅ Status do Código
- ✅ Código enviado para GitHub: https://github.com/eduardolneto/fut_stream
- ✅ Commit: "Melhorias no sistema de streaming WebRTC com debug detalhado"
- ✅ Branch: main

---

## 🔑 SECRET_KEY Gerada

Use esta SECRET_KEY no Render:

```
v()l3vj@8ua=ou!02yvudtq_h2c(4949aioj=lzlxez2pwiw#s65
```

⚠️ **IMPORTANTE**: Mantenha esta chave em segredo! Não compartilhe publicamente.

---

## 📋 Variáveis de Ambiente para o Render

Copie e cole estas variáveis no painel do Render (Environment):

### Configuração Mínima (Funcional)

```
SECRET_KEY=v()l3vj@8ua=ou!02yvudtq_h2c(4949aioj=lzlxez2pwiw#s65
DEBUG=False
ALLOWED_HOSTS=.onrender.com
```

### Configuração Recomendada (Com PostgreSQL)

Após criar o banco PostgreSQL no Render, adicione:

```
SECRET_KEY=v()l3vj@8ua=ou!02yvudtq_h2c(4949aioj=lzlxez2pwiw#s65
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<copiar-do-render-postgresql>
```

### Configuração Completa (Com Email)

Se quiser ativar o envio de emails:

```
SECRET_KEY=v()l3vj@8ua=ou!02yvudtq_h2c(4949aioj=lzlxez2pwiw#s65
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<copiar-do-render-postgresql>
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=eduardolucioneto@gmail.com
EMAIL_HOST_PASSWORD=<senha-de-app-do-gmail>
DEFAULT_FROM_EMAIL=noreply@toptraders.com
```

---

## 🚀 Comandos de Deploy

### Build Command (no Render)
```bash
./build.sh
```

### Start Command (no Render)
```bash
gunicorn fut_stream.wsgi:application
```

---

## 📝 Próximos Passos

1. ✅ Acessar: https://dashboard.render.com
2. ✅ Criar novo Web Service
3. ✅ Conectar repositório: `eduardolneto/fut_stream`
4. ✅ Configurar Build e Start Commands
5. ✅ Adicionar variáveis de ambiente
6. ✅ (Opcional) Criar PostgreSQL Database
7. ✅ Fazer deploy
8. ✅ Criar superusuário via Shell

---

## 🔗 Links Úteis

- **Dashboard Render**: https://dashboard.render.com
- **Repositório GitHub**: https://github.com/eduardolneto/fut_stream
- **Documentação Render**: https://render.com/docs/deploy-django
- **Guia Completo**: Ver arquivo `DEPLOY_RENDER.md`

---

## 📞 Após o Deploy

### Atualizar ALLOWED_HOSTS
Após o primeiro deploy, atualize a variável `ALLOWED_HOSTS` com o domínio real:
```
ALLOWED_HOSTS=seu-app-real.onrender.com
```

### Criar Admin
No Shell do Render:
```bash
python manage.py createsuperuser
```

### Testar
- Acesse: `https://seu-app.onrender.com`
- Admin: `https://seu-app.onrender.com/admin`

---

**Data de Deploy**: 2025-11-22
**Versão**: 1.0 (WebRTC com Debug)
