# Guia de Depuração - Análise de Logs

## Localização dos Logs
Os logs da aplicação são salvos em: `logs/app.log`

## Comandos Úteis para Análise de Logs

### 1. Ver todos os logs
```powershell
type logs/app.log
```

### 2. Filtrar por Nível de Log
```powershell
# Ver apenas erros
type logs/app.log | findstr "ERROR"

# Ver avisos
type logs/app.log | findstr "WARNING"

# Ver informações de debug
type logs/app.log | findstr "DEBUG"
```

### 3. Filtrar por Funcionalidade
```powershell
# Logs relacionados a login
type logs/app.log | findstr /i "login senha password hash"

# Logs relacionados ao registro de usuários
type logs/app.log | findstr /i "register registro"

# Logs do Supabase
type logs/app.log | findstr /i "supabase"
```

### 4. Combinando Filtros
```powershell
# Erros de autenticação
type logs/app.log | findstr "ERROR" | findstr /i "login auth password"

# Erros do Supabase
type logs/app.log | findstr "ERROR" | findstr /i "supabase"
```

## Formato do Log
Cada linha do log contém:
- Timestamp: Data e hora do evento
- Level: Nível do log (ERROR, WARNING, INFO, DEBUG)
- Module: Módulo onde ocorreu o evento
- Function: Função onde ocorreu o evento
- Line: Número da linha no código
- Message: Mensagem descritiva

Exemplo:
```
2024-03-14 10:30:45 - DEBUG - routes - login - 123 - Iniciando rota de login
```

## Dicas de Depuração
1. Sempre comece olhando os ERRORs mais recentes
2. Use os logs de DEBUG para seguir o fluxo da execução
3. Verifique os WARNINGs para identificar possíveis problemas
4. Para problemas de autenticação, procure por logs contendo "login", "senha", "hash"
5. Para problemas com banco de dados, procure por "supabase"

## Exemplos Práticos

### Problema de Login
```powershell
type logs/app.log | findstr /i "login senha password hash" | findstr "ERROR WARNING"
```

### Problema de Registro
```powershell
type logs/app.log | findstr /i "register registro" | findstr "ERROR WARNING"
```

### Problema de Banco de Dados
```powershell
type logs/app.log | findstr /i "supabase database" | findstr "ERROR"
```

## Mantendo os Logs
1. Os logs são salvos em `logs/app.log`
2. Faça backup regular dos logs
3. Considere rotacionar os logs periodicamente para evitar arquivos muito grandes
4. Mantenha os logs organizados por data

## Níveis de Log
- ERROR: Erros que impedem o funcionamento normal
- WARNING: Avisos sobre problemas potenciais
- INFO: Informações gerais sobre o funcionamento
- DEBUG: Informações detalhadas para depuração

Lembre-se: Os logs são sua melhor ferramenta para entender o que está acontecendo na aplicação! 