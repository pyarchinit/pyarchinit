# Tutorial 05: Ficha de Estrutura

## Introducao

A **Ficha de Estrutura** e o modulo do PyArchInit dedicado a documentacao de estruturas arqueologicas. Uma estrutura e um conjunto organizado de Unidades Estratigraficas (UE/UEM) que formam uma entidade construtiva ou funcional reconhecivel, tal como uma parede, um pavimento, uma sepultura, um forno, ou qualquer outro elemento construido.

### Conceitos Basicos

**Estrutura vs Unidade Estratigrafica:**
- Uma **UE** e a unidade individual (camada, corte, enchimento)
- Uma **Estrutura** agrupa varias UEs funcionalmente relacionadas
- Exemplo: uma parede (estrutura) e composta por fundacao, elevacao, argamassa (diferentes UEs)

**Hierarquias:**
- As estruturas podem ter relacoes entre si
- Cada estrutura pertence a um ou mais periodos/fases cronologicos
- As estruturas estao ligadas as UEs que as compoem

---

## Aceder a Ficha

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Structure Management** (ou **Structure form**)

![Acesso pelo menu](images/05_scheda_struttura/02_menu_accesso.png)

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Structure** (edificio estilizado)

![Acesso pela barra de ferramentas](images/05_scheda_struttura/03_toolbar_accesso.png)

---

## Panoramica da Interface

A ficha apresenta uma disposicao organizada em seccoes funcionais:

![Interface completa](images/05_scheda_struttura/04_interfaccia_completa.png)

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra de Ferramentas DBMS | Navegacao, pesquisa, gravacao |
| 2 | Info BD | Estado do registo, ordenacao, contador |
| 3 | Campos de Identificacao | Sitio, Codigo, Numero da estrutura |
| 4 | Campos de Classificacao | Categoria, Tipo, Definicao |
| 5 | Area de Separadores | Separadores tematicos para dados especificos |

---

## Barra de Ferramentas DBMS

A barra de ferramentas principal fornece todas as ferramentas para a gestao de registos.

![Barra de Ferramentas DBMS](images/05_scheda_struttura/05_toolbar_dbms.png)

### Botoes de Navegacao

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Primeiro](../../resources/icons/5_leftArrows.png) | Primeiro reg | Ir para o primeiro registo |
| ![Anterior](../../resources/icons/4_leftArrow.png) | Reg anterior | Ir para o registo anterior |
| ![Seguinte](../../resources/icons/6_rightArrow.png) | Reg seguinte | Ir para o registo seguinte |
| ![Ultimo](../../resources/icons/7_rightArrows.png) | Ultimo reg | Ir para o ultimo registo |

### Botoes CRUD

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Novo](../../resources/icons/newrec.png) | Novo registo | Criar um novo registo de estrutura |
| ![Guardar](../../resources/icons/b_save.png) | Guardar | Guardar alteracoes |
| ![Eliminar](../../resources/icons/delete.png) | Eliminar | Eliminar o registo atual |

### Botoes de Pesquisa

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Nova Pesquisa](../../resources/icons/new_search.png) | Nova pesquisa | Iniciar nova pesquisa |
| ![Pesquisar](../../resources/icons/search.png) | Pesquisar!!! | Executar pesquisa |
| ![Ordenar](../../resources/icons/sort.png) | Ordenar por | Ordenar resultados |
| ![Ver Todos](../../resources/icons/view_all.png) | Ver todos | Ver todos os registos |

