# Tutorial 23: Cerca Imatges

## Introducció

La funció **Cerca Imatges** permet cercar ràpidament imatges a la base de dades PyArchInit filtrant per lloc, tipus d'entitat i altres criteris. És una eina complementària al Gestor Media per a la cerca global.

## Accés

### Des del Menú
**PyArchInit** → **Cerca Imatges**

## Interfície

### Panell de Cerca

```
+--------------------------------------------------+
|           Cerca Imatges                           |
+--------------------------------------------------+
| Filtres:                                          |
|   Lloc: [ComboBox]                               |
|   Tipus Entitat: [-- Tots -- | US | Pottery | ...]|
|   [ ] Només imatges no etiquetades               |
+--------------------------------------------------+
| [Cerca]  [Neteja]                                |
+--------------------------------------------------+
| Resultats:                                        |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Obre Imatge] [Exporta] [Anar al Registre]       |
+--------------------------------------------------+
```

### Filtres Disponibles

| Filtre | Descripció |
|--------|------------|
| Lloc | Selecciona lloc específic o tots |
| Tipus Entitat | US, Pottery, Materials, Tomba, Estructura, UT |
| Només no etiquetades | Mostra només imatges sense connexions |

### Tipus d'Entitat

| Tipus | Descripció |
|-------|------------|
| -- Tots -- | Totes les entitats |
| US | Unitats Estratigràfiques |
| Pottery | Ceràmica |
| Materials | Troballes/Inventari |
| Tomba | Sepultures |
| Estructura | Estructures |
| UT | Unitats Topogràfiques |

## Funcionalitats

### Cerca Bàsica

1. Seleccionar els filtres desitjats
2. Fer clic **"Cerca"**
3. Visualitzar els resultats a la graella

### Accions sobre els Resultats

| Botó | Funció |
|------|--------|
| Obre Imatge | Visualitza imatge a mida original |
| Exporta | Exporta imatge seleccionada |
| Anar al Registre | Obre la fitxa de l'entitat connectada |
| Obre Gestor Media | Obre el Gestor Media amb la imatge seleccionada |

### Menú Contextual (Botó dret)

- **Obre imatge**
- **Exporta imatge...**
- **Anar al registre**

### Cerca Imatges No Etiquetades

Checkbox **"Només imatges no etiquetades"**:
- Troba imatges a la base de dades sense connexions
- Útil per neteja i organització
- Permet identificar imatges a catalogar

## Flux de Treball Típic

### 1. Trobar Imatges d'un Lloc

```
1. Seleccionar lloc del ComboBox
2. Deixar "-- Tots --" per tipus entitat
3. Fer clic Cerca
4. Explorar resultats
```

### 2. Trobar Imatges US Específiques

```
1. Seleccionar lloc
2. Seleccionar "US" com a tipus entitat
3. Fer clic Cerca
4. Doble-clic per obrir imatge
```

### 3. Identificar Imatges No Catalogades

```
1. Seleccionar lloc (o tots)
2. Activar "Només imatges no etiquetades"
3. Fer clic Cerca
4. Per a cada resultat:
   - Obrir imatge
   - Identificar contingut
   - Connectar mitjançant Gestor Media
```

## Exportació

### Export Imatge Individual

1. Seleccionar imatge als resultats
2. Fer clic **"Exporta"** o menú contextual
3. Seleccionar destinació
4. Desar

### Export Múltiple

Per exportar diverses imatges, usar la funció **Exporta Imatges** dedicada (Tutorial 24).

## Bones Pràctiques

### 1. Cerca Eficient

- Usar filtres específics per resultats dirigits
- Començar amb filtres amplis, després restringir
- Usar la cerca no etiquetades periòdicament

### 2. Organització

- Catalogar imatges no etiquetades regularment
- Verificar connexions després d'import
- Mantenir naming consistent

## Resolució de Problemes

### Cap Resultat

**Causes**:
- Filtres massa restrictius
- Cap imatge per als criteris

**Solucions**:
- Ampliar els filtres
- Verificar existència dades

### Imatge No Visualitzable

**Causes**:
- Fitxer no trobat
- Format no suportat

**Solucions**:
- Verificar ruta fitxer
- Controlar format imatge

## Referències

### Fitxers Font
- `tabs/Image_search.py` - Interfície cerca
- `gui/ui/pyarchinit_image_search_dialog.ui` - Layout UI

### Base de Dades
- `media_table` - Dades media
- `media_to_entity_table` - Connexions

---

## Vídeo Tutorial

### Cerca Imatges
`[Placeholder: video_cerca_imatges.mp4]`

**Continguts**:
- Ús filtres
- Cerca avançada
- Export resultats

**Durada prevista**: 8-10 minuts

---

*Última actualització: Gener 2026*
