# Tutorial 13: Gestió del Tesaurus

## Introducció

El **Tesaurus** de PyArchInit és el sistema centralitzat per a la gestió dels vocabularis controlats. Permet definir i mantenir les llistes de valors utilitzades a totes les fitxes del connector, garantint coherència terminològica i facilitant la cerca.

### Funcions Principals

- Gestió vocabularis per a cada fitxa
- Suport multilingüe
- Sigles i descripcions esteses
- Integració amb GPT per a suggeriments
- Import/export des de fitxer CSV

---

## Accés al Tesaurus

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Tesaurus** (o **Thesaurus form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Tesaurus** (llibre/diccionari)

---

## Panoràmica de la Interfície

### Àrees Principals

| # | Àrea | Descripció |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | Selecció Taula | Elecció de la fitxa a configurar |
| 3 | Camps Sigla | Codi, extensió, tipologia |
| 4 | Descripció | Descripció detallada del terme |
| 5 | Llengua | Selecció llengua |
| 6 | Eines | Import CSV, suggeriments GPT |

---

## Camps del Tesaurus

### Nom Taula

**Camp**: `comboBox_nome_tabella`
**Base de dades**: `nome_tabella`

Selecciona la fitxa per a la qual definir els valors.

**Taules disponibles:**
| Taula | Descripció |
|-------|-------------|
| `us_table` | Fitxa US/USM |
| `site_table` | Fitxa Lloc |
| `periodizzazione_table` | Periodització |
| `inventario_materiali_table` | Inventari Materials |
| `pottery_table` | Fitxa Pottery |
| `campioni_table` | Fitxa Mostres |
| `documentazione_table` | Documentació |
| `tomba_table` | Fitxa Tomba |
| `individui_table` | Fitxa Individus |
| `fauna_table` | Arqueozoologia |
| `ut_table` | Fitxa UT |

### Sigla

**Camp**: `comboBox_sigla`
**Base de dades**: `sigla`

Codi breu/abreviatura del terme.

**Exemples:**
- `MR` per Mur
- `US` per Unitat Estratigràfica
- `CR` per Ceràmica

### Sigla Estesa

**Camp**: `comboBox_sigla_estesa`
**Base de dades**: `sigla_estesa`

Forma completa del terme.

**Exemples:**
- `Mur perimetral`
- `Unitat Estratigràfica`
- `Ceràmica comuna`

### Descripció

**Camp**: `textEdit_descrizione_sigla`
**Base de dades**: `descrizione`

Descripció detallada del terme, definició, notes d'ús.

### Tipologia Sigla

**Camp**: `comboBox_tipologia_sigla`
**Base de dades**: `tipologia_sigla`

Codi numèric que identifica el camp de destinació.

**Estructura codis:**
```
X.Y on:
X = número taula
Y = número camp
```

**Exemples per a us_table:**
| Codi | Camp |
|------|------|
| 1.1 | Definició estratigràfica |
| 1.2 | Mode de formació |
| 1.3 | Tipus US |

### Llengua

**Camp**: `comboBox_lingua`
**Base de dades**: `lingua`

Llengua del terme.

**Llengües suportades:**
- IT (Italià)
- EN_US (Anglès)
- DE (Alemany)
- FR (Francès)
- ES (Espanyol)
- AR (Àrab)
- CA (Català)

---

## Camps Jerarquia

### ID Parent

**Camp**: `comboBox_id_parent`
**Base de dades**: `id_parent`

ID del terme pare (per a estructures jeràrquiques).

### Parent Sigla

**Camp**: `comboBox_parent_sigla`
**Base de dades**: `parent_sigla`

Sigla del terme pare.

### Hierarchy Level

**Camp**: `spinBox_hierarchy`
**Base de dades**: `hierarchy_level`

Nivell a la jerarquia (0=arrel, 1=primer nivell, etc.).

---

## Funcionalitats Especials

### Suggeriments GPT

El botó "Suggeriments" utilitza OpenAI GPT per:
- Generar descripcions automàtiques
- Proporcionar enllaços Wikipedia de referència
- Suggerir definicions en context arqueològic

**Ús:**
1. Seleccionar o inserir un terme a "Sigla estesa"
2. Clic a "Suggeriments"
3. Seleccionar el model GPT
4. Esperar la generació
5. Revisió i desament

**Nota:** Requereix API key OpenAI configurada.

### Import CSV

Per a base de dades SQLite és possible importar vocabularis des de fitxer CSV.

**Format CSV requerit:**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Mur,Estructura muràlia,1.3,CA
us_table,PV,Paviment,Superfície de trepig,1.3,CA
```

**Procediment:**
1. Clic a "Import CSV"
2. Seleccionar el fitxer
3. Confirmar la importació
4. Verificar les dades importades

---

## Flux de Treball Operatiu

### Afegir Nou Terme

1. **Obertura Tesaurus**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Selecció taula**
   ```
   Nom taula: us_table
   ```

4. **Definició terme**
   ```
   Sigla: PO
   Sigla estesa: Pou
   Tipologia sigla: 1.3
   Llengua: CA
   ```

5. **Descripció**
   ```
   Estructura excavada al terreny per
   a l'aprovisionament hidràulic.
   Generalment de forma circular
   amb revestiment en pedra o maons.
   ```

6. **Desament**
   - Clic a "Save"

### Cerca Termes

1. Clic a "New Search"
2. Emplenar criteris:
   - Nom taula
   - Sigla o sigla estesa
   - Llengua
3. Clic a "Search"
4. Navegar entre els resultats

### Modificació Terme Existent

1. Cercar el terme a modificar
2. Modificar els camps necessaris
3. Clic a "Save"

---

## Organització Codis Tipologia

### Estructura Recomanada

Per a cada taula, organitzar els codis de manera sistemàtica:

**us_table (1.x):**
| Codi | Camp |
|------|------|
| 1.1 | Definició estratigràfica |
| 1.2 | Mode formació |
| 1.3 | Tipus US |
| 1.4 | Consistència |
| 1.5 | Color |

**inventario_materiali_table (2.x):**
| Codi | Camp |
|------|------|
| 2.1 | Tipus troballa |
| 2.2 | Classe material |
| 2.3 | Definició |
| 2.4 | Estat conservació |

**pottery_table (3.x):**
| Codi | Camp |
|------|------|
| 3.1 | Form |
| 3.2 | Ware |
| 3.3 | Fabric |
| 3.4 | Surface treatment |

---

## Bones Pràctiques

### Coherència Terminològica

- Usar sempre els mateixos termes per als mateixos conceptes
- Evitar sinònims no documentats
- Documentar les convencions adoptades

### Multilingüe

- Crear els termes a totes les llengües necessàries
- Mantenir les correspondències entre llengües
- Usar traduccions oficials quan estiguin disponibles

### Jerarquia

- Utilitzar l'estructura jeràrquica per a termes correlacionats
- Definir clarament els nivells
- Documentar les relacions

### Manteniment

- Revisar periòdicament els vocabularis
- Eliminar termes obsolets
- Actualitzar les descripcions

---

## Resolució de Problemes

### Problema: Terme no visible als ComboBox

**Causa:** Codi tipologia erroni o llengua no corresponent.

**Solució:**
1. Verificar el codi tipologia_sigla
2. Controlar la llengua establerta
3. Verificar que el registre estigui desat

### Problema: Import CSV fallat

**Causa:** Format fitxer no correcte.

**Solució:**
1. Verificar l'estructura del CSV
2. Controlar els delimitadors (coma)
3. Verificar la codificació (UTF-8)

### Problema: Suggeriments GPT no funcionen

**Causa:** API key absent o no vàlida.

**Solució:**
1. Verificar la configuració API key
2. Controlar la connexió internet
3. Verificar el crèdit OpenAI

---

## Referències

### Base de Dades

- **Taula**: `pyarchinit_thesaurus_sigle`
- **Classe mapper**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Fitxers Font

- **UI**: `gui/ui/Thesaurus.ui`
- **Controller**: `tabs/Thesaurus.py`

---

## Vídeo Tutorial

### Gestió Vocabularis
**Durada**: 10-12 minuts
- Estructura del tesaurus
- Afegir termes
- Organització codis

[Placeholder vídeo: video_thesaurus_gestione.mp4]

### Multilingüe i Import
**Durada**: 8-10 minuts
- Configuració llengües
- Import des de CSV
- Suggeriments GPT

[Placeholder vídeo: video_thesaurus_avanzato.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