### Botoes Especiais

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Pre-vis. Mapa](map_preview.png) | Pre-visualizacao no mapa | Ativar/desativar pre-visualizacao no mapa |
| ![Pre-vis. Media](../../resources/icons/photo.png) | Pre-visualizacao media | Ativar/desativar pre-visualizacao de media |
| ![Desenhar Estrutura](../../resources/icons/iconStrutt.png) | Desenhar estrutura | Desenhar estrutura no mapa |
| ![GIS](../../resources/icons/GIS.png) | Carregar no GIS | Carregar estrutura no mapa |
| ![Camadas](../../resources/icons/layers-icon.png) | Carregar todas | Carregar todas as estruturas |
| ![PDF](../../resources/icons/pdf-icon.png) | Exportacao PDF | Exportar para PDF |
| ![Diretorio](../../resources/icons/directoryExp.png) | Abrir diretorio | Abrir pasta de exportacao |

---

## Campos de Identificacao

Os campos de identificacao definem univocamente a estrutura na base de dados.

![Campos de identificacao](images/05_scheda_struttura/06_campi_identificativi.png)

### Sitio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Selecionar o sitio arqueologico de pertenca. O menu pendente mostra todos os sitios registados na base de dados.

**Notas:**
- Campo obrigatorio
- A combinacao Sitio + Codigo + Numero deve ser unica
- Bloqueado apos a criacao do registo

### Codigo da Estrutura

**Campo**: `comboBox_sigla_struttura`
**Base de dados**: `sigla_struttura`

Codigo alfanumerico que identifica o tipo de estrutura. Convencoes comuns:

| Codigo | Significado | Exemplo |
|--------|-------------|---------|
| WL | Parede | WL 1 |
| ST | Estrutura | ST 5 |
| FL | Pavimento | FL 2 |
| KN | Forno | KN 1 |
| TK | Tanque | TK 3 |
| TB | Sepultura | TB 10 |
| WE | Poco | WE 2 |
| CN | Canal | CN 1 |

**Notas:**
- Editavel com entrada livre
- Bloqueado apos a criacao

### Numero da Estrutura

**Campo**: `numero_struttura`
**Base de dados**: `numero_struttura`

Numero progressivo da estrutura dentro do codigo.

**Notas:**
- Campo numerico
- Deve ser unico para a combinacao Sitio + Codigo
- Bloqueado apos a criacao

---

## Sincronizacao com a Ficha de UE

As estruturas criadas nesta ficha aparecem automaticamente no campo **Structure** da **Ficha de UE** para o mesmo sitio.

### Como funciona a ligacao

1. **Criar a estrutura** preenchendo pelo menos:
   - **Site**: o sitio arqueologico (ex.: "Roma_Forum")
   - **Code**: o codigo da estrutura (ex.: "MUR")
   - **Number**: o numero progressivo (ex.: 1)
   - Guardar o registo

2. **Na Ficha de UE** para o mesmo sitio:
   - O campo **Structure** mostrara a estrutura no formato `CODIGO-NUMERO`
   - Exemplo: "MUR-1", "PV-2", "ST-3"

### Formato de apresentacao

As estruturas aparecem na Ficha de UE no formato:
```
CODIGO_ESTRUTURA - NUMERO_ESTRUTURA
```

**Exemplos:**
| Ficha de Estrutura | Apresentado na Ficha de UE |
|--------------------|---------------------------|
| Site=Roma, Code=MUR, Number=1 | MUR-1 |
| Site=Roma, Code=PV, Number=2 | PV-2 |
| Site=Roma, Code=ST, Number=10 | ST-10 |

### Notas importantes

- A estrutura deve estar **guardada** antes de aparecer na Ficha de UE
- Apenas as estruturas do **mesmo sitio** sao visiveis
- Na Ficha de UE pode **selecionar multiplas estruturas** (selecao multipla com caixas de verificacao)
- Para **remover** uma estrutura da UE: abrir o menu pendente e desmarcar a caixa
- Para **limpar** todas as estruturas: clicar com o botao direito -> "Clear Structure field"

---

## Campos de Classificacao

Os campos de classificacao definem a natureza da estrutura.

![Campos de classificacao](images/05_scheda_struttura/07_campi_classificazione.png)

### Categoria da Estrutura

**Campo**: `comboBox_categoria_struttura`
**Base de dados**: `categoria_struttura`

