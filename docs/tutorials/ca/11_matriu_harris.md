# Tutorial 11: Matriu de Harris

## Introducció

La **Matriu de Harris** (o diagrama estratigràfic) és una eina fonamental en arqueologia per representar gràficament les relacions estratigràfiques entre les diverses Unitats Estratigràfiques (US). PyArchInit genera automàticament la Matriu de Harris a partir de les relacions estratigràfiques inserides a les fitxes US.

### Què és la Matriu de Harris?

La Matriu de Harris és un diagrama que representa:
- La **seqüència temporal** de les US (de la més recent a dalt a la més antiga a baix)
- Les **relacions físiques** entre les US (cobreix/cobert per, talla/tallat per, es lliga a)
- La **periodització** de l'excavació (agrupament per períodes i fases)

### Tipus de Relacions Representades

| Relació | Significat | Representació |
|---------|------------|---------------|
| Cobreix/Cobert per | Superposició física | Línia contínua cap avall |
| Talla/Tallat per | Acció negativa (interfície) | Línia discontínua |
| Es lliga a/Igual a | Contemporaneïtat | Línia horitzontal bidireccional |
| Rebleix/Reblert per | Rebliment de tall | Línia contínua |
| S'apoia a/Se li apoia | Assentament estructural | Línia contínua |

## Accés a la Funció

### Des del Menú Principal
1. **PyArchInit** a la barra del menú
2. Seleccionar **Matriu de Harris**

### Des de la Fitxa US
1. Obrir la Fitxa US
2. Pestanya **Map**
3. Botó **"Exporta Matrix"** o **"View Matrix"**

### Prerequisits
- Base de dades connectada correctament
- US amb relacions estratigràfiques emplenades
- Periodització definida (opcional però recomanat)
- Graphviz instal·lat al sistema

## Configuració de la Matriu

### Finestra de Configuració (Setting_Matrix)

Abans de la generació, apareix una finestra de configuració:

#### Pestanya General

| Camp | Descripció | Valor Recomanat |
|------|------------|-----------------|
| DPI | Resolució de la imatge | 150-300 |
| Mostra Períodes | Agrupa US per període/fase | Sí |
| Mostra Llegenda | Inclou llegenda al gràfic | Sí |
| PDF poster | Genera també un PDF pòster multipàgina per imprimir matrius més amples que un full: els fulls se solapen 2 cm i cada full porta l'etiqueta "foglio n/N - riga r/R, colonna c/C - A0 scala 1:x" (full n/N - fila r/R, columna c/C - A0 escala 1:x). Per a matrius molt grans (quan cal reduir el DPI del JPG) el pòster es genera igualment, encara que la casella no estigui marcada | Sí (per a impressió) |
| Formato (Format) | Format dels fulls del pòster: A0, A1, A2, A3 | A0 |
| Scala (Escala) | Escala del pòster: "Adatta all'altezza" (ajusta a l'alçada: una fila de fulls, l'alçada de la matriu omple el full), "Adatta alla pagina" (ajusta a la pàgina: un sol full amb tota la matriu), 1:1, 1:2, 1:3 (escala fixa, més fulls). El dibuix no s'amplia mai; l'orientació (vertical/horitzontal) es tria automàticament per fer servir menys fulls | Adatta all'altezza |

Els controls **PDF poster**, **Formato** i **Scala** són a la segona fila de la finestra (les etiquetes són en italià en tots els idiomes de la interfície).

#### Pestanya Nodes "Ante/Post" (Relacions Normals)

| Paràmetre | Descripció | Opcions |
|-----------|------------|---------|
| Forma node | Forma geomètrica | box, ellipse, diamond |
| Color farciment | Color intern | white, lightblue, etc. |
| Estil | Aspecte vora | solid, dashed |
| Gruix línia | Amplada vora | 0.5 - 2.0 |
| Tipus fletxa | Punta de la fletxa | normal, diamond, none |
| Mida fletxa | Grandària punta | 0.5 - 1.5 |

#### Pestanya Nodes "Negatiu" (Talls)

