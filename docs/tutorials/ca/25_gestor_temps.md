# Tutorial 25: Gestor de Temps (GIS Time Controller)

## Introducció

El **Gestor de Temps** (GIS Time Controller) és una eina avançada per visualitzar la seqüència estratigràfica en el temps. Permet "navegar" a través dels nivells estratigràfics usant un control temporal, visualitzant progressivament les US des de la més antiga a la més recent (la formació del lloc).

### Funcionalitats Principals

- Visualització progressiva dels nivells estratigràfics
- Control mitjançant dial/slider
- Modalitat acumulativa o nivell individual
- Impressió automàtica de les làmines de l'atles, una per nivell
- Integració amb Matriu de Harris

## Accés

### Des del Menú
**PyArchInit** → **Time Manager**

### Prerequisits

- Capa amb camp `order_layer` (índex estratigràfic)
- US amb order_layer emplenat
- Capes carregades a QGIS

## Interfície

### Panell Principal

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Capes disponibles:                                |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] altra_capa                                   |
+--------------------------------------------------+
|              [Dial Circular]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Nivell: [SpinBox: 0-N]                  |
+--------------------------------------------------+
| [ ] Modalitat Acumulativa (mostra <= nivell)    |
+--------------------------------------------------+
| [ ] Mostrar matriu                               |
| [Atlas Impressió Taules Període]                 |
| [Aturar procés d'impressió]                      |
+--------------------------------------------------+
| [Preview Matrix/Imatge]                          |
+--------------------------------------------------+
```

### Controls

| Control | Funció |
|---------|--------|
| Pestanyes (a dalt) | **Sistema de cronologia relativa** (llista de capes, dial i nivell) i **Sistema de cronologia absoluta** (cerca per anys, vegeu «Cronologia absoluta») |
| Checkbox Capa | Selecciona capa a controlar |
| Dial | Navega entre els nivells (rotació) |
| SpinBox | Inserció directa nivell |
| Modalitat Acumulativa | Mostra tots els nivells fins al seleccionat |
| Mostrar matriu | Visualitza Matriu de Harris sincronitzat |

## Camp order_layer

### Què és order_layer?

El camp `order_layer` defineix l'ordre estratigràfic de visualització:
- **0** = Nivell més antic (profund)
- **N** = Nivell més recent (superficial)

És la convenció del botó **Ordre estratigràfic** amb la casella "Ordre: Antic → Recent" activa (configuració predeterminada, vegeu el Tutorial 03): si l'ordenació s'ha calculat al revés, el Gestor de Temps i el mapa mostren la seqüència capgirada.

### Compilació order_layer

A la Fitxa US, pestanya **Ajuda** → **Tool Box**, el botó **Ordre estratigràfic** calcula `order_layer` a partir de les relacions estratigràfiques (vegeu el Tutorial 03); el valor de la US actual apareix al camp sota el botó. Regles:
1. 0 a les US més antigues, valors creixents cap a les més recents (en superfície)
2. US contemporànies poden tenir el mateix valor
3. Seguir la seqüència del Matrix

### Exemple

| US | order_layer | Descripció |
|----|-------------|------------|
| US001 | 4 | Humus superficial |
| US002 | 3 | Estrat de llaurada |
| US003 | 2 | Enderroc |
| US004 | 1 | Pla d'ús |
| US005 | 0 | Fonamentació |

Des de la 5.13.19-alpha les capes US i USM que pyArchInit carrega al mapa (vegeu el Tutorial 14, *Elecció de l'Estil*) es dibuixen en el mateix ordre que fa servir el Gestor de Temps: per cronologia del període i després per `order_layer` (0 = el més antic), de manera que les unitats més recents queden a sobre.

## Modalitats de Visualització

### Modalitat Nivell Individual

Checkbox **NO** actiu:
- Mostra NOMÉS les US del nivell seleccionat
- Útil per aïllar estrats individuals
- Visualització "a llesques"

### Modalitat Acumulativa

Checkbox **ACTIU**:
- Mostra totes les US des del nivell 0 (més antic) fins al seleccionat
- Mostra la formació del lloc, de les US més antigues a les més recents
- Visualització més realista

### Cronologia absoluta

La segona pestanya de la finestra, **Sistema de cronologia absoluta**, treballa amb anys en lloc dels nivells d'`order_layer`: es tria un interval de temps i es carreguen al mapa les US dels períodes que se superposen a aquest interval. Requereix la Periodització emplenada (vegeu el Tutorial 04), amb la **Cronologia inicial** i la **Cronologia final** de cada període i fase: un període sense anys no es troba.

**Controls.**

- **Cronologia inicial** i **Cronologia final**: dues caselles numèriques, que es llegeixen «Mostra l'interval de temps comprès entre l'any: … i l'any …». Els anys van de `-4.000.000` a `2100`: els valors negatius són aC (268 aC = `-268`), els positius dC sense signe (1400 dC = `1400`). L'any més antic va a Cronologia inicial.
- Botó **Visualitza**: inicia la cerca.

**Què fa el botó Visualitza.**

1. Cerca a la Periodització (de tots els llocs de la base de dades) els períodes i les fases la datació dels quals **se superposa** a l'interval, és a dir, que no acaben abans de l'any inicial ni comencen després de l'any final. Si no en troba cap, avisa «There are no Periods in this time interval» (el missatge surt en anglès) i s'atura.
2. Pren les US el període inicial i la fase inicial de les quals coincideixen amb els trobats. Si no n'hi ha cap, avisa «There are no geometries to display» (també en anglès).
3. Carrega al mapa les capes d'aquestes US, amb el mateix mecanisme de càrrega que la Fitxa US (vegeu el Tutorial 03).
4. Actualitza la previsualització de la matriu, si **Mostrar matriu** està actiu: la previsualització segueix les capes marcades i el nivell de la pestanya relativa, no l'interval d'anys.

**Diferència amb la pestanya relativa.** El dial i la modalitat acumulativa **filtren** les capes ja carregades; **Visualitza**, en canvi, **afegeix** al projecte un grup nou de capes a cada clic (els anteriors es queden al projecte). Com a la Fitxa US, amb una base de dades PostgreSQL el mecanisme de càrrega filtra per lloc i no per US individual: les capes mostren tot el lloc.

## Integració Matrix

### Visualització Sincronitzada

Amb checkbox **"Mostrar matriu"** actiu:
- El Matrix de Harris apareix al panell
- S'actualitza en sincronia amb el nivell
- Ressalta les US del nivell actual

### Generació Imatges

El Gestor de Temps pot generar:
- Una làmina per a cada nivell, maquetada amb la plantilla de layout triada (imatge JPG)
- La matriu de Harris d'aquest nivell dins de la làmina, si **Mostrar matriu** està actiu

## Impressió de les Làmines

### Procés

1. Seleccionar capes a incloure
2. Activar **Mostrar matriu** si la matriu ha d'aparèixer a les làmines (si no, la imatge de la matriu de la plantilla queda oculta)
3. Fer clic a **Atlas Impressió Taules Període**
4. A la finestra que s'obre, triar la plantilla de layout (vegeu la nota «Quina plantilla triar» al final) i confirmar
5. Triar la carpeta on desar les làmines
6. Respondre la pregunta de si cal obrir el Layout Designer per retocar la plantilla abans de començar
7. Esperar: una barra de progrés mostra la làmina en curs i, en acabar, un missatge diu on s'han desat
8. Per aturar la generació, fer clic a **Aturar procés d'impressió**: les làmines ja escrites es queden a la carpeta

### Sortida

- Una `Tavola_N.jpg` per a cada nivell (N és el valor d'`order_layer`), a la carpeta triada: el mapa en aquest nivell, en la modalitat activa (acumulativa o nivell individual)
- El títol «Tavola N» i la imatge de la matriu apareixen si la plantilla els preveu (la matriu només amb **Mostrar matriu** actiu)
- Els nivells on cap US té la datació emplenada s'ometen: aquests números falten a la seqüència de fitxers
- Amb una plantilla de dues pàgines cada nivell produeix dues imatges, la segona és `Tavola_N_2.jpg` (vegeu la nota «Fer apta qualsevol plantilla» al final)

**Etiquetes de la làmina.** Mentre genera les làmines de l'atles, el Time Manager posa a les capes triades les etiquetes de la làmina —el número de la unitat dins d'un cercle a les US, la cota als punts— i les treu en acabar la generació, tornant a posar les que hi havia abans. Des de la 5.13.110-alpha les treu en qualsevol cas, fins i tot si una làmina falla: abans, en aquest cas, es quedaven a les capes del projecte i acabaven al fitxer del projecte en desar-lo.

## Flux de Treball Típic

### 1. Preparació

```
1. Obrir projecte QGIS amb capes US
2. Verificar que order_layer estigui emplenat
3. Obrir Gestor de Temps
```

### 2. Selecció Capes

```
1. Seleccionar les capes a controlar
2. Normalment: pyunitastratigrafiche i/o _usm
```

### 3. Navegació

```
1. Usar el dial o spinbox
2. Observar canvi visualització
3. Activar/desactivar modalitat acumulativa
```

### 4. Documentació

```
1. Activar "Mostrar matriu"
2. Imprimir les làmines amb "Atlas Impressió Taules Període"
3. Revisar els fitxers Tavola_N.jpg a la carpeta triada
```

## Templates de Layout

### Càrrega Template

El Gestor de Temps suporta templates QGIS per:
- Layouts d'impressió personalitzats
- Capçaleres i llegendes
- Formats estàndard

### Templates Disponibles

La finestra d'elecció llista els fitxers `.qpt` trobats a la carpeta del plugin, a `resources/dbfiles/` i a `~/pyarchinit_5/bin/profile/template/`:
- `layout_TimeManager`: la plantilla del Time Manager, amb el títol «Tavola N» i la imatge de la matriu
- les plantilles d'impressió del perfil de pyArchInit (per exemple les «Modello adArte…»)
- qualsevol altre `.qpt`, triat amb el botó **Sfoglia...** (Cerca)

## Bones Pràctiques

### 1. order_layer

- Emplenar ABANS d'usar Gestor de Temps
- Usar valors consecutius
- US contemporànies = mateix valor

### 2. Visualització

- Començar des del nivell 0 (més antic)
- Procedir en ordre creixent
- Usar modalitat acumulativa per presentacions

### 3. Documentació

- Capturar screenshots als nivells significatius
- Documentar passatges de fase
- Imprimir les làmines per a les memòries (una per nivell)

## Resolució de Problemes

### Capes No Visibles a la Llista

**Causa**: Capa sense camp order_layer

**Solució**:
- Afegir camp order_layer a la capa
- Emplenar-lo amb valors apropiats

### Cap Canvi Visual

**Causes**:
- order_layer no emplenat
- Filtre no aplicat

**Solucions**:
- Verificar valors order_layer a les US
- Controlar que la capa estigui seleccionada

### Dial No Respon

**Causa**: Cap capa seleccionada

**Solució**: Seleccionar almenys una capa de la llista

## Referències

### Fitxers Font
- `tabs/Gis_Time_controller.py` - Interfície principal
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Camp Base de Dades
- `us_table.order_layer` - Índex estratigràfic

---

## Vídeo Tutorial

### Gestor de Temps
`[Placeholder: video_gestor_temps.mp4]`

**Continguts**:
- Configuració order_layer
- Navegació temporal
- Impressió de les làmines
- Integració Matrix

**Durada prevista**: 15-18 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/pyarchinit_timemanager_animation.html)

---

## La matriu, des de la 5.13.44

La matriu del Time Manager ja no passa per Graphviz. La dibuixa el mateix motor de composició del plafó **Veure la matriu**, dins de QGIS i sense subprocessos.

- **És immediata.** Al lloc d'exemple (51 UE, 81 relacions) el dibuix costa uns mil·lisegons en lloc d'unes tres dècimes de segon, i han desaparegut els processos `dot` i `tred` que de vegades es penjaven. Els períodes del lloc es llegeixen **una sola vegada**.
- **A l'atles la matriu és vectorial.** La imatge de la làmina és un SVG de poques desenes de KB en lloc d'un JPEG de megabytes.
- **És la mateixa matriu** del plafó Extended Matrix: mateixes franges de període, mateixa simbologia, mateixa reducció de redundàncies. Les fletxes que **pugen** les franges — on l'estratigrafia contradiu la cronologia — es dibuixen en **vermell**.
- La matriu continua contenint només les UE visibles a la posició actual del dial.

- Les UE que **no són visibles** a la posició actual però que una relació esmenta entren igualment al dibuix, **atenuades**: sense elles la seqüència semblaria trencada.

> **Quina plantilla triar.** Al selector cada plantilla està marcada: **✓** té el títol i la imatge de la matriu, **•** només el mapa, **✗** no té mapa. Abans triar-ne una sense aquests elements feia tornar enrere el generador sense dir res.

> **Fer apta qualsevol plantilla.** `scripts/prepare_atlas_templates.py`, executat amb el Python del QGIS, escriu al costat de cada plantilla una còpia amb el sufix « + Time Manager» amb el títol i la imatge de la matriu en una **pàgina nova**. Els originals no es toquen.
