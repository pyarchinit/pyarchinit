# Tutorial 19: Trabalho Multiutilizador com PostgreSQL

## Introducao

O PyArchInit suporta trabalho **multiutilizador** atraves da utilizacao de **PostgreSQL/PostGIS** como backend de base de dados. Esta configuracao permite que varios operadores trabalhem simultaneamente no mesmo projeto arqueologico a partir de diferentes estacoes de trabalho.

### Vantagens do Multiutilizador

| Aspeto | SQLite | PostgreSQL Multiutilizador |
|--------|--------|---------------------------|
| Utilizadores simultaneos | 1 | Ilimitados |
| Acesso remoto | Nao | Sim |
| Gestao de permissoes | Nao | Sim |
| Copia de seguranca centralizada | Manual | Automatizavel |
| Desempenho | Bom | Excelente |
| Escalabilidade | Limitada | Elevada |

## Pre-requisitos

### Servidor PostgreSQL

1. **PostgreSQL** 12 ou superior
2. **PostGIS** 3.0 ou superior
3. Servidor acessivel na rede (LAN ou Internet)

### Cliente

1. QGIS com PyArchInit instalado
2. Ligacao de rede ao servidor
3. Credenciais de acesso

## Configuracao do Servidor

### Instalacao do PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Descarregar o instalador de [postgresql.org](https://www.postgresql.org/download/windows/)
- Instalar com Stack Builder para PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Criacao da Base de Dados

```sql
-- Ligar como superutilizador
sudo -u postgres psql

-- Criar base de dados
CREATE DATABASE pyarchinit_db;

-- Ativar PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Criar utilizador da aplicacao
CREATE USER pyarchinit WITH PASSWORD 'palavra_passe_segura';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configuracao de Acesso a Rede

Editar `pg_hba.conf`:
```
# Permitir ligacoes da rede local
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Ou de qualquer IP (menos seguro)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Editar `postgresql.conf`:
```
listen_addresses = '*'
```

Reiniciar o PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Configuracao do Cliente PyArchInit

### Configuracao Inicial

1. **PyArchInit** > **Configuracao**
2. Separador **Base de Dados**
3. Selecionar **PostgreSQL**
4. Preencher os campos:

| Campo | Valor |
|-------|-------|
| Servidor | Endereco IP ou nome do servidor |
| Porta | 5432 (predefinicao) |
| Base de dados | pyarchinit_db |
| Utilizador | pyarchinit |
| Palavra-passe | palavra_passe_segura |

### Teste de Ligacao

1. Clicar em **Testar Ligacao**
2. Verificar mensagem de sucesso
3. Guardar configuracao

### Criacao do Esquema

Se a base de dados for nova:
1. Clicar em **Criar Esquema**
2. Aguardar a criacao das tabelas
3. Verificar a estrutura

## Gestao de Utilizadores

### Criar Utilizadores Adicionais

```sql
-- Utilizador com acesso total
CREATE USER arqueologo1 WITH PASSWORD 'palavra_passe1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO arqueologo1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO arqueologo1;

-- Utilizador apenas de leitura
CREATE USER consultor1 WITH PASSWORD 'palavra_passe2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultor1;
```

### Niveis de Acesso Sugeridos

| Funcao | Permissoes | Utilizacao |
|--------|-----------|------------|
| Admin | ALL | Configuracao, gestao |
| Arqueologo | SELECT, INSERT, UPDATE, DELETE | Trabalho diario |
| Especialista | SELECT, INSERT, UPDATE (tabelas especificas) | Entrada de dados especializados |
| Consultor | SELECT | Consulta de dados |
| Copia de seguranca | SELECT | Scripts de copia de seguranca |

### Gestao de Funcoes

```sql
-- Criar funcao de grupo
CREATE ROLE arqueologos;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arqueologos;

-- Atribuir utilizadores ao grupo
GRANT arqueologos TO arqueologo1;
GRANT arqueologos TO arqueologo2;
```

## Fluxo de Trabalho Multiutilizador

### Organizacao do Trabalho

#### Por Area
- Atribuir diferentes areas a diferentes operadores
- Evitar sobreposicoes

#### Por Tipo
- Um operador: UE de deposito
- Outro operador: UE de muro
- Outro operador: Achados

#### Por Sitio
- Diferentes sitios para diferentes equipas

### Gestao de Conflitos

#### Bloqueio de Registos (recomendado)
1. Antes de modificar, verificar que ninguem esta a trabalhar no mesmo registo
2. Comunicar com a equipa