Macrocategoria funcional da estrutura.

**Valores tipicos:**
- Residencial
- Produtiva
- Funeraria
- Religiosa
- Defensiva
- Hidraulica
- Viaria
- Artesanal

### Tipo da Estrutura

**Campo**: `comboBox_tipologia_struttura`
**Base de dados**: `tipologia_struttura`

Tipo especifico dentro da categoria.

**Exemplos por categoria:**
| Categoria | Tipos |
|-----------|-------|
| Residencial | Casa, Villa, Palacio, Cabana |
| Produtiva | Forno, Moinho, Lagar |
| Funeraria | Sepultura em fossa, Sepultura em camara, Sarcofago |
| Hidraulica | Poco, Cisterna, Aqueduto, Canal |

### Definicao da Estrutura

**Campo**: `comboBox_definizione_struttura`
**Base de dados**: `definizione_struttura`

Definicao sintetica e especifica do elemento estrutural.

**Exemplos:**
- Parede perimetral
- Pavimento em cocciopesto
- Soleira em pedra
- Escadaria
- Base de coluna

---

## Separador Dados Descritivos

O primeiro separador contem campos de texto para descricao detalhada.

![Separador Dados Descritivos](images/05_scheda_struttura/08_tab_descrittivi.png)

### Descricao

**Campo**: `textEdit_descrizione_struttura`
**Base de dados**: `descrizione`

Campo de texto livre para descricao fisica da estrutura.

**Conteudo recomendado:**
- Tecnica construtiva
- Materiais utilizados
- Estado de conservacao
- Dimensoes gerais
- Orientacao
- Caracteristicas peculiares

**Exemplo:**
```
Parede em opus incertum construida com blocos de calcario local
de dimensoes variaveis (15-30 cm). Ligante em argamassa de cal
esbranquicada. Conservada ate uma altura maxima de 1,20 m.
Largura media 50 cm. Orientacao NE-SO. Apresenta vestigios
de reboco no lado interno.
```

### Interpretacao

**Campo**: `textEdit_interpretazione_struttura`
**Base de dados**: `interpretazione`

Interpretacao funcional e historica da estrutura.

**Conteudo recomendado:**
- Funcao original hipotetica
- Fases de utilizacao/reutilizacao
- Comparacoes tipologicas
- Enquadramento cronologico
- Relacoes com outras estruturas

**Exemplo:**
```
Parede perimetral norte de um edificio residencial de epoca romana
imperial. A tecnica construtiva e os materiais sugerem uma datacao
do seculo II d.C. Numa fase posterior (seculos III-IV)
a parede foi parcialmente espoliada e incorporada numa
estrutura produtiva.
```

---

## Separador Periodizacao

Este separador gere o enquadramento cronologico da estrutura.

![Separador Periodizacao](images/05_scheda_struttura/09_tab_periodizzazione.png)

### Periodo e Fase Inicial

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Periodo Inicial | `periodo_iniziale` | Periodo de construcao/inicio de utilizacao |
| Fase Inicial | `fase_iniziale` | Fase dentro do periodo |

Os valores sao automaticamente preenchidos com base nos periodos definidos na Ficha de Periodizacao para o sitio selecionado.

### Periodo e Fase Final

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Periodo Final | `periodo_finale` | Periodo de abandono/desativacao |
| Fase Final | `fase_finale` | Fase dentro do periodo |

### Datacao Alargada

**Campo**: `comboBox_datazione_estesa`
**Base de dados**: `datazione_estesa`

Datacao literal calculada automaticamente ou introduzida manualmente.

**Formatos:**
- "Seculo I a.C. - Seculo II d.C."
- "100 a.C. - 200 d.C."
- "Epoca romana imperial"

**Notas:**
- Proposta automaticamente com base no periodo/fase
- Editavel manualmente para casos especiais

---

## Separador Relacoes

Este separador gere as relacoes entre estruturas.