| Paràmetre | Descripció | Opcions |
|-----------|------------|---------|
| Forma node | Forma geomètrica | box, ellipse, diamond |
| Color farciment | Color distintiu | gray, lightcoral |
| Estil línia | Aspecte connexió | dashed (discontínua) |

#### Pestanya Nodes "Contemporani"

| Paràmetre | Descripció | Opcions |
|-----------|------------|---------|
| Forma node | Forma geomètrica | box, ellipse |
| Color farciment | Color distintiu | lightyellow, white |
| Estil línia | Aspecte connexió | solid |
| Fletxa | Tipus connexió | none (bidireccional) |

## Tipus d'Exportació

### 1. Exportació Matrix Estàndard

Genera la matriu base amb:
- Totes les relacions estratigràfiques
- Agrupament per període/fase
- Disseny vertical (TB - Top to Bottom)

**Sortida**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Exportació Matrix 2ED (Estès)

Versió estesa amb:
- Informacions addicionals als nodes (US + definició + datació)
- Connexions especials (>, >>)
- Exportació també en format GraphML

**Sortida**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. View Matrix (Visualització Ràpida)

Per a visualització veloce sense opcions de configuració:
- Usa configuracions predefinides
- Generació més ràpida
- Ideal per a controls ràpids

## Procés de Generació

### Pas 1: Recollida Dades

El sistema recull automàticament:
```
Per a cada US al lloc/àrea seleccionat:
  - Número US
  - Tipus unitat (US/USM)
  - Relacions estratigràfiques
  - Període i fase inicial
  - Definició interpretativa
```

### Pas 2: Construcció Graf

Creació de les relacions:
```
Seqüència (Ante/Post):
  US1 -> US2 (US1 cobreix US2)

Negatiu (Talls):
  US3 -> US4 (US3 talla US4)

Contemporani:
  US5 <-> US6 (US5 es lliga a US6)
```

### Pas 3: Clustering per Períodes

Agrupament jeràrquic:
```
Lloc
  └── Àrea
      └── Període 1 : Fase 1 : "Època Romana"
          ├── US101
          ├── US102
          └── US103
      └── Període 1 : Fase 2 : "Antiguitat Tardana"
          ├── US201
          └── US202
```

### Pas 4: Reducció Transitiva (tred)

La comanda `tred` de Graphviz elimina les relacions redundants:
- Si US1 -> US2 i US2 -> US3, elimina US1 -> US3
- Simplifica el diagrama
- Manté només relacions directes

### Pas 5: Renderització Final

Generació imatge amb formats múltiples:
- DOT (font Graphviz)
- JPG (imatge comprimida)
- PNG (imatge lossless)

## Interpretació de la Matriu

### Lectura Vertical

```
     [US més recents]
           ↓
        US 001
           ↓
        US 002
           ↓
        US 003
           ↓
     [US més antigues]
```

### Lectura dels Clusters

Els requadres acolorits representen períodes/fases:
- **Blau clar**: Cluster de període
- **Groc**: Cluster de fase
- **Gris**: Fons lloc

### Tipus de Connexions

```
─────────→  Línia contínua = Cobreix/Rebleix/S'apoia
- - - - →  Línia discontínua = Talla
←────────→  Bidireccional = Contemporani/Igual a
```

### Colors dels Nodes

| Color | Significat Típic |
|-------|------------------|
| Blanc | US dipòsit normal |
| Gris | US negativa (tall) |
| Groc | US contemporànies |
| Blau | US amb relacions especials |

## Resolució de Problemes

### Error: "Loop Detected"

**Causa**: Existeixen cicles a les relacions (A cobreix B, B cobreix A)

**Solució**:
1. Obrir la Fitxa US
2. Verificar les relacions de les US indicades
3. Corregir les relacions circulars
4. Regenerar la matriu

### Error: "tred command not found"

**Causa**: Graphviz no instal·lat

**Solució**:
- **Windows**: Instal·lar Graphviz des de graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matriu No Generada

**Causes possibles**:
1. Cap relació estratigràfica inserida
2. US sense període/fase assignat
3. Problemes de permisos a la carpeta de sortida

