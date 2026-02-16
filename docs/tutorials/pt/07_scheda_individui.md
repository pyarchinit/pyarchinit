# Tutorial 07: Ficha de Individuo

## Introducao

A **Ficha de Individuo** e o modulo do PyArchInit dedicado a documentacao antropologica de restos humanos encontrados durante a escavacao. Esta ficha regista informacao sobre sexo, idade, posicao do corpo e estado de conservacao do esqueleto.

### Conceitos Basicos

**Individuo no PyArchInit:**
- Um individuo e um conjunto de restos osseos atribuiveis a uma unica pessoa
- Esta ligado a Ficha de Sepultura (contexto de enterramento)
- Esta ligado a Ficha de Estrutura (estrutura fisica)
- Pode estar ligado a Arqueozoologia para analises especificas

**Dados Antropologicos:**
- Estimativa do sexo biologico
- Estimativa da idade a morte
- Posicao e orientacao do corpo
- Estado de conservacao e completude

---

## Aceder a Ficha

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Individual Form**

![Acesso pelo menu](images/07_scheda_individui/02_menu_accesso.png)

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Individual** (figura humana)

![Acesso pela barra de ferramentas](images/07_scheda_individui/03_toolbar_accesso.png)

---

## Panoramica da Interface

A ficha apresenta uma disposicao organizada em seccoes funcionais:

![Interface completa](images/07_scheda_individui/04_interfaccia_completa.png)

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra de Ferramentas DBMS | Navegacao, pesquisa, gravacao |
| 2 | Info BD | Estado do registo, ordenacao, contador |
| 3 | Campos de Identificacao | Sitio, Area, UE, N.o do Individuo |
| 4 | Ligacao a Estrutura | Codigo e numero da estrutura |
| 5 | Area de Separadores | Separadores tematicos para dados especificos |

---

## Barra de Ferramentas DBMS

A barra de ferramentas principal fornece ferramentas para a gestao de registos.

![Barra de Ferramentas DBMS](images/07_scheda_individui/05_toolbar_dbms.png)

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
| ![Novo](../../resources/icons/newrec.png) | Novo registo | Criar um novo registo de individuo |
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
| ![PDF](../../resources/icons/pdf-icon.png) | Exportacao PDF | Exportar para PDF |
| ![Diretorio](../../resources/icons/directoryExp.png) | Abrir diretorio | Abrir pasta de exportacao |

---

## Campos de Identificacao

Os campos de identificacao definem univocamente o individuo na base de dados.

![Campos de identificacao](images/07_scheda_individui/06_campi_identificativi.png)

### Sitio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Selecionar o sitio arqueologico de pertenca.

### Area

**Campo**: `comboBox_area`
**Base de dados**: `area`

Area de escavacao dentro do sitio. Os valores sao preenchidos a partir do thesaurus.

### UE

**Campo**: `comboBox_us`
**Base de dados**: `us`

Unidade Estratigrafica de referencia.

### Numero do Individuo

**Campo**: `lineEdit_individuo`
**Base de dados**: `nr_individuo`

Numero progressivo do individuo. O proximo numero disponivel e proposto automaticamente.

**Notas:**
- A combinacao Sitio + Area + UE + N.o do Individuo deve ser unica
- O numero e atribuido automaticamente na criacao

### Ligacao a Estrutura

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Codigo da estrutura | `sigla_struttura` | Codigo da estrutura (ex.: TM) |
| N.o da estrutura | `nr_struttura` | Numero da estrutura |

Estes campos ligam o individuo a estrutura funeraria.

---

## Dados de Registo

![Dados de registo](images/07_scheda_individui/07_dati_schedatura.png)

### Data de Registo

**Campo**: `dateEdit_schedatura`
**Base de dados**: `data_schedatura`

Data de compilacao da ficha.

### Autor do Registo

**Campo**: `comboBox_schedatore`
**Base de dados**: `schedatore`

Nome do operador que compila a ficha.

---

## Separador Dados Descritivos

O primeiro separador contem dados antropologicos fundamentais.

![Separador Dados Descritivos](images/07_scheda_individui/08_tab_descrittivi.png)

### Estimativa do Sexo

**Campo**: `comboBox_sesso`
**Base de dados**: `sesso`

Estimativa do sexo biologico com base em caracteres morfologicos.

**Valores:**
| Valor | Descricao |
|-------|-----------|
| Masculino | Caracteres masculinos claros |
| Feminino | Caracteres femininos claros |
| Provavel masculino | Caracteres predominantemente masculinos |
| Provavel feminino | Caracteres predominantemente femininos |
| Indeterminado | Nao determinavel |

**Criterios de determinacao:**
- Morfologia da pelve
- Morfologia do cranio
- Robustez geral do esqueleto
- Dimensoes osseas

### Estimativa da Idade a Morte

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Idade minima | `eta_min` | Limite inferior da estimativa |
| Idade maxima | `eta_max` | Limite superior da estimativa |

