# Tutorial 20: Publicacao Web com Lizmap

## Introducao

O PyArchInit suporta a **publicacao web** de dados arqueologicos atraves do **Lizmap**, uma aplicacao que permite transformar projetos QGIS em aplicacoes web interativas.

### O Que e o Lizmap?

O Lizmap consiste em:
- **Plugin QGIS**: Para configurar a publicacao
- **Lizmap Web Client**: Aplicacao web para visualizar mapas
- **QGIS Server**: Backend para servir mapas

### Vantagens da Publicacao Web

| Aspeto | Descricao |
|--------|-----------|
| Acessibilidade | Dados acessiveis a partir do navegador |
| Partilha | Distribuicao facil para partes interessadas |
| Interatividade | Zoom, panoramica, consulta, popup |
| Atualizacao | Sincronizacao com a base de dados |
| Dispositivos moveis | Acesso a partir de telemovel/tablet |

## Pre-requisitos

### Servidor

1. **QGIS Server** instalado
2. **Lizmap Web Client** configurado
3. Servidor web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (recomendado)

### Cliente

1. **QGIS Desktop** com plugin Lizmap
2. **PyArchInit** configurado
3. Projeto QGIS guardado

## Instalacao do Plugin Lizmap

### A Partir do QGIS

1. **Plugins** > **Gerir Plugins**
2. Procurar "Lizmap"
3. Instalar **Lizmap**
4. Reiniciar o QGIS

## Preparacao do Projeto

### 1. Organizacao das Camadas

Estrutura recomendada:
```
Projeto QGIS
+-- Grupo: Base
|   +-- Ortofoto
|   +-- CTR/Cadastral
+-- Grupo: Escavacao
|   +-- pyunitastratigrafiche
|   +-- pyunitastratigrafiche_usm
|   +-- pyarchinit_quote
+-- Grupo: Documentacao
|   +-- Fotografias georreferenciadas
|   +-- Levantamentos
+-- Grupo: Analise
    +-- Harris Matrix (imagem)
```

### 2. Estilo das Camadas

Para cada camada:
1. Aplicar estilo apropriado
2. Configurar etiquetas
3. Definir visibilidade por escala

### 3. Popups e Atributos

Configurar popups para cada camada:
1. Clicar com o botao direito na camada > **Propriedades**
2. Separador **Visualizacao**
3. Configurar **Dica HTML do Mapa**

Exemplo de popup de UE:
```html
<h3>UE [% "us_s" %]</h3>
<p><b>Area:</b> [% "area_s" %]</p>
<p><b>Tipo:</b> [% "tipo_us_s" %]</p>
<p><b>Definicao:</b> [% "definizione" %]</p>
```

### 4. Guardar o Projeto

1. Guardar o projeto (.qgz) na pasta Lizmap
2. Utilizar caminhos relativos para os dados
3. Verificar que todas as camadas estao acessiveis

## Configuracao do Lizmap

### Abrir o Plugin

1. **Web** > **Lizmap** > **Lizmap**

### Separador Geral

| Campo | Descricao | Valor |
|-------|-----------|-------|
| Titulo do mapa | Nome apresentado | "Escavacao Via Roma" |
| Resumo | Descricao | "Documentacao arqueologica..." |
| Imagem | Miniatura do projeto | project_thumb.png |
| Repositorio | Pasta no servidor | /var/www/lizmap/projects |

### Separador Camadas

Para cada camada configurar:

| Opcao | Descricao |
|-------|-----------|
| Ativada | Camada visivel no Lizmap |
| Camada base | Camada de fundo (ortofoto, etc.) |
| Popup | Ativar popup ao clicar |
| Edicao | Permitir edicao online |
| Filtro | Filtros de utilizador |

### Separador Mapa Base

Configurar fundos:
- OpenStreetMap
- Google Maps (requer chave API)
- Bing Maps
- Ortofoto personalizada

### Separador Localizar

Pesquisa de localizacao:
- Configurar camadas para pesquisa
- Campos a pesquisar
- Formato de apresentacao

### Separador Edicao (Opcional)

Para permitir edicao online:
1. Selecionar camadas editaveis
2. Configurar campos editaveis
3. Definir permissoes

### Separador Ferramentas

Ativar/desativar:
- Impressao
- Medicoes
- Selecao
- Ligacao permanente
- etc.

### Guardar Configuracao

Clicar em **Guardar** para gerar o ficheiro `.qgs.cfg`

## Publicacao

### Carregar para o Servidor

1. Copiar ficheiros `.qgz` e `.qgz.cfg` para o servidor
2. Verificar permissoes dos ficheiros
3. Configurar o QGIS Server

### Estrutura no Servidor

```
/var/www/lizmap/
+-- lizmap/           # Aplicacao Lizmap
+-- projects/         # Projetos QGIS
|   +-- scavo_roma.qgz
|   +-- scavo_roma.qgz.cfg
+-- var/              # Dados da aplicacao
```