**Verificació**:
1. Controlar que les US tinguin relacions
2. Verificar la periodització
3. Controlar els permisos de `pyarchinit_Matrix_folder`

### Matriu Massa Gran

**Problema**: Imatge il·legible amb moltes US

**Solucions**:
1. Reduir el DPI (100-150)
2. Filtrar per àrea específica
3. Usar el View Matrix per a àrees individuals
4. Exportar en format vectorial (DOT) i obrir amb yEd

### Matrius de Grans Dimensions

Amb matrius molt grans (p. ex. 1300 US i unes 2000 relacions) l'exportació amb connexions ortogonals podia trigar més de 25 minuts i produir un JPG buit (0 bytes). A partir d'aquesta versió **Exporta Matrix** i **View Matrix** s'adapten automàticament:

| Situació | Què passa |
|----------|-----------|
| Més de **600** relacions | Les connexions passen automàticament d'ortogonals (`ortho`) a polilínies rectes amb espaiat més compacte: la mateixa matriu es compagina en aproximadament un segon. Per sota del llindar l'estil ortogonal no canvia |
| Imatge que supera el límit del renderitzador bitmap (32 767 px per costat) | El DPI de JPG/PNG es redueix automàticament (el valor configurat a Setting_Matrix és un màxim) i al costat de la imatge, a `pyarchinit_Matrix_folder`, es desen les còpies vectorials `.svg` i `.pdf` (`Harris_matrix_tred.dot.svg/.pdf`; per a View Matrix `Harris_matrix_viewtred.dot.svg/.pdf`) |
| Avís "Matrix molto grande" (matriu molt gran: el JPG s'ha generat a N dpi, fes servir els fitxers .svg / .pdf) | Obrir el fitxer `.svg` o `.pdf` (navegador, Inkscape, visor PDF) per a una versió llegible i ampliable sense pèrdua de qualitat |

Els fitxers `.dot` es generen com abans.

**Exportació amb periodització** (casella de períodes a Setting_Matrix):

- L'exportació ja no s'interromp amb l'error `Errore durante il rendering del file DOT: 'NoneType' object has no attribute 'write'`, que apareixia quan Graphviz emetia un avís i QGIS no tenia la consola Python oberta (típic a Windows). Els avisos de Graphviz ara s'escriuen a la consola Python / al registre de QGIS en lloc d'avortar l'exportació.
- En DB grans l'exportació amb períodes és molt més ràpida (la mateixa base de dades de 1311 US ha passat d'uns 25–45 s i un DOT de 51 MB a uns 3 s) i cada fase obté el seu propi clúster invisible, de manera que Graphviz no ignora silenciosament cap fase.
- Per a matrius amb períodes molt amples el JPG ara es pot generar fins i tot per sota de 12 dpi si cal (com a referència, la matriu de 1311 US amb períodes surt a 49 dpi): és només una visió general; per a la versió llegible fes servir les còpies `.svg` / `.pdf` desades al costat.

**Còpies vectorials i impressió del pòster**:

