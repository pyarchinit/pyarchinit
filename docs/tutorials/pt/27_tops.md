# Tutorial 27: TOPS - Total Open Station

## Introducao

**TOPS** (Total Open Station) e a integracao do PyArchInit com software de codigo aberto para descarregar e converter dados de estacoes totais. Permite a importacao direta de levantamentos topograficos para o sistema PyArchInit.

### O Que e o Total Open Station?

O Total Open Station e software livre para:
- Descarregar dados de estacoes totais
- Conversao de formatos
- Exportacao para formatos compativeis com SIG

O PyArchInit integra o TOPS para simplificar a importacao de dados de escavacao.

## Acesso

### Pelo Menu
**PyArchInit** > **TOPS (Total Open Station)**

## Interface

### Painel Principal

```
+--------------------------------------------------+
|         Total Open Station para PyArchInit        |
+--------------------------------------------------+
| Entrada:                                          |
|   Ficheiro: [___________________] [Procurar]     |
|   Formato de entrada: [ComboBox formatos]        |
+--------------------------------------------------+
| Saida:                                            |
|   Ficheiro: [___________________] [Procurar]     |
|   Formato de saida: [csv | dxf | ...]            |
+--------------------------------------------------+
| [ ] Converter coordenadas                        |
+--------------------------------------------------+
| [Pre-visualizacao de Dados - TableView]           |
+--------------------------------------------------+
|              [Exportar]                           |
+--------------------------------------------------+
```

## Formatos Suportados

### Formatos de Entrada (Estacoes Totais)

| Formato | Fabricante | Extensao |
|---------|-----------|----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV Generico | - | .csv |

### Formatos de Saida

| Formato | Utilizacao |
|---------|-----------|
| CSV | Importacao para Cotas do PyArchInit |
| DXF | Importacao para CAD/SIG |
| GeoJSON | Importacao direta para SIG |
| Shapefile | Padrao SIG |

## Fluxo de Trabalho

### 1. Importar Dados da Estacao Total

```
1. Ligar estacao total ao PC
2. Descarregar ficheiro de dados (formato nativo)
3. Guardar na pasta de trabalho
```

### 2. Conversao com TOPS

```
1. Abrir TOPS no PyArchInit
2. Selecionar ficheiro de entrada (Procurar)
3. Escolher formato de entrada correto
4. Definir ficheiro de saida
5. Escolher formato de saida (CSV recomendado)
6. Clicar em Exportar
```

### 3. Importacao para PyArchInit

Apos exportacao CSV:
1. O sistema pede automaticamente:
   - **Nome do sitio** arqueologico
   - **Unidade de medida** (metros)
   - **Nome do topografo**
2. Os pontos sao carregados como camada QGIS
3. Opcional: copiar para camada de Cotas UE

### 4. Conversao de Coordenadas (Opcional)

Se a caixa de selecao **"Converter coordenadas"** estiver ativa:
- Introduzir desfasamento X, Y, Z
- Aplicar translacao de coordenadas
- Util para sistemas de referencia locais

## Pre-visualizacao de Dados

### TableView

Mostra pre-visualizacao dos dados importados:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Edicao de Dados

- Selecionar linhas a eliminar
- Botao **Eliminar** remove linhas selecionadas
- Util para filtrar pontos desnecessarios

## Integracao com Cotas UE

### Copia Automatica

Apos importacao, o TOPS pode copiar pontos para a camada **"Desenho de Cotas UE"**:
1. O nome do sitio e solicitado
2. A unidade de medida e solicitada
3. O topografo e solicitado
4. Os pontos sao copiados com atributos corretos

### Atributos Preenchidos

| Atributo | Valor |
|----------|-------|
| sito_q | Nome do sitio introduzido |
| area_q | Extraido do point_name |
| unita_misu_q | Unidade introduzida (metros) |
| disegnatore | Nome introduzido |
| data | Data atual |

## Convencoes de Nomenclatura

### Formato point_name

Para extracao automatica da area:
```
[AREA]-[NOME_PONTO]
Exemplo: 1000-P001
```

O sistema separa automaticamente:
- `area_q` = 1000
- `point_name` = P001

## Boas Praticas

### 1. No Campo

- Utilizar nomenclatura consistente para pontos
- Incluir codigo de area no nome do ponto
- Anotar sistema de referencia utilizado

### 2. Importacao

- Verificar formato de entrada correto
- Verificar pre-visualizacao antes de exportar
- Eliminar pontos errados/duplicados

### 3. Pos-Importacao

- Verificar coordenadas no QGIS
- Confirmar camada de Cotas UE
- Associar pontos a UE correta

## Resolucao de Problemas

### Formato Nao Reconhecido

**Causa**: Formato da estacao nao suportado

**Solucao**:
- Exportar da estacao em formato generico (CSV)
- Verificar documentacao da estacao

### Coordenadas Erradas

**Causas**:
- Sistema de referencia diferente
- Desfasamento nao aplicado

**Solucoes**:
- Verificar sistema de referencia do projeto
- Aplicar conversao de coordenadas

### Camada Nao Criada

**Causa**: Erro durante a importacao

**Solucao**:
- Verificar registo de erros
- Verificar formato do ficheiro de saida
- Repetir conversao

## Referencias

### Ficheiros Fonte
- `tabs/tops_pyarchinit.py` - Interface principal
- `gui/ui/Tops2pyarchinit.ui` - Disposicao da UI

### Software Externo
- [Total Open Station](https://tops.iosa.it/) - Software principal
- Documentacao de formatos de estacoes

---

## Tutorial em Video

### Importacao TOPS
`[Placeholder: video_tops.mp4]`

**Conteudos**:
- Descarregamento da estacao total
- Conversao de formatos
- Importacao para PyArchInit
- Integracao com Cotas UE

**Duracao prevista**: 12-15 minutos

---

*Ultima atualizacao: janeiro de 2026*
