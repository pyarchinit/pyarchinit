# Tutorial 18: Copia de Seguranca e Restauro

## Introducao

A gestao de **copias de seguranca** e fundamental para a seguranca dos dados arqueologicos. O PyArchInit oferece ferramentas para efetuar copias de seguranca da base de dados e dos ficheiros associados, tanto para SQLite como para PostgreSQL.

### Importancia da Copia de Seguranca

- **Protecao de dados**: salvaguarda contra perda acidental
- **Versionamento**: possibilidade de voltar a estados anteriores
- **Migracao**: transferencia entre sistemas
- **Arquivo**: preservacao de projetos concluidos

---

## Tipos de Copia de Seguranca

### Copia de Seguranca da Base de Dados SQLite

Para bases de dados SQLite (ficheiros `.sqlite`):
- Copia direta do ficheiro da base de dados
- Simples e rapida
- Inclui todos os dados

### Copia de Seguranca da Base de Dados PostgreSQL

Para bases de dados PostgreSQL:
- Exportacao via `pg_dump`
- Formato SQL ou personalizado
- Pode incluir esquema e/ou dados

### Copia de Seguranca Completa

Inclui:
- Base de dados
- Ficheiros media (imagens, videos)
- Ficheiros de configuracao
- Relatorios gerados

---

## Aceder as Funcoes de Copia de Seguranca

### Pelo Painel de Configuracao

1. Menu **PyArchInit** > **Sketchy GPT** > **Definicoes** (ou Definicoes diretamente)
2. Na janela de configuracao
3. Separador ou seccao dedicada a copias de seguranca

### Pelo Sistema de Ficheiros

Para SQLite, pode copiar diretamente:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Copia de Seguranca SQLite

### Procedimento Manual

1. **Fechar** todos os formularios PyArchInit abertos
2. **Localizar** o ficheiro da base de dados:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   No Windows:
   ```
   C:\Users\[utilizador]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copiar** o ficheiro para uma pasta de copia de seguranca:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verificar** a integridade abrindo a copia com uma ferramenta SQLite

### Script Automatico (opcional)

Para copias de seguranca automaticas, criar um script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Copia de seguranca concluida: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Copia de seguranca concluida: %DEST%
```

---

## Copia de Seguranca PostgreSQL

### Utilizando pg_dump

1. **Abrir** um terminal/linha de comandos

2. **Executar** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parametros:
   - `-h`: servidor da base de dados
   - `-U`: utilizador
   - `-d`: nome da base de dados
   - `-F c`: formato personalizado (comprimido)
   - `-f`: ficheiro de saida

3. **Introduzir** a palavra-passe quando solicitado

### Copia de Seguranca Apenas de Dados

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_data.sql
```

### Copia de Seguranca Apenas do Esquema

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Copia de Seguranca de Ficheiros Media

### Pasta de Media

Os ficheiros media encontram-se na pasta:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procedimento

1. **Localizar** a pasta:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copiar** toda a pasta:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Comprimir** (opcional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restauro

### Restauro SQLite

1. **Fechar** o QGIS e o PyArchInit
2. **Renomear** a base de dados atual (por seguranca):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copiar** a copia de seguranca para a pasta original:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Reiniciar** o QGIS

### Restauro PostgreSQL

1. **Criar** uma base de dados vazia (se necessario):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restaurar** a copia de seguranca:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Atualizar** a configuracao do PyArchInit para utilizar a nova base de dados

### Restauro de Ficheiros Media

1. **Copiar** os ficheiros de copia de seguranca para a pasta de media:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Copia de Seguranca Completa do Projeto

### O Que Incluir

| Elemento | Caminho |
|----------|---------|
| Base de dados SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| PDFs gerados | `pyarchinit_PDF_folder/` |
| Relatorios | `pyarchinit_Report_folder/` |
| Configuracao | `pyarchinit_Logo_folder/`, ficheiros .txt |

### Script de Copia de Seguranca Completa

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Base de dados
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF e Relatorios
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Comprimir
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Copia de seguranca completa: $BACKUP_DIR.tar.gz"
```

---

## Boas Praticas

### Frequencia de Copias de Seguranca

| Tipo de Atividade | Frequencia Recomendada |
|-------------------|----------------------|
| Escavacao ativa | Diaria |
| Pos-escavacao | Semanal |
| Arquivo | Antes de cada alteracao significativa |

### Retencao

- Manter pelo menos **3 copias** em locais diferentes
- Utilizar **armazenamento na nuvem** para redundancia
- **Verificar periodicamente** a integridade das copias de seguranca

### Nomenclatura

Formato recomendado:
```
[projeto]_[tipo]_[data]_[versao]
Exemplo: vila_romana_db_20240115_v1.sqlite
```

### Documentacao

Criar um registo de copias de seguranca:
```
Data: 2024-01-15
Tipo: Copia de seguranca completa
Ficheiro: vila_romana_backup_20240115.tar.gz
Tamanho: 2.5 GB
Notas: Pre-encerramento campanha 2024
```

---

## Automatizacao de Copias de Seguranca

### Cron Job (Linux/Mac)

Adicionar ao crontab (`crontab -e`):
```
# Copia de seguranca diaria as 23:00
0 23 * * * /caminho/para/backup_script.sh
```

### Agendador de Tarefas (Windows)

1. Abrir o **Agendador de Tarefas**
2. Criar tarefa basica
3. Definir acionador (diario)
4. Acao: Iniciar programa > script batch

---

## Resolucao de Problemas

### Problema: Base de dados corrompida apos restauro

**Causa**: Ficheiro de copia de seguranca incompleto ou danificado.

**Solucao**:
1. Verificar integridade com `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Utilizar uma copia de seguranca anterior
3. Tentar recuperacao com ferramentas SQLite

### Problema: Tamanho excessivo da copia de seguranca

**Causa**: Muitos ficheiros media ou base de dados muito grande.

**Solucao**:
1. Comprimir copias de seguranca
2. Executar VACUUM na base de dados
3. Arquivar media mais antigos separadamente

### Problema: Erro de ligacao pg_dump

**Causa**: Parametros de ligacao incorretos.

**Solucao**:
1. Verificar servidor, porta, utilizador
2. Verificar pg_hba.conf para permissoes
3. Testar ligacao com psql

---

## Migracao Entre Bases de Dados

### De SQLite para PostgreSQL

1. Exportar dados do SQLite
2. Criar esquema no PostgreSQL
3. Importar dados

O PyArchInit gere isto atraves das definicoes de configuracao.

### De PostgreSQL para SQLite

1. Exportar dados do PostgreSQL
2. Criar base de dados SQLite
3. Importar dados

---

## Referencias

### Caminhos Padrao

| Sistema | Caminho Base |
|---------|-------------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[utilizador]\pyarchinit\` |

### Ferramentas Uteis

- **SQLite Browser**: Visualizacao/edicao de bases de dados SQLite
- **pgAdmin**: Gestao de PostgreSQL
- **7-Zip/tar**: Compressao de copias de seguranca
- **rsync**: Sincronizacao incremental

---

## Tutorial em Video

### Copia de Seguranca e Seguranca de Dados
**Duracao**: 10-12 minutos
- Procedimentos de copia de seguranca
- Restauro de base de dados
- Automatizacao

[Video placeholder: video_backup_restore.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
