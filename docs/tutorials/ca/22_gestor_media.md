# Tutorial 22: Gestor Media

## Introducció

El **Gestor Media** és l'eina central de PyArchInit per a la gestió de les imatges i dels continguts multimèdia associats als registres arqueològics. Permet connectar fotos, dibuixos, vídeos i altres media a US, troballes, tombes, estructures i altres entitats.

### Funcionalitats Principals

- Gestió centralitzada de tots els media
- Connexió a entitats arqueològiques (US, Troballes, Pottery, Tombes, Estructures, UT)
- Visualització miniatures i imatges a mida original
- Etiquetatge i categorització
- Cerca avançada
- Integració amb GPT per anàlisi d'imatges

## Accés

### Des del Menú
**PyArchInit** → **Media Manager**

### Des de la Barra d'Eines
Icona **Media Manager** a la barra d'eines PyArchInit

## Interfície

### Panell Principal

```
+----------------------------------------------------------+
|                    Gestor Media                           |
+----------------------------------------------------------+
| Lloc: [ComboBox]  Àrea: [ComboBox]  US: [ComboBox]       |
+----------------------------------------------------------+
| [Graella Miniatures Imatges]                              |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags: [Llista etiquetes associades]                       |
+----------------------------------------------------------+
| [Navegació] << < Registre X de Y > >>                     |
+----------------------------------------------------------+
```

### Filtres de Cerca

| Camp | Descripció |
|------|------------|
| Lloc | Filtra per lloc arqueològic |
| Àrea | Filtra per àrea d'excavació |
| US | Filtra per Unitat Estratigràfica |
| Sigla Estructura | Filtra per sigla estructura |
| Nr. Estructura | Filtra per número estructura |

### Controls Miniatures

| Control | Funció |
|---------|--------|
| Slider mida | Ajusta mida miniatures |
| Doble-clic | Obre imatge a mida original |
| Selecció múltiple | Ctrl+clic per seleccionar diverses imatges |

## Gestió Media

### Afegir Noves Imatges

1. Obrir Gestor Media
2. Seleccionar el lloc de destinació
3. Fer clic **"Nou Registre"** o usar el menú contextual
4. Seleccionar les imatges a afegir
5. Emplenar les metadades

### Connectar Media a Entitats

1. Seleccionar la imatge a la graella
2. Al panell Tags, seleccionar:
   - **Tipus entitat**: US, Troballa, Pottery, Tomba, Estructura, UT
   - **Identificador**: Número/codi de l'entitat
3. Fer clic **"Connecta"**

### Tipus d'Entitats Suportades

| Tipus | Taula BD | Descripció |
|-------|----------|------------|
| US | us_table | Unitats Estratigràfiques |
| TROBALLA | inventario_materiali_table | Troballes/Materials |
| CERÀMICA | pottery_table | Ceràmica |
| TOMBA | tomba_table | Sepultures |
| ESTRUCTURA | struttura_table | Estructures |
| UT | ut_table | Unitats Topogràfiques |

### Visualitzar Imatge Original

- **Doble-clic** sobre miniatura
- S'obre visor amb:
  - Zoom (rodeta ratolí)
  - Pan (arrossegament)
  - Rotació
  - Mesurament

## Funcionalitats Avançades

### Cerca Avançada

El Gestor Media suporta cerca per:
- Nom fitxer
- Data inserció
- Entitat connectada
- Tag/categories

### Integració GPT

Botó **"GPT Sketch"** per:
- Anàlisi automàtica de la imatge
- Generació descripció
- Suggeriments de classificació

### Càrrega Remota

Suport per a imatges a servidors remots:
- URL directes
- Servidor FTP
- Emmagatzematge al núvol

## Base de Dades

### Taules Involucrades

| Taula | Descripció |
|-------|------------|
| `media_table` | Metadades media |
| `media_thumb_table` | Miniatures |
| `media_to_entity_table` | Connexions entitats |

### Classes Mapper

- `MEDIA` - Entitat media principal
- `MEDIA_THUMB` - Miniatures
- `MEDIATOENTITY` - Relació media-entitat

## Bones Pràctiques

### 1. Organització Fitxers

- Usar noms de fitxer descriptius
- Organitzar per lloc/àrea/any
- Mantenir còpies de seguretat originals

### 2. Metadades

- Emplenar sempre lloc i àrea
- Afegir descripcions significatives
- Usar etiquetes consistents

### 3. Qualitat Imatges

- Resolució mínima recomanada: 1920x1080
- Format: JPG per fotos, PNG per dibuixos
- Compressió moderada

### 4. Connexions

- Connectar cada imatge a les entitats pertinents
- Verificar connexions després d'import massiu
- Usar la cerca per imatges no connectades

## Resolució de Problemes

### Miniatures No Visualitzades

**Causes**:
- Ruta imatge errònia
- Fitxer absent
- Problemes de permisos

**Solucions**:
- Verificar ruta a base de dades
- Controlar existència fitxer
- Verificar permisos carpeta

### Imatge No Connectable

**Causes**:
- Entitat no existent
- Tipus entitat erroni

**Solucions**:
- Verificar existència registre
- Controlar tipus entitat seleccionat

## Referències

### Fitxers Font
- `tabs/Image_viewer.py` - Interfície principal
- `modules/utility/pyarchinit_media_utility.py` - Utilitats media

### Base de Dades
- `media_table` - Dades media
- `media_to_entity_table` - Connexions

---

## Vídeo Tutorial

### Gestor Media Complet
`[Placeholder: video_gestor_media.mp4]`

**Continguts**:
- Afegir imatges
- Connexió a entitats
- Cerca i filtres
- Funcionalitats avançades

**Durada prevista**: 15-18 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../pyarchinit_media_manager_animation.html)
