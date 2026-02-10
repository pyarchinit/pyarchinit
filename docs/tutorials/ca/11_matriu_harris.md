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