**Metodos de estimativa:**
- Sinfise pubica
- Superficie auricular
- Suturas cranianas
- Desenvolvimento dentario (para subadultos)
- Epifises osseas (para subadultos)

### Classes Etarias

**Campo**: `comboBox_classi_eta`
**Base de dados**: `classi_eta`

Classificacao por grupo etario.

**Valores tipicos:**
| Classe | Idade aproximada |
|--------|------------------|
| Infans I | 0-6 anos |
| Infans II | 7-12 anos |
| Juvenis | 13-20 anos |
| Adultus | 21-40 anos |
| Maturus | 41-60 anos |
| Senilis | >60 anos |

### Observacoes

**Campo**: `textEdit_osservazioni`
**Base de dados**: `osservazioni`

Campo de texto para notas antropologicas especificas.

**Conteudo recomendado:**
- Patologias observadas
- Traumas
- Marcadores ocupacionais
- Anomalias esqueleticas
- Notas sobre determinacao de sexo e idade

---

## Separador Orientacao e Posicao

Este separador documenta a posicao e orientacao do corpo.

![Separador Orientacao](images/07_scheda_individui/09_tab_orientamento.png)

### Estado de Conservacao

| Campo | Base de dados | Valores |
|-------|---------------|---------|
| Completo | `completo_si_no` | Sim / Nao |
| Perturbado | `disturbato_si_no` | Sim / Nao |
| Em articulacao | `in_connessione_si_no` | Sim / Nao |

**Definicoes:**
- **Completo**: todos os distritos anatomicos estao representados
- **Perturbado**: evidencia de perturbacao pos-deposicional
- **Em articulacao**: as articulacoes estao preservadas

### Comprimento do Esqueleto

**Campo**: `lineEdit_lunghezza`
**Base de dados**: `lunghezza_scheletro`

Comprimento do esqueleto medido in situ (em cm ou m).

### Posicao do Esqueleto

**Campo**: `comboBox_posizione_scheletro`
**Base de dados**: `posizione_scheletro`

Posicao geral do corpo.

**Valores:**
- Decubito dorsal (de costas)
- Decubito ventral (de barriga para baixo)
- Lateral direito
- Lateral esquerdo
- Fletido
- Irregular

### Posicao do Cranio

**Campo**: `comboBox_posizione_cranio`
**Base de dados**: `posizione_cranio`

Orientacao da cabeca.

**Valores:**
- Virado a direita
- Virado a esquerda
- Virado para cima
- Virado para baixo
- Nao determinavel

### Posicao dos Membros Superiores

**Campo**: `comboBox_arti_superiori`
**Base de dados**: `posizione_arti_superiori`

Posicao dos bracos.

**Valores:**
- Estendidos ao longo do corpo
- Sobre a pelve
- Sobre o peito
- Cruzados sobre o peito
- Mistos
- Nao determinavel

### Posicao dos Membros Inferiores

**Campo**: `comboBox_arti_inferiori`
**Base de dados**: `posizione_arti_inferiori`

Posicao das pernas.

**Valores:**
- Estendidos
- Fletidos
- Cruzados
- Afastados
- Nao determinavel

### Orientacao do Eixo

**Campo**: `comboBox_orientamento_asse`
**Base de dados**: `orientamento_asse`

Orientacao do eixo longitudinal do corpo.

**Valores:**
- N-S (cabeca a Norte)
- S-N (cabeca a Sul)
- E-O (cabeca a Este)
- O-E (cabeca a Oeste)
- NE-SO, NO-SE, etc.

### Orientacao Azimutal

**Campo**: `lineEdit_azimut`
**Base de dados**: `orientamento_azimut`

Valor numerico do azimute em graus (0-360).

---

## Separador Restos Osteologicos

Este separador e dedicado a documentacao dos distritos anatomicos.

![Separador Restos Osteologicos](images/07_scheda_individui/10_tab_osteologici.png)

### Documentacao de Distritos

Permite registar:
- Presenca/ausencia de elementos osseos individuais
- Estado de conservacao por distrito
- Lado (direito/esquerdo) para elementos emparelhados

**Distritos principais:**
| Distrito | Elementos |
|----------|----------|
| Cranio | Calota, mandibula, dentes |
| Coluna vertebral | Vertebras cervicais, toracicas, lombares, sacro |
| Torax | Costelas, esterno |
| Membros superiores | Claviculas, escapulas, umeros, radio, cubito, maos |
| Pelve | Coxais |
| Membros inferiores | Femures, tibia, perone, pes |

---

## Separador Outras Caracteristicas

Este separador contem informacao adicional.

![Separador Outras Caracteristicas](images/07_scheda_individui/11_tab_altre.png)

### Conteudos

- Caracteristicas metricas especificas
- Indices antropometricos
- Patologias detalhadas
- Relacoes com outros individuos

---

## Exportacao e Impressao

### Exportacao PDF

O botao PDF abre um painel com opcoes:

