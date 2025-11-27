@echo off
REM Script de Backup do Banco de Dados para Windows
REM Execute este script regularmente para fazer backup dos seus dados

REM Configurações
set BACKUP_DIR=backups
set DATE=%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set BACKUP_FILE=%BACKUP_DIR%\backup_%DATE%.json

REM Criar diretório de backups se não existir
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo 🔄 Iniciando backup do banco de dados...

REM Fazer backup
python manage.py dumpdata ^
    --exclude auth.permission ^
    --exclude contenttypes ^
    --exclude admin.logentry ^
    --exclude sessions.session ^
    --indent 2 ^
    > %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo ✅ Backup criado com sucesso: %BACKUP_FILE%
    
    REM Mostrar tamanho do arquivo
    for %%A in (%BACKUP_FILE%) do echo 📦 Tamanho: %%~zA bytes
    
    echo ✅ Backup concluído!
) else (
    echo ❌ Erro ao criar backup!
    exit /b 1
)