### Configuracao do QGIS Server

Ficheiro `/etc/apache2/sites-available/lizmap.conf`:
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Acesso Web

### URL da Aplicacao

```
http://lizmap.example.com/
```

### Navegacao

1. Selecao de projeto na pagina inicial
2. Vista interativa do mapa
3. Ferramentas na barra de ferramentas

### Funcionalidades para o Utilizador

| Funcao | Descricao |
|--------|-----------|
| Zoom | Roda do rato, botoes +/- |
| Panoramica | Arrastar o mapa |
| Popup | Clicar na feicao |
| Pesquisa | Barra de pesquisa |
| Impressao | Exportar para PDF |
| Ligacao permanente | URL partilhavel |

## Integracao com PyArchInit

### Dados em Tempo Real

Com PostgreSQL:
- Os dados estao sempre atualizados
- Alteracoes no PyArchInit visiveis imediatamente
- Sem sincronizacao manual

### Camadas Recomendadas

| Camada PyArchInit | Publicacao |
|-------------------|-----------|
| pyunitastratigrafiche | Sim, com popup |
| pyunitastratigrafiche_usm | Sim, com popup |
| pyarchinit_quote | Sim |
| pyarchinit_siti | Sim, como visao geral |
| Harris Matrix | Como imagem estatica |

### Configuracao Avancada de Popup de UE

Modelo HTML avancado:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">UE [% "us_s" %]</h3>
    <table>
        <tr><td><b>Sitio:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Area:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Tipo:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definicao:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Periodo:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Seguranca

### Autenticacao

O Lizmap suporta:
- Utilizadores locais
- LDAP
- OAuth2

### Configuracao de Utilizadores

Na administracao do Lizmap:
1. Criar grupos (admin, arqueologo, publico)
2. Criar utilizadores
3. Atribuir permissoes por projeto

### Permissoes de Camadas

| Grupo | Ver | Editar | Imprimir |
|-------|-----|--------|----------|
| Admin | Tudo | Tudo | Sim |
| Arqueologo | Tudo | Algumas | Sim |
| Publico | Apenas base | Nao | Nao |

## Manutencao

### Atualizacoes do Projeto

1. Editar projeto no QGIS Desktop
2. Regenerar configuracao Lizmap
3. Carregar para o servidor

### Cache

Gestao da cache de mosaicos:
```bash
# Limpar cache
lizmap-cache-clearer.php -project scavo_roma

# Regenerar mosaicos
lizmap-tiles-seeder.php -project scavo_roma -bbox xmin,ymin,xmax,ymax
```

### Registos e Depuracao

```bash
# Registo do QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Registo do Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Boas Praticas

### 1. Otimizacao de Desempenho

- Utilizar camadas raster pre-mosaicadas
- Limitar o numero de feicoes por camada
- Configurar visibilidade por escala
- Utilizar indices espaciais

### 2. Experiencia do Utilizador

- Popups informativos mas concisos
- Estilos claros e legiveis
- Organizacao logica das camadas
- Documentacao para o utilizador

### 3. Seguranca

- HTTPS obrigatorio
- Atualizacoes regulares
- Copias de seguranca das configuracoes
- Monitorizacao de acessos

### 4. Copia de Seguranca

- Copias de seguranca dos ficheiros `.qgz` e `.cfg`
- Copia de seguranca da base de dados PostgreSQL
- Versionar configuracoes

## Resolucao de Problemas

### Mapa Nao Apresentado

**Causas**:
- QGIS Server nao configurado
- Caminhos de ficheiros incorretos
- Permissoes insuficientes

**Solucoes**:
- Verificar registo do QGIS Server
- Verificar caminhos no projeto
- Verificar permissoes dos ficheiros

### Popups Nao Funcionam

**Causas**:
- Camada nao configurada para popup
- HTML incorreto no modelo

**Solucoes**:
- Ativar popup no Lizmap
- Verificar sintaxe HTML

### Desempenho Lento

**Causas**:
- Demasiados dados
- Cache nao configurada
- Servidor subdimensionado

**Solucoes**:
- Reduzir dados visiveis
- Configurar cache de mosaicos
- Aumentar recursos do servidor

## Referencias

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentacao
- [Documentacao Lizmap](https://docs.lizmap.com/)
- [Documentacao QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Tutorial em Video

### Configuracao do Lizmap
`[Placeholder: video_lizmap_setup.mp4]`

**Conteudos**:
- Instalacao do plugin
- Configuracao do projeto
- Publicacao

**Duracao prevista**: 20-25 minutos

### Personalizacao Web
`[Placeholder: video_lizmap_custom.mp4]`

**Conteudos**:
- Popups avancados
- Estilos personalizados
- Gestao de utilizadores

**Duracao prevista**: 15-18 minutos

---

*Ultima atualizacao: janeiro de 2026*
