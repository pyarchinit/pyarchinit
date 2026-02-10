# Tutorial 29: Crea el teu Mapa

## Introducció

**Crea el teu Mapa** és la funció de PyArchInit per generar mapes i layouts d'impressió professionals directament des de la visualització actual de QGIS. Utilitza els templates de layout predefinits per crear sortides cartogràfiques estandarditzades.

### Funcionalitats

- Generació ràpida de mapes des de vista actual
- Templates predefinits per diversos formats
- Personalització capçaleres i llegendes
- Export en PDF, PNG, SVG

## Accés

### Des de la Barra d'Eines
Icona **"Make your Map"** (impressora) a la barra d'eines PyArchInit

### Des del Menú
**PyArchInit** → **Make your Map**

## Ús Bàsic

### Generació Ràpida

1. Configurar la vista mapa desitjada a QGIS
2. Establir zoom i extensió correctes
3. Fer clic **"Make your Map"**
4. Seleccionar template desitjat
5. Inserir títol i informacions
6. Generar mapa

## Templates Disponibles

### Formats Estàndard

| Template | Format | Orientació | Ús |
|----------|--------|------------|-----|
| A4 Portrait | A4 | Vertical | Documentació estàndard |
| A4 Landscape | A4 | Horitzontal | Vistes extenses |
| A3 Portrait | A3 | Vertical | Taules detallades |
| A3 Landscape | A3 | Horitzontal | Planimetries |

### Elements Template

Cada template inclou:
- **Àrea mapa** - Vista principal
- **Capçalera** - Títol i informacions projecte
- **Escala** - Barra d'escala gràfica
- **Nord** - Fletxa del nord
- **Llegenda** - Símbols capes
- **Caixetí** - Informacions tècniques

## Personalització

### Informacions Inseribles

| Camp | Descripció |
|------|------------|
| Títol | Nom del mapa |
| Subtítol | Descripció addicional |
| Lloc | Nom lloc arqueològic |
| Àrea | Número àrea |
| Data | Data creació |
| Autor | Nom autor |
| Escala | Escala de representació |

### Estil Mapa

Abans de generar:
1. Configurar estils capes a QGIS
2. Activar/desactivar capes desitjades
3. Establir etiquetes
4. Verificar llegenda

## Export

### Formats Disponibles

| Format | Ús | Qualitat |
|--------|-----|----------|
| PDF | Impressió, arxiu | Vectorial |
| PNG | Web, presentacions | Ràster |
| SVG | Edició, publicació | Vectorial |
| JPG | Web, preview | Ràster comprimit |

### Resolució

| DPI | Ús |
|-----|-----|
| 96 | Pantalla/preview |
| 150 | Publicació web |
| 300 | Impressió estàndard |
| 600 | Impressió alta qualitat |

## Integració Gestor de Temps

### Generació Seqüència

En combinació amb Gestor de Temps:
1. Configurar Gestor de Temps
2. Per a cada nivell estratigràfic:
   - Establir nivell
   - Generar mapa
   - Desar amb nom progressiu

### Sortida Animació

Sèrie de mapes per:
- Presentacions
- Vídeo time-lapse
- Documentació progressiva

## Flux de Treball Típic

### 1. Preparació

```
1. Carregar capes necessàries
2. Configurar estils apropiats
3. Establir sistema referència
4. Definir extensió mapa
```

### 2. Configuració Vista

```
1. Fer zoom a l'àrea d'interès
2. Activar/desactivar capes
3. Verificar etiquetes
4. Controlar llegenda
```

### 3. Generació

```
1. Fer clic Make your Map
2. Seleccionar template
3. Emplenar informacions
4. Escollir format export
5. Desar
```

## Bones Pràctiques

### 1. Abans de la Generació

- Verificar completesa dades
- Controlar estils capes
- Establir escala apropiada

### 2. Template

- Usar templates consistents al projecte
- Personalitzar capçaleres per institució
- Mantenir estàndards cartogràfics

### 3. Sortida

- Desar en alta resolució per impressió
- Mantenir còpia PDF per arxiu
- Usar naming descriptiu

## Personalització Templates

### Modificació Template

Els templates QGIS es poden modificar:
1. Obrir Layout Manager a QGIS
2. Modificar template existent
3. Desar com a nou template
4. Disponible a Crea el teu Mapa

### Creació Template

1. Crear nou layout a QGIS
2. Afegir elements necessaris
3. Configurar variables per camps dinàmics
4. Desar a la carpeta templates

## Resolució de Problemes

### Mapa Buit

**Causes**:
- Cap capa activa
- Extensió errònia

**Solucions**:
- Activar capes visibles
- Fer zoom a l'àrea amb dades

### Llegenda Incompleta

**Causa**: Capes no configurades correctament

**Solució**: Verificar propietats capes a QGIS

### Export Fallit

**Causes**:
- Ruta no escrivible
- Format no suportat

**Solucions**:
- Verificar permisos carpeta
- Escollir format diferent

## Referències

### Fitxers Font
- `pyarchinitPlugin.py` - Funció runPrint
- Templates a la carpeta `resources/templates/`

### QGIS
- Layout Manager
- Print Composer

---

## Vídeo Tutorial

### Crea el teu Mapa
`[Placeholder: video_crea_mapa.mp4]`

**Continguts**:
- Preparació vista
- Ús templates
- Personalització
- Export formats

**Durada prevista**: 10-12 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/pyarchinit_create_map_animation.html)
