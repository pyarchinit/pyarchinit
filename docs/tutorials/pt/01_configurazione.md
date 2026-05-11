# PyArchInit - Guia de Configuracao

## Indice
1. [Introducao](#introducao)
2. [Aceder a Configuracao](#aceder-a-configuracao)
3. [Separador Parametros de Ligacao](#separador-parametros-de-ligacao)
4. [Separador Instalacao da BD](#separador-instalacao-da-bd)
5. [Separador Ferramentas de Importacao](#separador-ferramentas-de-importacao)
6. [Separador Graphviz](#separador-graphviz)
7. [Separador PostgreSQL](#separador-postgresql)
8. [Separador Ajuda](#separador-ajuda)
9. [Separador FTP para Lizmap](#separador-ftp-para-lizmap)
10. [Workspace de Paradata (apenas PostgreSQL)](#workspace-de-paradata-apenas-postgresql)

---

## Introducao

A janela de configuracao do PyArchInit permite definir todos os parametros necessarios para o correto funcionamento do plugin. Antes de comecar a documentar uma escavacao arqueologica, e necessario configurar corretamente a ligacao a base de dados e os caminhos dos recursos.

> **Video Tutorial**: [Inserir ligacao de video para introducao a configuracao]

---

## Aceder a Configuracao

Para aceder a configuracao:
1. Abrir o QGIS
2. Menu **PyArchInit** -> **Config**

Ou, na barra de ferramentas do PyArchInit, clicar no icone de **Definicoes**.

![Aceder a configuracao](images/01_configurazione/01_menu_config.png)
*Figura 1: Aceder a janela de configuracao a partir do menu PyArchInit*

![Barra de ferramentas PyArchInit](images/01_configurazione/02_toolbar_config.png)
*Figura 2: Icone de configuracao na barra de ferramentas*

---

## Separador Parametros de Ligacao

Este e o separador principal para configurar a ligacao a base de dados.

![Separador Parametros de Ligacao](images/01_configurazione/03_tab_parametri_connessione.png)
*Figura 3: Separador Parametros de Ligacao - Vista completa*

### Seccao Definicoes da BD

| Campo | Descricao |
|-------|-----------|
| **Database** | Selecionar o tipo de base de dados: `sqlite` (local) ou `postgres` (servidor) |
| **Host** | Endereco do servidor PostgreSQL (ex.: `localhost` ou IP do servidor) |
| **DBname** | Nome da base de dados (ex.: `pyarchinit`) |
| **Port** | Porta de ligacao (predefinicao: `5432` para PostgreSQL) |
| **User** | Nome de utilizador para a ligacao |
| **Password** | Palavra-passe do utilizador |
| **SSL Mode** | Modo SSL para PostgreSQL: `allow`, `prefer`, `require`, `disable` |

![Definicoes da BD](images/01_configurazione/04_db_settings.png)
*Figura 4: Seccao Definicoes da BD*

#### Escolha da Base de Dados

**SQLite/Spatialite** (Recomendado para utilizador unico):
- Base de dados local, sem necessidade de servidor
- Ideal para projetos individuais ou pequenos
- O ficheiro `.sqlite` e guardado na pasta `pyarchinit_DB_folder`

![Configuracao SQLite](images/01_configurazione/05_config_sqlite.png)
*Figura 5: Exemplo de configuracao SQLite*

**PostgreSQL/PostGIS** (Recomendado para equipas):
- Base de dados em servidor, acesso multiutilizador
- Requer PostgreSQL com extensao PostGIS instalada
- Suporta gestao de utilizadores e permissoes
- Ideal para grandes projetos com varios operadores

![Configuracao PostgreSQL](images/01_configurazione/06_config_postgres.png)
*Figura 6: Exemplo de configuracao PostgreSQL*

> **Video Tutorial**: [Inserir ligacao de video para configuracao da base de dados]

### Seccao Definicoes de Caminhos

| Campo | Descricao | Botao |
|-------|-----------|-------|
| **Thumbnail path** | Caminho para guardar miniaturas de imagens | `...` para navegar |
| **Image resize** | Caminho para imagens redimensionadas | `...` para navegar |
| **Logo path** | Caminho para logotipo personalizado para relatorios | `...` para navegar |

![Definicoes de Caminhos](images/01_configurazione/07_path_settings.png)
*Figura 7: Seccao Definicoes de Caminhos*

#### Caminhos Remotos Suportados

O PyArchInit tambem suporta armazenamento remoto:
- **Google Drive**: `gdrive://pasta/caminho/`
- **Dropbox**: `dropbox://pasta/caminho/`
- **Amazon S3**: `s3://bucket/caminho/`
- **Cloudinary**: `cloudinary://cloud_name/pasta/`
- **WebDAV**: `webdav://servidor/caminho/`
- **HTTP/HTTPS**: `https://servidor/caminho/`

![Armazenamento Remoto](images/01_configurazione/08_remote_storage.png)
*Figura 8: Exemplo de configuracao de armazenamento remoto*

### Seccao Definicoes do Sitio

| Campo | Descricao |
|-------|-----------|
| **Site** | Nome do sitio predefinido para novos registos |
| **Experimental features** | Ativar funcionalidades experimentais (Sim/Nao) |

---

## Separador Instalacao da BD

Este separador permite instalar ou atualizar a base de dados do PyArchInit.

![Separador Instalacao da BD](images/01_configurazione/08_tab_installazione_db.png)
*Figura 8: Separador Instalacao da BD*

### Nova Instalacao

1. Selecionar **sqlite** ou **postgres** como tipo de base de dados
2. Clicar em **Connect**
3. Se a base de dados nao existir, clicar em **Install Database**
4. O sistema criara todas as tabelas necessarias

### Atualizacao da Base de Dados

Para instalacoes existentes:
1. Clicar em **Database Check/Update**
2. O sistema verifica a estrutura e aplica eventuais atualizacoes

> **Aviso**: Faca sempre uma copia de seguranca da sua base de dados antes de atualizar!

---

## Separador Ferramentas de Importacao

Ferramentas para importar dados de fontes externas.

### Importacao CSV

1. Selecionar o ficheiro CSV
2. Mapear as colunas para os campos da base de dados
3. Clicar em **Import**

### Importacao de Shapefile

Para importar dados GIS diretamente para as camadas do PyArchInit.

---

## Separador Graphviz

Configuracao do Graphviz para gerar diagramas Harris Matrix.

| Campo | Descricao |
|-------|-----------|
| **Graphviz Path** | Caminho para a instalacao do Graphviz (ex.: `/usr/bin/` no Linux) |
| **Check Graphviz** | Verificar a instalacao do Graphviz |

### Instalar o Graphviz

**Windows**: Descarregar a partir de [graphviz.org](https://graphviz.org/download/)

**macOS**: `brew install graphviz`

**Linux**: `sudo apt install graphviz`

---

## Separador PostgreSQL

Definicoes avancadas do servidor PostgreSQL.

| Campo | Descricao |
|-------|-----------|
| **pg_dump path** | Caminho para o pg_dump para copias de seguranca |
| **psql path** | Caminho para o comando psql |

---

## Separador Ajuda

Contem ligacoes e recursos uteis.

| Recurso | Descricao |
|---------|-----------|
| Video Tutorial | Ligacao para video tutoriais no YouTube |
| Documentacao Online | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| Facebook | Pagina UnaQuantum |

---

## Separador FTP para Lizmap

Configuracao para publicacao web com Lizmap.

| Campo | Descricao |
|-------|-----------|
| **FTP Host** | Endereco do servidor FTP |
| **FTP User** | Nome de utilizador FTP |
| **FTP Password** | Palavra-passe FTP |
| **Remote Path** | Caminho de destino no servidor |

---

## Workspace de Paradata (apenas PostgreSQL)

No **Separador DB Sync** da janela de configuracao encontra-se a seccao **Paradata Workspace**, que permite personalizar a pasta onde sao guardados os ficheiros `paradata_<sitio>.graphml` e `groups_<sitio>.graphml` quando se trabalha com uma base de dados PostgreSQL.

> **Apenas PostgreSQL**: os utilizadores de SQLite nao sao afetados por esta opcao. Com SQLite, os ficheiros de paradata continuam a ser guardados ao lado do ficheiro `.sqlite` (comportamento legado byte-identico).

### Caminho predefinido

Sem override, o caminho resolvido e:

```
~/pyarchinit/pyarchinit_DB_folder/<host>_<port>_<dbname>/<sitio>/
```

Exemplo: `~/pyarchinit/pyarchinit_DB_folder/localhost_5432_pyarchinit/Volterra/`

### Personalizar o caminho

- **Procurar...** abre um dialogo de ficheiros para escolher uma pasta. O caminho e guardado imediatamente nas QSettings do QGIS.
- Tambem se pode **escrever** o caminho diretamente no campo de texto: o valor e persistido ao sair do campo (sinal `editingFinished`). Deixar o campo vazio remove o override.
- **Repor** limpa o campo, remove a chave das QSettings e restaura o caminho predefinido.

### Cadeia de resolucao (quem ganha)

O caminho efetivo segue uma cadeia de fallback em 3 niveis:

1. **Variavel de ambiente `PYARCHINIT_WORKSPACE_DIR`** (prioridade maxima — util para scripts CI/teste).
2. **QSettings `pyarchinit/paradata_workspace`** (override da UI — esta seccao).
3. **Predefinido** `~/pyarchinit/pyarchinit_DB_folder/`.

Valores vazios sao ignorados: se `PYARCHINIT_WORKSPACE_DIR=""`, a resolucao passa para o nivel 2; se as QSettings tambem estiverem vazias, usa-se o predefinido.

### Quando produz efeito

As alteracoes sao **imediatas**: o proximo acesso a ParadataStore / GroupStore (por exemplo, gravar paradata numa ficha US ou exportar uma Matrix) usa o novo caminho. **Nao e necessario reiniciar o QGIS.**

### Casos de uso

- **Unidade de rede partilhada**: apontar o workspace para um caminho de rede (ex. `/Volumes/team/pyarchinit_workspace`) para partilhar paradata entre utilizadores num PostgreSQL centralizado.
- **Backup separado**: manter os ficheiros de paradata fora da pasta pessoal para facilitar copias de seguranca dedicadas.
- **Testes isolados**: definir `PYARCHINIT_WORKSPACE_DIR` em scripts de teste para nao poluir o workspace predefinido.

---

## Resolucao de Problemas

### Falha na Ligacao

**Causas**:
- Credenciais incorretas
- Servidor nao esta em execucao
- Firewall a bloquear a ligacao

**Solucoes**:
- Verificar nome de utilizador e palavra-passe
- Verificar se o servico PostgreSQL esta a funcionar
- Verificar as regras da firewall

### Base de Dados Nao Encontrada

**Causa**: Base de dados ainda nao instalada

**Solucao**: Ir ao separador Instalacao da BD e clicar em Install Database

---

## Boas Praticas

1. **Fazer copias de seguranca regularmente**: Utilizar a funcao de Copia de Seguranca e Restauro
2. **Usar PostgreSQL para equipas**: Melhor suporte multiutilizador
3. **Definir caminhos corretos**: Assegurar que todas as definicoes de caminhos apontam para diretorios validos
4. **Testar a ligacao**: Verificar sempre a ligacao antes de comecar a trabalhar

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para compreender melhor o processo de instalacao e configuracao.

[Abrir Animacao de Instalacao](../../animations/pyarchinit_installation_animation.html)

Explore a animacao interativa para a gestao de armazenamento remoto.

[Abrir Animacao de Armazenamento Remoto](../../animations/pyarchinit_remote_storage_animation.html)
