# 🗄️ Guia: Migrar para PostgreSQL Permanente no Render

## ❌ Problema
Você está perdendo os usuários cadastrados a cada deploy porque:
- O SQLite (`db.sqlite3`) é armazenado no sistema de arquivos
- O Render **apaga** todos os arquivos a cada deploy
- Resultado: **todos os dados são perdidos**

## ✅ Solução
Usar o **PostgreSQL do Render** que é permanente e não é afetado pelos deploys.

---

## 📋 Passo a Passo

### 1. Criar um Banco PostgreSQL no Render

1. Acesse: https://dashboard.render.com/
2. Clique em **"New +"** → **"PostgreSQL"**
3. Preencha:
   - **Name:** `fut-stream-db`
   - **Database:** `fut_stream`
   - **User:** `fut_stream_user`
   - **Region:** *(mesma região do seu web service)*
   - **PostgreSQL Version:** `16`
   - **Instance Type:** `Free`
4. Clique em **"Create Database"**
5. **Aguarde** a criação (2-3 minutos)

### 2. Copiar a URL do Banco

Após a criação:
1. Clique no banco de dados criado
2. Na seção **"Connections"**, copie a **"Internal Database URL"**
   
   Exemplo:
   ```
   postgresql://fut_stream_user:senha@dpg-xxxxx/fut_stream
   ```

### 3. Configurar a Variável de Ambiente

1. Vá para o seu **Web Service** no Render
2. Clique em **"Environment"** (menu lateral)
3. Procure ou adicione a variável `DATABASE_URL`
4. **Cole** a URL que você copiou
5. Clique em **"Save Changes"**

### 4. Fazer um Novo Deploy

O Render vai detectar a mudança e fazer um novo deploy automaticamente.

**OU** você pode forçar um deploy manual:
1. Vá em **"Manual Deploy"**
2. Clique em **"Deploy latest commit"**

### 5. Executar as Migrações

Após o deploy completar:
1. No Web Service, clique em **"Shell"** (menu lateral)
2. Execute:
```bash
python manage.py migrate
```

### 6. Criar um Novo Superusuário

No mesmo Shell, execute:
```bash
python manage.py createsuperuser
```

Preencha:
- **Username:** `admin` (ou o que preferir)
- **Email:** `eduardolucioneto@gmail.com`
- **Password:** *(escolha uma senha segura)*

---

## 🎯 Resultado

Agora seus dados estarão **permanentemente salvos** no PostgreSQL:
- ✅ Usuários **não serão perdidos** nos deploys
- ✅ Jogos cadastrados **permanecerão** salvos
- ✅ Chat e mensagens **serão mantidos**
- ✅ Configurações do admin **preservadas**

---

## 📊 Diferenças: SQLite vs PostgreSQL

| Característica | SQLite (Local) | PostgreSQL (Render) |
|----------------|----------------|---------------------|
| **Persistência** | ❌ Perdido a cada deploy | ✅ Permanente |
| **Performance** | 🟡 Boa para dev | ✅ Excelente para produção |
| **Concorrência** | ❌ Limitada | ✅ Múltiplos usuários |
| **Backup** | ❌ Manual | ✅ Automático (Render) |
| **Custo** | Grátis | Grátis (Free tier) |

---

## ⚠️ Importante: Backup do Banco

### Fazer Backup Manual

No Shell do Render, execute:
```bash
python manage.py dumpdata > backup.json
```

Para restaurar:
```bash
python manage.py loaddata backup.json
```

### Backup Automático (Render Free Tier)

O Render faz backup automático, mas no plano Free:
- ⚠️ O banco expira após **90 dias de inatividade**
- ⚠️ Faça backups manuais regularmente

---

## 🔄 Migrar Dados Existentes (Se Necessário)

Se você já tem dados no SQLite local e quer migrar para o PostgreSQL:

### 1. Exportar Dados do SQLite Local

No seu computador:
```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json
```

### 2. Fazer Upload para o Render

Você pode fazer isso de duas formas:

**Opção A: Via Git**
1. Adicione o arquivo ao repositório:
```bash
git add data_backup.json
git commit -m "Add data backup for migration"
git push
```

2. No Shell do Render:
```bash
python manage.py loaddata data_backup.json
```

**Opção B: Via Shell Direto**
1. Copie o conteúdo de `data_backup.json`
2. No Shell do Render, crie o arquivo:
```bash
cat > data_backup.json << 'EOF'
[cole o conteúdo aqui]
EOF
```
3. Carregue os dados:
```bash
python manage.py loaddata data_backup.json
```

---

## 🐛 Troubleshooting

### Erro: "relation does not exist"
**Solução:** Execute as migrações primeiro:
```bash
python manage.py migrate
```

### Erro: "database is locked"
**Solução:** Isso não acontece com PostgreSQL, só com SQLite

### Erro: "password authentication failed"
**Solução:** Verifique se a `DATABASE_URL` está correta

### Banco não conecta
**Solução:** 
1. Certifique-se de usar a **Internal Database URL** (não a External)
2. Verifique se o banco PostgreSQL está rodando no Render

---

## 📝 Checklist de Migração

- [ ] Banco PostgreSQL criado no Render
- [ ] Internal Database URL copiada
- [ ] Variável `DATABASE_URL` configurada no Web Service
- [ ] Deploy realizado com sucesso
- [ ] Migrações executadas (`python manage.py migrate`)
- [ ] Superusuário criado
- [ ] Dados migrados (se necessário)
- [ ] Teste de login funcionando
- [ ] Teste de criação de jogo funcionando

---

## 💡 Dicas Importantes

1. **Sempre use PostgreSQL em produção**
   - SQLite é apenas para desenvolvimento local
   - PostgreSQL é mais robusto e confiável

2. **Faça backups regulares**
   - Use `dumpdata` semanalmente
   - Guarde os backups em local seguro

3. **Monitore o uso do banco**
   - O plano Free tem limite de 1GB
   - Verifique o uso no dashboard do Render

4. **Não commite o db.sqlite3**
   - Já está no `.gitignore`
   - Nunca envie bancos de dados para o Git

---

## ✅ Pronto!

Após seguir estes passos, seus dados estarão seguros e **não serão mais perdidos** nos deploys! 🎉

**Última atualização:** 23/11/2025