![Separador Relacoes](images/05_scheda_struttura/10_tab_rapporti.png)

### Tabela de Relacoes da Estrutura

**Widget**: `tableWidget_rapporti`
**Base de dados**: `rapporti_struttura`

Regista as relacoes entre a estrutura atual e outras estruturas.

**Colunas:**
| Coluna | Descricao |
|--------|-----------|
| Tipo de relacao | Relacao estratigrafica/funcional |
| Sitio | Sitio da estrutura relacionada |
| Codigo | Codigo da estrutura relacionada |
| Numero | Numero da estrutura relacionada |

**Tipos de relacao:**

| Relacao | Inversa | Descricao |
|---------|---------|-----------|
| Liga-se a | Liga-se a | Ligacao fisica contemporanea |
| Cobre | Coberta por | Relacao de sobreposicao |
| Corta | Cortada por | Relacao de corte |
| Preenche | Preenchida por | Relacao de enchimento |
| Encosta-se a | Suporta | Relacao de encosto |
| Igual a | Igual a | Mesma estrutura com nome diferente |

### Gestao de Linhas

| Botao | Funcao |
|-------|--------|
| + | Adicionar nova linha |
| - | Remover linha selecionada |

---

## Separador Elementos Construtivos

Este separador documenta os materiais e elementos que compoem a estrutura.

![Separador Elementos Construtivos](images/05_scheda_struttura/11_tab_elementi.png)

### Materiais Utilizados

**Widget**: `tableWidget_materiali_impiegati`
**Base de dados**: `materiali_impiegati`

Lista de materiais utilizados na construcao.

**Coluna:**
- Materiais: descricao do material

**Exemplos de materiais:**
- Blocos de calcario
- Tijolos
- Argamassa de cal
- Seixos de rio
- Telhas
- Marmore
- Tufo

### Elementos Estruturais

**Widget**: `tableWidget_elementi_strutturali`
**Base de dados**: `elementi_strutturali`

Lista de elementos construtivos com quantidades.

**Colunas:**
| Coluna | Descricao |
|--------|-----------|
| Tipo de elemento | Tipo de elemento |
| Quantidade | Numero de elementos |

**Exemplos de elementos:**
| Elemento | Quantidade |
|----------|------------|
| Base de coluna | 4 |
| Capitel | 2 |
| Soleira | 1 |
| Bloco esquadrado | 45 |

### Gestao de Linhas

Para ambas as tabelas:
| Botao | Funcao |
|-------|--------|
| + | Adicionar nova linha |
| - | Remover linha selecionada |

---

## Separador Medicoes

Este separador regista as dimensoes da estrutura.

![Separador Medicoes](images/05_scheda_struttura/12_tab_misure.png)

### Tabela de Medicoes

**Widget**: `tableWidget_misurazioni`
**Base de dados**: `misure_struttura`

**Colunas:**
| Coluna | Descricao |
|--------|-----------|
| Tipo de medicao | Tipo de dimensao |
| Unidade de medida | m, cm, m2, etc. |
| Valor | Valor numerico |

### Tipos de Medicao Comuns

| Tipo | Descricao |
|------|-----------|
| Comprimento | Dimensao maior |
| Largura | Dimensao menor |
| Altura conservada | Elevacao conservada |
| Altura original | Elevacao original estimada |
| Profundidade | Para estruturas enterradas |
| Diametro | Para estruturas circulares |
| Espessura | Para paredes, pavimentos |
| Area de superficie | Area em m2 |

### Exemplo de Preenchimento

| Tipo de medicao | Unidade de medida | Valor |
|-----------------|-------------------|-------|
| Comprimento | m | 8,50 |
| Largura | cm | 55 |
| Altura conservada | m | 1,20 |
| Area de superficie | m2 | 4,68 |

---

## Separador Media

Gestao de imagens, videos e modelos 3D associados a estrutura.

