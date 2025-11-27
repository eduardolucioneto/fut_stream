#!/bin/bash
# Script de Backup do Banco de Dados
# Execute este script regularmente para fazer backup dos seus dados

# Configurações
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.json"

# Criar diretório de backups se não existir
mkdir -p $BACKUP_DIR

echo "🔄 Iniciando backup do banco de dados..."

# Fazer backup
python manage.py dumpdata \
    --exclude auth.permission \
    --exclude contenttypes \
    --exclude admin.logentry \
    --exclude sessions.session \
    --indent 2 \
    > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso: $BACKUP_FILE"
    
    # Mostrar tamanho do arquivo
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "📦 Tamanho: $SIZE"
    
    # Manter apenas os últimos 10 backups
    echo "🧹 Limpando backups antigos..."
    ls -t $BACKUP_DIR/backup_*.json | tail -n +11 | xargs -r rm
    
    echo "✅ Backup concluído!"
else
    echo "❌ Erro ao criar backup!"
    exit 1
fi