- Les còpies `.pdf` / `.svg` es mantenen ara sempre dins de 200 polzades (14 400 pt) per costat, el límit a partir del qual Acrobat i Previsualització mostren només una part de la pàgina: tota la matriu queda així visible i ampliable (vectorial, sense pèrdua de qualitat). A la base de dades de 1311 US amb períodes el PDF fa 14 400 × 2 591 pt.
- Per imprimir-la fes servir el PDF pòster (casella **PDF poster** a Setting_Matrix): per a la mateixa base de dades, A0 amb "Adatta all'altezza" (ajusta a l'alçada) dona 5 fulls A0 horitzontals a escala 1:3,4 (text ≈ 4 pt: llegible en un plòter; fes servir A0 "1:2" o "1:1" per a text més gran i més fulls). Un sol full A0 ("Adatta alla pagina", ajusta a la pàgina) és només una visió general.

### US No Agrupades per Període

**Causa**: Falta la periodització o no està habilitada

**Solució**:
1. Emplenar la Fitxa Periodització
2. Assignar període/fase inicial a les US
3. Habilitar "Mostra Períodes" a les configuracions

## Sortida i Fitxers Generats

### Carpeta de Sortida

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Font Graphviz
├── Harris_matrix_tred.dot      # Després de reducció transitiva
├── Harris_matrix_tred.dot.jpg  # Imatge final JPG
├── Harris_matrix_tred.dot.png  # Imatge final PNG
├── Harris_matrix_tred.dot.svg  # Vectorial (només matrius grans)
├── Harris_matrix_tred.dot.pdf  # Vectorial (només matrius grans)
├── Harris_matrix_poster_A0.pdf # PDF pòster multipàgina per a impressió
├── Harris_matrix2ED.dot        # Versió estesa
├── Harris_matrix2ED_graphml.dot # Per exportació GraphML
└── matrix_error.txt            # Log errors
```

### Ús dels Fitxers

| Fitxer | Ús |
|--------|-----|
| *.jpg/*.png | Inserció a informes |
| *.dot | Modificació amb editor Graphviz |
| _graphml.dot | Import a yEd per a edició avançada |
| *.svg/*.pdf | Versió vectorial ampliable (matrius grans) |
| _poster_A0.pdf | PDF pòster multipàgina per a impressió; el nom segueix el format triat (p. ex. `_poster_A3.pdf`), per a Export Matrix 2ED el prefix és `Harris_matrix2ED` |

## Bones Pràctiques

### 1. Abans de la Generació

- Verificar completesa relacions estratigràfiques
- Controlar absència de cicles
- Assignar període/fase a totes les US
- Emplenar la definició interpretativa

### 2. Durant la Compilació US

- Inserir relacions bidireccionals correctes
- Usar terminologia consistent
- Verificar àrea correcta a les relacions

### 3. Optimització Sortida

- Per a impressió: DPI 300
- Per a pantalla: DPI 150
- Per a excavacions complexes: subdividir per àrees

### 4. Control Qualitat

- Confrontar matriu amb documentació d'excavació
- Verificar seqüències lògiques
- Controlar agrupaments per període

## Flux de Treball Complet

### 1. Preparació Dades

```
1. Completar fitxes US amb totes les relacions
2. Emplenar fitxa Periodització
3. Assignar període/fase a les US
4. Verificar consistència dades
```

### 2. Generació Matriu

```
1. Menú PyArchInit → Matriu de Harris
2. Configurar configuracions (DPI, colors)
3. Habilitar cluster per períodes
4. Generar la matriu
```

### 3. Verificació i Correcció

```
1. Controlar la matriu generada
2. Identificar eventuals errors
3. Corregir relacions a les fitxes US
4. Regenerar si cal
```

### 4. Ús Final

```
1. Inserir a memòria d'excavació
2. Exportar per a publicació
3. Arxivar amb documentació
```

## Integració amb Altres Eines

### Exportació per a yEd

El fitxer `_graphml.dot` es pot obrir a yEd per a:
- Edició manual del disseny
- Afegir anotacions
- Exportació en formats diversos

### Exportació per a s3egraph

PyArchInit suporta l'exportació per al sistema s3egraph:
- Format compatible
- Manté relacions estratigràfiques
- Suport per a visualització 3D

## Referències

### Fitxers Font
- `tabs/Interactive_matrix.py` - Interfície interactiva
- `modules/utility/pyarchinit_matrix_exp.py` - Classes HarrisMatrix i ViewHarrisMatrix

### Base de Dades
- `us_table` - Dades US i relacions
- `periodizzazione_table` - Períodes i fases

### Dependències
- Graphviz (dot, tred)
- Python graphviz library

---

## Vídeo Tutorial

### Matriu de Harris - Generació Completa
`[Placeholder: video_matrix_harris.mp4]`

**Continguts**:
- Configuració configuracions
- Generació matriu
- Interpretació resultats
- Resolució problemes comuns

**Durada prevista**: 15-20 minuts

### Matriu de Harris - Edició Avançada amb yEd
`[Placeholder: video_matrix_yed.mp4]`

**Continguts**:
- Exportació per a yEd
- Modificació disseny
- Afegir anotacions
- Re-exportació

**Durada prevista**: 10-12 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/harris_matrix_animation.html)
