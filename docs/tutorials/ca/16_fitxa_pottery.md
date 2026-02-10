# Tutorial 16: Fitxa Pottery (Ceràmica Especialitzada)

## Índex
1. [Introducció](#introducció)
2. [Accés a la Fitxa](#accés-a-la-fitxa)
3. [Interfície d'Usuari](#interfície-dusuari)
4. [Camps Principals](#camps-principals)
5. [Pestanyes de la Fitxa](#pestanyes-de-la-fitxa)
6. [Pottery Tools](#pottery-tools)
7. [Cerca per Similitud Visual](#cerca-per-similitud-visual)
8. [Quantificacions](#quantificacions)
9. [Gestió Media](#gestió-media)
10. [Export i Informes](#export-i-informes)
11. [Flux de Treball Operatiu](#flux-de-treball-operatiu)
12. [Bones Pràctiques](#bones-pràctiques)
13. [Resolució de Problemes](#resolució-de-problemes)

---

## Introducció

La **Fitxa Pottery** és una eina especialitzada per a la catalogació detallada de la ceràmica arqueològica. A diferència de la fitxa Inventari Materials (més generalista), aquesta fitxa està dissenyada específicament per a l'anàlisi ceramològica aprofundida, amb camps dedicats a fabric, ware, decoracions i mesures específiques dels vasos.

### Diferències amb Fitxa Inventari Materials

| Aspecte | Inventari Materials | Pottery |
|---------|---------------------|---------|
| **Objectiu** | Tots els tipus de troballes | Només ceràmica |
| **Detall** | General | Especialitzat |
| **Camps fabric** | Cos ceràmic (genèric) | Fabric detallat |
| **Decoracions** | Camp únic | Interna/Externa separades |
| **Mesures** | Genèriques | Específiques per a vasos |
| **Eines AI** | SketchGPT | PotteryInk, YOLO, Similarity Search |

### Funcionalitats Avançades

La fitxa Pottery inclou funcionalitats AI d'avantguarda:
- **PotteryInk**: Generació automàtica de dibuixos arqueològics des de foto
- **YOLO Detection**: Reconeixement automàtic de formes ceràmiques
- **Visual Similarity Search**: Cerca ceràmiques similars mitjançant embedding visuals
- **Layout Generator**: Generació automàtica de taules ceràmiques

---

## Accés a la Fitxa

### Des del Menú

1. Obrir QGIS amb el connector PyArchInit actiu
2. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

### Des de la Barra d'Eines

1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **Pottery** (icona vas/àmfora ceràmica)

---

## Interfície d'Usuari

L'interfície està organitzada de manera eficient per a la fitxació ceramològica:

### Àrees Principals

| Àrea | Descripció |
|------|------------|
| **1. Header** | DBMS Toolbar, indicadors estat, filtres |
| **2. Identificació** | Lloc, Àrea, US, ID Number, Box, Bag |
| **3. Classificació** | Form, Ware, Fabric, Material |
| **4. Tab Detall** | Description, Technical Data, Supplements |
| **5. Media Panel** | Visor imatges, previsualització |

### Pestanyes Disponibles

| Pestanya | Contingut |
|----------|-----------|
| **Description data** | Descripció, decoracions, notes |
| **Technical Data** | Mesures, tractament superfície, Munsell |
| **Supplements** | Bibliografia, Estadístiques |

---

## Camps Principals

### Camps Identificatius

#### ID Number
- **Tipus**: Integer
- **Obligatori**: Sí
- **Descripció**: Número identificatiu únic del fragment ceràmic
- **Restricció**: Únic per lloc

#### Lloc
- **Tipus**: ComboBox
- **Obligatori**: Sí
- **Descripció**: Lloc arqueològic de procedència

#### Àrea
- **Tipus**: ComboBox editable
- **Descripció**: Àrea d'excavació

#### US (Unitat Estratigràfica)
- **Tipus**: Integer
- **Descripció**: Número de la US de troballa

#### Sector
- **Tipus**: Text
- **Descripció**: Sector específic de troballa

### Camps Dipòsit

#### Box
- **Tipus**: Integer
- **Descripció**: Número de la caixa de dipòsit

#### Bag
- **Tipus**: Integer
- **Descripció**: Número de la bossa

#### Year (Any)
- **Tipus**: Integer
- **Descripció**: Any de troballa/fitxació

### Camps Classificació Ceràmica

#### Form (Forma)
- **Tipus**: ComboBox editable
- **Obligatori**: Recomanat
- **Valors típics**: Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, etc.
- **Descripció**: Forma general del vas

#### Specific Form (Forma Específica)
- **Tipus**: ComboBox editable
- **Descripció**: Tipologia específica (p. ex. Hayes 50, Dressel 1)

#### Specific Shape
- **Tipus**: Text
- **Descripció**: Variant morfològica detallada

#### Ware
- **Tipus**: ComboBox editable
- **Descripció**: Classe ceràmica
- **Exemples**:
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

#### Material
- **Tipus**: ComboBox editable
- **Descripció**: Material base
- **Valors**: Ceramic, Terracotta, Porcelain, etc.

#### Fabric
- **Tipus**: ComboBox editable
- **Descripció**: Tipus de pasta ceràmica
- **Característiques a considerar**:
  - Color de la pasta
  - Granulometria inclusions
  - Duresa
  - Porositat

### Camps Conservació

#### Percent
- **Tipus**: ComboBox editable
- **Descripció**: Percentatge conservat del vas
- **Valors típics**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Tipus**: Integer
- **Descripció**: Nombre de fragments

### Camps Documentació

#### Photo
- **Tipus**: Text
- **Descripció**: Referència fotogràfica

#### Drawing
- **Tipus**: Text
- **Descripció**: Referència dibuix

---

## Pestanyes de la Fitxa

### Pestanya 1: Description Data

Pestanya principal per a la descripció del fragment.

#### Decoracions

| Camp | Descripció |
|------|------------|
| **External Decoration** | Tipus decoració externa |
| **Internal Decoration** | Tipus decoració interna |
| **Description External Deco** | Descripció detallada decoració externa |
| **Description Internal Deco** | Descripció detallada decoració interna |
| **Decoration Type** | Tipologia decorativa (Painted, Incised, Applique, etc.) |
| **Decoration Motif** | Motiu decoratiu (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Posició decoració (Rim, Body, Base, Handle) |

#### Wheel Made
- **Tipus**: ComboBox
- **Valors**: Yes, No, Unknown
- **Descripció**: Indica si el vas ha estat produït al torn

#### Note
- **Tipus**: TextEdit multilínia
- **Descripció**: Notes addicionals i observacions

#### Media Viewer
Àrea per visualitzar les imatges associades:
- Drag & drop per associar imatges
- Doble clic per obrir visor complet
- Botons per gestió etiquetes

### Pestanya 2: Technical Data

Dades tècniques i mesuraments.

#### Munsell Color
- **Tipus**: ComboBox editable
- **Descripció**: Codi color Munsell de la pasta
- **Format**: p. ex. "10YR 7/4", "5YR 6/6"
- **Notes**: Referir-se a la Munsell Soil Color Chart

#### Surface Treatment
- **Tipus**: ComboBox editable
- **Descripció**: Tractament superficial
- **Valors típics**:
  - Slip (engalba)
  - Burnished (brunyit)
  - Glazed (vidriat)
  - Painted (pintat)
  - Plain (simple)

#### Mesures (en cm)

| Camp | Descripció |
|------|------------|
| **Diameter Max** | Diàmetre màxim del vas |
| **Diameter Rim** | Diàmetre de la vora |
| **Diameter Bottom** | Diàmetre del fons |
| **Total Height** | Alçada total (si reconstruïble) |
| **Preserved Height** | Alçada conservada |

#### Datació
- **Tipus**: ComboBox editable
- **Descripció**: Enquadrament cronològic
- **Format**: Textual (p. ex. "I-II s. d.C.")

### Pestanya 3: Supplements

Pestanya amb subseccions per a dades suplementàries.

#### Sub-Tab: Bibliography
Gestió referències bibliogràfiques per a confronts tipològics.

| Columna | Descripció |
|---------|------------|
| Author | Autor/s |
| Year | Any publicació |
| Title | Títol abreujat |
| Page | Pàgina de referència |
| Figure | Figura/Taula |

#### Sub-Tab: Statistic
Accés a les funcionalitats de quantificació i gràfics estadístics.

---

## Pottery Tools

La fitxa Pottery inclou un potent conjunt d'eines AI per a l'elaboració de les imatges ceràmiques.

### Accés a Pottery Tools

1. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

O des del botó dedicat a la fitxa Pottery.

### PotteryInk - Generació Dibuixos

Transforma automàticament les fotos de ceràmica en dibuixos arqueològics estilitzats.

#### Ús

1. Seleccionar una imatge de ceràmica
2. Fer clic a "Generate Drawing"
3. El sistema elabora la imatge amb AI
4. El dibuix es genera en estil arqueològic

#### Requisits
- Entorn virtual dedicat (creat automàticament)
- Models AI pre-entrenats
- GPU recomanada per a rendiment òptim

### YOLO Pottery Detection

Reconeixement automàtic de les formes ceràmiques a les imatges.

#### Funcionalitats

- Identifica automàticament la forma del vas
- Suggereix classificació
- Detecta parts anatòmiques (vora, paret, fons, nansa)

### Layout Generator

Genera automàticament taules ceràmiques per a publicació.

#### Sortida

- Taules en format estàndard arqueològic
- Escala mètrica automàtica
- Disposició optimitzada
- Export en PDF o imatge

### PDF Extractor

Extreu imatges de ceràmica de publicacions PDF per a confronts.

---

## Cerca per Similitud Visual

Funcionalitat avançada per trobar ceràmiques visualment similars a la base de dades.

### Com Funciona

El sistema utilitza **embedding visuals** generats per models de deep learning per representar cada imatge ceràmica com un vector numèric. La cerca troba les ceràmiques amb vectors més similars.

### Ús

1. Seleccionar una imatge de referència
2. Fer clic a "Find Similar"
3. El sistema cerca a la base de dades
4. Es mostren les ceràmiques més similars ordenades per similitud

### Models Disponibles

- **ResNet50**: Bon equilibri velocitat/precisió
- **EfficientNet**: Rendiment òptim
- **CLIP**: Cerca multimodal (text + imatge)

### Actualització Embedding

Els embedding es generen automàticament quan s'afegeixen noves imatges. És possible forçar l'actualització des del menú Pottery Tools.

---

## Quantificacions

### Accés

1. Fer clic al botó **Quant** a la barra d'eines
2. Seleccionar el paràmetre de quantificació
3. Visualitzar el gràfic

### Paràmetres Disponibles

| Paràmetre | Descripció |
|-----------|------------|
| **Fabric** | Distribució per tipus de pasta |
| **US** | Distribució per unitat estratigràfica |
| **Area** | Distribució per àrea d'excavació |
| **Material** | Distribució per material |
| **Percent** | Distribució per percentatge conservat |
| **Shape/Form** | Distribució per forma |
| **Specific form** | Distribució per forma específica |
| **Ware** | Distribució per classe ceràmica |
| **Munsell color** | Distribució per color |
| **Surface treatment** | Distribució per tractament superficial |
| **External decoration** | Distribució per decoració externa |
| **Internal decoration** | Distribució per decoració interna |
| **Wheel made** | Distribució torn sí/no |

### Export Quantificacions

Les dades s'exporten a:
- Fitxer CSV a `pyarchinit_Quantificazioni_folder`
- Gràfic visualitzat a pantalla

---

## Gestió Media

### Associació Imatges

#### Mètodes

1. **Drag & Drop**: Arrossegar imatges a la llista
2. **Botó All Images**: Carrega totes les imatges associades
3. **Search Images**: Cerca imatges específiques

### Video Player

Per a ceràmiques amb documentació vídeo, hi ha disponible un reproductor integrat.

### Cloudinary Integration

Suport per a imatges remotes a Cloudinary:
- Càrrega automàtica miniatures
- Cache local per a rendiment
- Sincronització amb núvol

---

## Export i Informes

### Export PDF Fitxa

Genera una fitxa PDF completa amb:
- Dades identificatives
- Classificació
- Mesures
- Imatges associades
- Notes

### Export Llista

Genera llistat PDF de tots els registres visualitzats.

### Export Dades

Botó per export en format tabular (CSV/Excel).

---

## Flux de Treball Operatiu

### Fitxació Nou Fragment Ceràmic

#### Pas 1: Obertura i Nou Registre
1. Obrir la Fitxa Pottery
2. Fer clic **New record**

#### Pas 2: Dades Identificatives
1. Verificar/seleccionar **Lloc**
2. Inserir **ID Number** (progressiu)
3. Inserir **Àrea**, **US**, **Sector**
4. Inserir **Box** i **Bag**

#### Pas 3: Classificació
1. Seleccionar **Form** (Bowl, Jar, etc.)
2. Seleccionar **Ware** (classe ceràmica)
3. Seleccionar **Fabric** (tipus pasta)
4. Indicar **Material** i **Percent**

#### Pas 4: Dades Tècniques
1. Obrir pestanya **Technical Data**
2. Inserir **Munsell color**
3. Seleccionar **Surface treatment**
4. Inserir les **mesures** (diàmetres, alçades)
5. Indicar **Wheel made**

#### Pas 5: Decoracions (si n'hi ha)
1. Tornar a pestanya **Description data**
2. Seleccionar tipus **External/Internal decoration**
3. Emplenar descripcions detallades
4. Indicar **Decoration type**, **motif**, **position**

#### Pas 6: Documentació
1. Associar fotos (drag & drop)
2. Inserir referència **Photo** i **Drawing**
3. Emplenar **Note** amb observacions

#### Pas 7: Datació i Confronts
1. Inserir **Datació**
2. Obrir pestanya **Supplements** → **Bibliography**
3. Afegir referències bibliogràfiques

#### Pas 8: Desament
1. Fer clic **Save**
2. Verificar confirmació

---

## Bones Pràctiques

### Classificació Coherent

- Utilitzar vocabularis estandarditzats per Form, Ware, Fabric
- Mantenir coherència en la nomenclatura
- Actualitzar el tesaurus quan sigui necessari

### Documentació Fotogràfica

- Fotografiar cada fragment amb escala
- Incloure vista interna i externa
- Documentar detalls decoratius

### Mesuraments

- Usar calibre per a mesures acurades
- Indicar sempre la unitat de mesura (cm)
- Per a fragments, mesurar només parts conservades

### Color Munsell

- Usar sempre la Munsell Soil Color Chart
- Mesurar sobre fractura fresca
- Indicar condicions de llum

### Ús Eines AI

- Verificar sempre els resultats automàtics
- PotteryInk funciona millor amb fotos de bona qualitat
- La similarity search és útil per a confronts, no substitutiva de l'anàlisi

---

## Resolució de Problemes

### Problemes Comuns

#### ID Number duplicat
- **Error**: "Ja existeix un registre amb aquest ID"
- **Solució**: Verificar el proper número disponible

#### Pottery Tools no s'inicia
- **Causa**: Entorn virtual no configurat
- **Solució**:
  1. Verificar connexió internet
  2. Esperar configuració automàtica
  3. Controlar log a `pyarchinit/bin/pottery_venv`

#### PotteryInk lent
- **Causa**: Elaboració CPU en lloc de GPU
- **Solució**:
  1. Instal·lar driver CUDA (NVIDIA)
  2. Verificar que PyTorch usi GPU

#### Similarity Search buit
- **Causa**: Embedding no generats
- **Solució**:
  1. Obrir Pottery Tools
  2. Fer clic "Update Embeddings"
  3. Esperar finalització

#### Imatges no carregades
- **Causa**: Path no correcte o Cloudinary no configurat
- **Solució**:
  1. Verificar configuració path a Settings
  2. Per Cloudinary: verificar credencials

---

## Vídeo Tutorial

### Vídeo 1: Panoràmica Fitxa Pottery
*Durada: 5-6 minuts*

[Placeholder per vídeo]

### Vídeo 2: Fitxació Ceràmica Completa
*Durada: 8-10 minuts*

[Placeholder per vídeo]

### Vídeo 3: Pottery Tools i AI
*Durada: 10-12 minuts*

[Placeholder per vídeo]

### Vídeo 4: Cerca per Similitud
*Durada: 5-6 minuts*

[Placeholder per vídeo]

---

## Resum Camps Base de Dades

| Camp | Tipus | Base de dades | Obligatori |
|------|-------|---------------|------------|
| ID Number | Integer | id_number | Sí |
| Lloc | Text | sito | Sí |
| Àrea | Text | area | No |
| US | Integer | us | No |
| Box | Integer | box | No |
| Bag | Integer | bag | No |
| Sector | Text | sector | No |
| Photo | Text | photo | No |
| Drawing | Text | drawing | No |
| Year | Integer | anno | No |
| Fabric | Text | fabric | No |
| Percent | Text | percent | No |
| Material | Text | material | No |
| Form | Text | form | No |
| Specific Form | Text | specific_form | No |
| Specific Shape | Text | specific_shape | No |
| Ware | Text | ware | No |
| Munsell Color | Text | munsell | No |
| Surface Treatment | Text | surf_trat | No |
| External Decoration | Text | exdeco | No |
| Internal Decoration | Text | intdeco | No |
| Wheel Made | Text | wheel_made | No |
| Descrip. External Deco | Text | descrip_ex_deco | No |
| Descrip. Internal Deco | Text | descrip_in_deco | No |
| Note | Text | note | No |
| Diameter Max | Numeric | diametro_max | No |
| QTY | Integer | qty | No |
| Diameter Rim | Numeric | diametro_rim | No |
| Diameter Bottom | Numeric | diametro_bottom | No |
| Total Height | Numeric | diametro_height | No |
| Preserved Height | Numeric | diametro_preserved | No |
| Decoration Type | Text | decoration_type | No |
| Decoration Motif | Text | decoration_motif | No |
| Decoration Position | Text | decoration_position | No |
| Datació | Text | datazione | No |

---

*Última actualització: Gener 2026*
*PyArchInit - Archaeological Pottery Analysis*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../animations/pyarchinit_pottery_tools_animation.html)
