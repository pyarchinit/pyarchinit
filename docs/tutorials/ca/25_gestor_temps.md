# Tutorial 25: Gestor de Temps (GIS Time Controller)

## Introducció

El **Gestor de Temps** (GIS Time Controller) és una eina avançada per visualitzar la seqüència estratigràfica en el temps. Permet "navegar" a través dels nivells estratigràfics usant un control temporal, visualitzant progressivament les US des de la més antiga a la més recent (la formació del lloc).

### Funcionalitats Principals

- Visualització progressiva dels nivells estratigràfics
- Control mitjançant dial/slider
- Modalitat acumulativa o nivell individual
- Generació automàtica d'imatges/vídeo
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
| [x] Modalitat Acumulativa (mostra <= nivell)    |
+--------------------------------------------------+
| [ ] Mostra Matrix          [Stop] [Genera Vídeo]|
+--------------------------------------------------+
| [Preview Matrix/Imatge]                          |
+--------------------------------------------------+
```

### Controls

| Control | Funció |
|---------|--------|
| Checkbox Capa | Selecciona capa a controlar |
| Dial | Navega entre els nivells (rotació) |
| SpinBox | Inserció directa nivell |
| Modalitat Acumulativa | Mostra tots els nivells fins al seleccionat |
| Mostra Matrix | Visualitza Matriu de Harris sincronitzat |

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

## Integració Matrix

### Visualització Sincronitzada

Amb checkbox **"Mostra Matrix"** actiu:
- El Matrix de Harris apareix al panell
- S'actualitza en sincronia amb el nivell
- Ressalta les US del nivell actual

### Generació Imatges

El Gestor de Temps pot generar:
- Captura de pantalla per a cada nivell
- Seqüència d'imatges
- Vídeo time-lapse

## Generació Vídeo/Imatges

### Procés

1. Seleccionar capes a incloure
2. Configurar rang nivells (min-max)
3. Fer clic **"Genera Vídeo"**
4. Esperar elaboració
5. Sortida a carpeta designada

### Sortida

- Imatges PNG per a cada nivell
- Opcional: vídeo MP4 compilat

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
1. Activar "Mostra Matrix"
2. Generar captures de pantalla significatives
3. Opcional: generar vídeo
```

## Templates de Layout

### Càrrega Template

El Gestor de Temps suporta templates QGIS per:
- Layouts d'impressió personalitzats
- Capçaleres i llegendes
- Formats estàndard

### Templates Disponibles

A la carpeta `resources/templates/`:
- Template base
- Template amb Matrix
- Template per vídeo

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
- Generar vídeo per memòries

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
- Generació vídeo
- Integració Matrix

**Durada prevista**: 15-18 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/pyarchinit_timemanager_animation.html)