![Separador Media](images/05_scheda_struttura/13_tab_media.png)

### Funcionalidades

**Widget**: `iconListWidget`

Apresenta miniaturas dos media associados.

### Botoes

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Todas as Imagens](../../resources/icons/photo2.png) | Todas as imagens | Mostrar todas as imagens |
| ![Remover Tags](../../resources/icons/remove_tag.png) | Remover tags | Remover associacao de media |
| ![Pesquisar](../../resources/icons/search.png) | Pesquisar imagens | Pesquisar imagens na base de dados |

### Arrastar e Largar

Pode arrastar ficheiros diretamente para a ficha:

**Formatos suportados:**
- Imagens: JPG, JPEG, PNG, TIFF, TIF, BMP
- Video: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Visualizacao

- **Duplo clique** na miniatura: abre o visualizador
- Para video: abre o leitor de video integrado
- Para 3D: abre o visualizador 3D PyVista

---

## Separador Mapa

Pre-visualizacao da posicao da estrutura no mapa.

![Separador Mapa](images/05_scheda_struttura/14_tab_map.png)

### Funcionalidades

- Apresenta a geometria da estrutura
- Zoom automatico no elemento
- Integracao com as camadas GIS do projeto

---

## Integracao GIS

### Visualizacao no Mapa

| Botao | Funcao |
|-------|--------|
| Pre-visualizacao no Mapa | Alternar pre-visualizacao no separador Mapa |
| Desenhar Estrutura | Realcar a estrutura no mapa QGIS |
| Carregar no GIS | Carregar camada de estruturas |
| Carregar Todas | Carregar todas as estruturas do sitio |

### Camadas GIS

A ficha utiliza a camada **pyarchinit_strutture** para visualizacao:
- Geometria: poligono ou multipoligono
- Atributos ligados aos campos da ficha

---

## Exportacao e Impressao

### Exportacao PDF

![Painel de Exportacao](images/05_scheda_struttura/15_export_panel.png)

O botao PDF abre um painel com opcoes de exportacao:

| Opcao | Descricao |
|-------|-----------|
| Lista de Estruturas | Lista sintetica de estruturas |
| Fichas de Estrutura | Fichas detalhadas completas |
| Imprimir | Gerar PDF |
| Converter para Word | Converter PDF para formato Word |

### Conversao PDF para Word

Funcionalidade avancada para converter PDFs gerados em documentos Word editaveis:

1. Selecionar o ficheiro PDF a converter
2. Especificar o intervalo de paginas (opcional)
3. Clicar em "Convert"
4. O ficheiro Word e guardado na mesma pasta

---

## Fluxo de Trabalho Operacional

### Criar uma Nova Estrutura

1. **Abrir ficha**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar no botao "New Record"
   - Os campos de identificacao tornam-se editaveis

3. **Dados de identificacao**
   ```
   Site: Villa Romana de Settefinestre
   Code: WL
   Number: 15
   ```

4. **Classificacao**
   ```
   Category: Residencial
   Type: Parede perimetral
   Definition: Parede em opus incertum
   ```

5. **Dados descritivos** (Separador 1)
   ```
   Description: Parede construida em opus incertum com
   blocos de calcario local...

   Interpretation: Limite norte da domus, fase I
   do complexo residencial...
   ```

6. **Periodizacao** (Separador 2)
   ```
   Periodo inicial: I - Fase: A
   Periodo final: II - Fase: B
   Datacao: Seculo I a.C. - Seculo II d.C.
   ```

7. **Relacoes** (Separador 3)
   ```
   Liga-se a: WL 16, WL 17
   Cortada por: ST 5
   ```

8. **Elementos construtivos** (Separador 4)
   ```
   Materiais: Blocos de calcario, Argamassa de cal
   Elementos: Blocos esquadrados (52), Soleira (1)
   ```

9. **Medicoes** (Separador 5)
   ```
   Comprimento: 12,50 m
   Largura: 0,55 m
   Altura conservada: 1,80 m
   ```

