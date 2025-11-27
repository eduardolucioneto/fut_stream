# 🔐 Variáveis de Ambiente para o Render

## Copie e cole estas configurações no Render:

### SECRET_KEY
```
+ancao#z!6$l(fq@m*1im#a__j(w_992^rptm8+0b)p0#-=3+!f
```

### DEBUG
```
False
```

### ALLOWED_HOSTS
```
fut-stream.onrender.com
```
(Substitua "fut-stream" pelo nome que você escolher para o seu web service)

### DATABASE_URL
```
(Será preenchido automaticamente após criar o banco PostgreSQL no Render)
```

---

## 📋 Resumo Rápido do Deploy

1. **Acesse:** https://render.com/
2. **Crie um Web Service** conectando ao repositório: `eduardoneto/fut_stream`
3. **Configure:**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn fut_stream.wsgi:application`
   - Instance Type: `Free`
4. **Adicione as variáveis de ambiente** acima
5. **Crie um PostgreSQL Database** (Free tier)
6. **Copie a Internal Database URL** e cole em `DATABASE_URL`
7. **Aguarde o deploy** (5-10 minutos)
8. **Crie um superusuário** via Shell:
   ```bash
   python manage.py createsuperuser
   ```

## ✅ Pronto!

Sua aplicação estará disponível em:
```
https://fut-stream.onrender.com
```

Admin:
```
https://fut-stream.onrender.com/admin/
```

---

**Nota:** O guia completo está em `DEPLOY_GUIDE.md`
