# Tutorial 29: Make Your Map

## Introducao

**Make Your Map** e a funcao do PyArchInit para gerar mapas profissionais e composicoes de impressao diretamente a partir da vista atual do QGIS. Utiliza modelos de composicao predefinidos para criar saidas cartograficas padronizadas.

### Funcionalidades

- Geracao rapida de mapas a partir da vista atual
- Modelos predefinidos para varios formatos
- Personalizacao de cabecalho e legenda
- Exportacao para PDF, PNG, SVG

## Acesso

### Pela Barra de Ferramentas
Icone **"Make your Map"** (impressora) na barra de ferramentas do PyArchInit

### Pelo Menu
**PyArchInit** > **Make your Map**

## Utilizacao Basica

### Geracao Rapida

1. Configurar vista de mapa pretendida no QGIS
2. Definir zoom e extensao corretos
3. Clicar em **"Make your Map"**
4. Selecionar modelo pretendido
5. Introduzir titulo e informacoes
6. Gerar mapa

## Modelos Disponiveis

### Formatos Padrao

| Modelo | Formato | Orientacao | Utilizacao |
|--------|---------|------------|-----------|
| A4 Retrato | A4 | Retrato | Documentacao padrao |
| A4 Paisagem | A4 | Paisagem | Vistas alargadas |
| A3 Retrato | A3 | Retrato | Estampas detalhadas |
| A3 Paisagem | A3 | Paisagem | Planimetrias |

### Elementos do Modelo

Cada modelo inclui:
- **Area do mapa** - Vista principal
- **Cabecalho** - Titulo e informacoes do projeto
- **Escala** - Barra de escala grafica
- **Norte** - Seta do norte
- **Legenda** - Simbolos das camadas
- **Carimbo** - Informacoes tecnicas

## Personalizacao

### Informacoes Editaveis

| Campo | Descricao |
|-------|-----------|
| Titulo | Nome do mapa |
| Subtitulo | Descricao adicional |
| Sitio | Nome do sitio arqueologico |
| Area | Numero da area |
| Data | Data de criacao |
| Autor | Nome do autor |
| Escala | Escala de representacao |

### Estilo do Mapa

Antes de gerar:
1. Configurar estilos das camadas no QGIS
2. Ativar/desativar camadas pretendidas
3. Definir etiquetas
4. Verificar legenda

## Exportacao

### Formatos Disponiveis

| Formato | Utilizacao | Qualidade |
|---------|-----------|-----------|
| PDF | Impressao, arquivo | Vetorial |
| PNG | Web, apresentacoes | Raster |
| SVG | Edicao, publicacao | Vetorial |
| JPG | Web, pre-visualizacao | Raster comprimido |

### Resolucao

| DPI | Utilizacao |
|-----|-----------|
| 96 | Ecra/pre-visualizacao |
| 150 | Publicacao web |
| 300 | Impressao padrao |
| 600 | Impressao de alta qualidade |

## Integracao com Time Manager

### Geracao de Sequencia

Em combinacao com o Time Manager:
1. Configurar Time Manager
2. Para cada nivel estratigrafico:
   - Definir nivel
   - Gerar mapa
   - Guardar com nome progressivo

### Resultado em Animacao

Serie de mapas para:
- Apresentacoes
- Videos time-lapse
- Documentacao progressiva

## Fluxo de Trabalho Tipico

### 1. Preparacao

```
1. Carregar camadas necessarias
2. Configurar estilos adequados
3. Definir sistema de referencia de coordenadas
4. Definir extensao do mapa
```

### 2. Configuracao da Vista

```
1. Ampliar para area de interesse
2. Ativar/desativar camadas
3. Verificar etiquetas
4. Verificar legenda
```

### 3. Geracao

```
1. Clicar em Make your Map
2. Selecionar modelo
3. Preencher informacoes
4. Escolher formato de exportacao
5. Guardar
```

## Boas Praticas

### 1. Antes da Geracao

- Verificar completude dos dados
- Verificar estilos das camadas
- Definir escala adequada

### 2. Modelos

- Utilizar modelos consistentes no projeto
- Personalizar cabecalhos para a instituicao
- Manter normas cartograficas

### 3. Resultado

- Guardar em alta resolucao para impressao
- Manter copia PDF para arquivo
- Utilizar nomenclatura descritiva

## Personalizacao de Modelos

### Modificacao de Modelos

Os modelos QGIS podem ser modificados:
1. Abrir Gestor de Composicoes no QGIS
2. Modificar modelo existente
3. Guardar como novo modelo
4. Disponivel no Make your Map

### Criacao de Modelos

1. Criar nova composicao no QGIS
2. Adicionar elementos necessarios
3. Configurar variaveis para campos dinamicos
4. Guardar na pasta de modelos

## Resolucao de Problemas

### Mapa Vazio

**Causas**:
- Nenhuma camada ativa
- Extensao errada

**Solucoes**:
- Ativar camadas visiveis
- Ampliar para area com dados

### Legenda Incompleta

**Causa**: Camadas nao configuradas corretamente

**Solucao**: Verificar propriedades das camadas no QGIS

### Exportacao Falhou

**Causas**:
- Caminho sem permissao de escrita
- Formato nao suportado

**Solucoes**:
- Verificar permissoes da pasta
- Escolher formato diferente

## Referencias

### Ficheiros Fonte
- `pyarchinitPlugin.py` - Funcao runPrint
- Modelos na pasta `resources/templates/`

### QGIS
- Gestor de Composicoes
- Compositor de Impressao

---

## Tutorial em Video

### Make Your Map
`[Placeholder: video_make_map.mp4]`

**Conteudos**:
- Preparacao da vista
- Utilizacao de modelos
- Personalizacao
- Formatos de exportacao

**Duracao prevista**: 10-12 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/pyarchinit_create_map_animation.html)