10. **Guardar**
    - Clicar em "Save"
    - Verificar a confirmacao de gravacao

### Pesquisar Estruturas

1. Clicar em "New Search"
2. Preencher um ou mais campos de filtro:
   - Sitio
   - Codigo da estrutura
   - Categoria
   - Periodo
3. Clicar em "Search"
4. Navegar pelos resultados

### Modificar Estrutura Existente

1. Navegar ate ao registo desejado
2. Modificar os campos necessarios
3. Clicar em "Save"

---

## Boas Praticas

### Nomenclatura

- Utilizar codigos consistentes ao longo de todo o projeto
- Documentar as convencoes utilizadas
- Evitar numeracao duplicada

### Descricao

- Ser sistematico na descricao
- Seguir um esquema: tecnica > materiais > dimensoes > estado
- Separar descricao objetiva da interpretacao

### Periodizacao

- Ligar sempre aos periodos definidos na Ficha de Periodizacao
- Indicar tanto a fase inicial como a final
- Utilizar a datacao alargada para sintese

### Relacoes

- Registar todas as relacoes significativas
- Verificar a reciprocidade das relacoes
- Ligar as UEs que compoem a estrutura

### Media

- Associar fotografias representativas
- Incluir fotografias de detalhe construtivo
- Documentar as fases de escavacao

---

## Resolucao de Problemas

### Problema: Estrutura nao visivel no mapa

**Causa**: Geometria nao associada ou camada nao carregada.

**Solucao**:
1. Verificar se a camada `pyarchinit_strutture` existe
2. Verificar se a estrutura tem geometria associada
3. Verificar o sistema de coordenadas de referencia

### Problema: Periodos nao disponiveis

**Causa**: Periodos nao definidos para o sitio.

**Solucao**:
1. Abrir a Ficha de Periodizacao
2. Definir periodos para o sitio atual
3. Regressar a Ficha de Estrutura

### Problema: Erro ao guardar "registo existente"

**Causa**: A combinacao Sitio + Codigo + Numero ja existe.

**Solucao**:
1. Verificar a numeracao existente
2. Utilizar um numero progressivo livre
3. Verificar duplicados

### Problema: Media nao apresentados

**Causa**: Caminho das imagens incorreto.

**Solucao**:
1. Verificar o caminho na configuracao
2. Verificar se os ficheiros existem
3. Regenerar miniaturas se necessario

---

## Relacoes com Outras Fichas

| Ficha | Relacao |
|-------|---------|
| **Ficha de Sitio** | O sitio contem estruturas |
| **Ficha de UE** | As UEs compoem as estruturas |
| **Ficha de Periodizacao** | Fornece a cronologia |
| **Ficha de Inventario de Materiais** | Achados associados a estruturas |
| **Ficha de Sepultura** | Sepulturas como tipo especial de estrutura |

---

## Referencias

### Base de Dados

- **Tabela**: `struttura_table`
- **Classe mapper**: `STRUTTURA`
- **ID**: `id_struttura`

### Ficheiros Fonte

- **UI**: `gui/ui/Struttura.ui`
- **Controlador**: `tabs/Struttura.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Video Tutorial

### Panoramica da Ficha de Estrutura
**Duracao**: 5-6 minutos
- Apresentacao geral da interface
- Navegacao entre separadores
- Funcionalidades principais

[Marcador de video: video_panoramica_struttura.mp4]

### Documentacao Completa de Estrutura
**Duracao**: 10-12 minutos
- Criacao de novo registo
- Preenchimento de todos os campos
- Gestao de relacoes e medicoes

[Marcador de video: video_schedatura_struttura.mp4]

### Integracao GIS e Exportacao
**Duracao**: 6-8 minutos
- Visualizacao no mapa
- Carregamento de camadas
- Exportacao PDF e Word

[Marcador de video: video_gis_export_struttura.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