| Opcao | Descricao |
|-------|-----------|
| Lista de Individuos | Lista sintetica |
| Fichas de Individuo | Fichas detalhadas completas |
| Imprimir | Gerar PDF |

### Conteudo da Ficha PDF

A ficha PDF inclui:
- Dados de identificacao
- Dados antropologicos (sexo, idade)
- Posicao e orientacao
- Estado de conservacao
- Observacoes

---

## Fluxo de Trabalho Operacional

### Criar um Novo Individuo

1. **Abrir ficha**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar em "New Record"
   - O numero do individuo e proposto automaticamente

3. **Dados de identificacao**
   ```
   Site: Necropole de Isola Sacra
   Area: 1
   UE: 150
   N.o do Individuo: 1
   Codigo da estrutura: TM
   N.o da estrutura: 45
   ```

4. **Dados de registo**
   ```
   Data: 15/03/2024
   Autor: M. Rossi
   ```

5. **Dados antropologicos** (Separador 1)
   ```
   Sexo: Masculino
   Idade minima: 35
   Idade maxima: 45
   Classe etaria: Adultus

   Observacoes: Estatura estimada 170 cm.
   Artrose lombar. Caries multiplas.
   ```

6. **Orientacao e Posicao** (Separador 2)
   ```
   Completo: Sim
   Perturbado: Nao
   Em articulacao: Sim
   Comprimento: 165 cm
   Posicao: Decubito dorsal
   Cranio: Virado a direita
   Membros superiores: Estendidos ao longo do corpo
   Membros inferiores: Estendidos
   Orientacao: E-O
   Azimute: 90
   ```

7. **Restos osteologicos** (Separador 3)
   - Documentar os distritos presentes

8. **Guardar**
   - Clicar em "Save"

### Pesquisar Individuos

1. Clicar em "New Search"
2. Preencher criterios:
   - Sitio
   - Sexo
   - Classe etaria
   - Posicao
3. Clicar em "Search"
4. Navegar pelos resultados

---

## Relacoes com Outras Fichas

| Ficha | Relacao |
|-------|---------|
| **Ficha de Sitio** | O sitio contem individuos |
| **Ficha de Estrutura** | A estrutura contem o individuo |
| **Ficha de Sepultura** | A sepultura documenta o contexto |
| **Arqueozoologia** | Para analises osteologicas especificas |

### Fluxo de Trabalho Recomendado

1. Criar **Ficha de Estrutura** para a sepultura
2. Criar **Ficha de Sepultura**
3. Criar **Ficha de Individuo** para cada esqueleto
4. Ligar o individuo a sepultura e estrutura

---

## Boas Praticas

### Determinacao do Sexo

- Utilizar multiplos indicadores morfologicos
- Indicar o nivel de fiabilidade
- Especificar os criterios utilizados nas observacoes

### Estimativa da Idade

- Fornecer sempre um intervalo (minimo-maximo)
- Indicar os metodos utilizados
- Para subadultos, especificar desenvolvimento dentario e epifisario

### Posicao e Orientacao

- Documentar com fotografias antes da remocao
- Utilizar referencias cardeais
- Medir o azimute com bussola

### Conservacao

- Distinguir perdas tafonomicas de remocoes antigas
- Documentar perturbacoes pos-deposicionais
- Registar as condicoes de recuperacao

---

## Resolucao de Problemas

### Problema: Numero de individuo duplicado

**Causa**: Ja existe um individuo com o mesmo numero.

**Solucao**:
1. Verificar a numeracao existente
2. Utilizar o numero proposto automaticamente
3. Verificar area e UE

### Problema: Estrutura nao encontrada

**Causa**: A estrutura nao existe ou tem um codigo diferente.

**Solucao**:
1. Verificar se a Ficha de Estrutura existe
2. Verificar codigo e numero
3. Criar primeiro a estrutura se necessario

### Problema: Classes etarias nao disponiveis

**Causa**: Thesaurus nao configurado.

**Solucao**:
1. Verificar a configuracao do thesaurus
2. Verificar a definicao de idioma
3. Contactar o administrador

---

## Referencias

### Base de Dados

- **Tabela**: `individui_table`
- **Classe mapper**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Ficheiros Fonte

- **UI**: `gui/ui/Schedaind.ui`
- **Controlador**: `tabs/Schedaind.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Video Tutorial

### Panoramica da Ficha de Individuo
**Duracao**: 5-6 minutos
- Apresentacao da interface
- Campos principais
- Navegacao entre separadores

[Marcador de video: video_panoramica_individui.mp4]

### Documentacao Antropologica Completa
**Duracao**: 12-15 minutos
- Criacao de novo registo
- Determinacao de sexo e idade
- Documentacao da posicao
- Registo de restos osteologicos

[Marcador de video: video_schedatura_individui.mp4]

### Ligacao Sepultura-Individuo
**Duracao**: 5-6 minutos
- Relacoes entre fichas
- Fluxo de trabalho correto
- Boas praticas

[Marcador de video: video_collegamento_tomba_individuo.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