#### Resolucao de Conflitos
Em caso de modificacoes concorrentes:
1. A ultima modificacao prevalece
2. Verificar dados apos cada sessao
3. Utilizar o campo "data de modificacao" para rastreio

### Sincronizacao

Com PostgreSQL a sincronizacao e automatica:
- Cada modificacao e imediatamente visivel para os outros
- Nao e necessaria sincronizacao manual
- Atualizar o formulario para ver atualizacoes

## Copia de Seguranca e Seguranca

### Copia de Seguranca Automatica

Script de copia de seguranca diaria:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Manter apenas os ultimos 30 dias
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Agendar com cron:
```bash
# crontab -e
0 2 * * * /caminho/para/backup_pyarchinit.sh
```

### Restauro

```bash
# Restaurar a partir da copia de seguranca
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Seguranca

1. **Palavras-passe fortes**: Minimo 12 caracteres, mistura de maiusculas/minusculas/numeros
2. **Ligacoes SSL**: Ativar SSL para ligacoes remotas
3. **Firewall**: Limitar acesso a porta 5432
4. **Atualizacoes**: Manter o PostgreSQL atualizado
5. **Registo de auditoria**: Ativar registo de ligacoes

### SSL para Ligacoes Remotas

Em `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

Em `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Monitorizacao

### Ligacoes Ativas

```sql
SELECT
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE datname = 'pyarchinit_db';
```

### Tamanho da Base de Dados

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Bloqueios Ativos

```sql
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = 'pyarchinit_db');
```

## Migracao do SQLite

### Exportar do SQLite

1. Abrir o PyArchInit com a base de dados SQLite
2. **PyArchInit** > **Utilitarios** > **Exportar Base de Dados**
3. Exportar em formato SQL

### Importar para PostgreSQL

1. Configurar ligacao PostgreSQL
2. Criar esquema vazio
3. Importar dados exportados

### Script de Migracao

```python
# Exemplo conceptual
# Utilizar ferramentas de migracao especificas
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copiar tabelas
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Boas Praticas

### 1. Planeamento

- Definir funcoes e responsabilidades
- Estabelecer convencoes de trabalho
- Documentar procedimentos

### 2. Comunicacao

- Canal de comunicacao da equipa (chat, email)
- Sinalizar inicio/fim das sessoes de trabalho
- Comunicar areas em modificacao

### 3. Copia de Seguranca

- Copias de seguranca automaticas diarias
- Testes periodicos de restauro
- Copia de seguranca fora do local

### 4. Formacao

- Formacao sobre fluxo de trabalho multiutilizador
- Documentacao de procedimentos
- Suporte tecnico disponivel

## Resolucao de Problemas

### Ligacao Recusada

**Causas**:
- Servidor inacessivel
- Firewall a bloquear
- Credenciais incorretas

**Solucoes**:
- Verificar conectividade de rede
- Verificar regras da firewall
- Verificar credenciais

### Tempo de Ligacao Esgotado

**Causas**:
- Rede lenta
- Servidor sobrecarregado
- Demasiadas ligacoes

**Solucoes**:
- Otimizar rede
- Aumentar recursos do servidor
- Limitar ligacoes simultaneas

### Bloqueio da Base de Dados

**Causa**: Transacoes nao concluidas

**Solucao**:
```sql
-- Identificar processos bloqueantes
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminar processo (com cautela)
SELECT pg_terminate_backend(pid);
```

## Referencias

### Configuracao
- `modules/db/pyarchinit_conn_strings.py` - Cadeias de ligacao
- `gui/pyarchinit_Setting.py` - Interface de configuracao

### Documentacao Externa
- [Documentacao PostgreSQL](https://www.postgresql.org/docs/)
- [Documentacao PostGIS](https://postgis.net/documentation/)

---

## Tutorial em Video

### Configuracao Multiutilizador
`[Placeholder: video_multiutente_setup.mp4]`

**Conteudos**:
- Instalacao do PostgreSQL
- Configuracao do servidor
- Configuracao do cliente
- Gestao de utilizadores

**Duracao prevista**: 20-25 minutos

### Fluxo de Trabalho Colaborativo
`[Placeholder: video_multiutente_workflow.mp4]`

**Conteudos**:
- Organizacao do trabalho
- Gestao de conflitos
- Boas praticas

**Duracao prevista**: 12-15 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/pyarchinit_concurrency_animation.html)
