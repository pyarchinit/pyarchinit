# Tutorial 25: Gestor de Temps (GIS Time Controller)

## Introducció

El **Gestor de Temps** (GIS Time Controller) és una eina avançada per visualitzar la seqüència estratigràfica en el temps. Permet "navegar" a través dels nivells estratigràfics usant un control temporal, visualitzant progressivament les US des de la més recent a la més antiga.

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
|         Nivell: [SpinBox: 1-N]                  |
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
- **1** = Nivell més recent (superficial)
- **N** = Nivell més antic (profund)

### Compilació order_layer

A la Fitxa US, camp **"Índex Estratigràfic"**:
1. Assignar valors creixents des de la superfície
2. US contemporànies poden tenir el mateix valor
3. Seguir la seqüència del Matrix

### Exemple

| US | order_layer | Descripció |
|----|-------------|------------|
| US001 | 1 | Humus superficial |
| US002 | 2 | Estrat de llaurada |
| US003 | 3 | Enderroc |
| US004 | 4 | Pla d'ús |
| US005 | 5 | Fonamentació |

## Modalitats de Visualització

### Modalitat Nivell Individual

Checkbox **NO** actiu:
- Mostra NOMÉS les US del nivell seleccionat
- Útil per aïllar estrats individuals
- Visualització "a llesques"

### Modalitat Acumulativa

Checkbox **ACTIU**:
- Mostra totes les US fins al nivell seleccionat
- Simula l'excavació progressiva
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

- Començar des de nivell 1 (superficial)
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

[Obre Animació Interactiva](../../pyarchinit_timemanager_animation.html)
