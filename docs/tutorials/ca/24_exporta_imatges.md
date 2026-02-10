# Tutorial 24: Exporta Imatges

## Introducció

La funció **Exporta Imatges** permet exportar en massa les imatges associades als registres arqueològics, organitzant-les automàticament en carpetes per període, fase, tipus d'entitat.

## Accés

### Des del Menú
**PyArchInit** → **Exporta Imatges**

## Interfície

### Panell Export

```
+--------------------------------------------------+
|           Exporta Imatges                         |
+--------------------------------------------------+
| Lloc: [ComboBox selecció lloc]                   |
| Any: [ComboBox any excavació]                    |
+--------------------------------------------------+
| Tipus Export:                                     |
|   [o] Totes les imatges                          |
|   [ ] Només US                                   |
|   [ ] Només Troballes                            |
|   [ ] Només Pottery                              |
+--------------------------------------------------+
| [Obre Carpeta]           [Exporta]               |
+--------------------------------------------------+
```

### Opcions Export

| Opció | Descripció |
|-------|------------|
| Totes les imatges | Exporta tot el material fotogràfic |
| Només US | Exporta només imatges connectades a US |
| Només Troballes | Exporta només imatges de les troballes |
| Només Pottery | Exporta només imatges ceràmica |

## Estructura Sortida

### Organització Carpetes

L'export crea una estructura jeràrquica:

```
pyarchinit_image_export/
└── [Nom Lloc] - Totes les imatges/
    ├── Període - 1/
    │   ├── Fase - 1/
    │   │   ├── US_001/
    │   │   │   ├── foto_001.jpg
    │   │   │   └── foto_002.jpg
    │   │   └── US_002/
    │   │       └── foto_003.jpg
    │   └── Fase - 2/
    │       └── US_003/
    │           └── foto_004.jpg
    └── Període - 2/
        └── ...
```

### Convenció Noms

Els fitxers mantenen el nom original, organitzats per:
1. **Període** - Període cronològic inicial
2. **Fase** - Fase cronològica inicial
3. **Entitat** - US, Troballa, etc.

## Procés d'Export

### Pas 1: Selecció Paràmetres

1. Seleccionar el **Lloc** del ComboBox
2. Seleccionar l'**Any** (opcional)
3. Escollir el **Tipus d'export**

### Pas 2: Execució

1. Fer clic **"Exporta"**
2. Esperar finalització
3. Missatge de confirmació

### Pas 3: Verificació

1. Fer clic **"Obre Carpeta"**
2. Verificar estructura creada
3. Controlar completesa

## Carpeta de Sortida

### Ruta Estàndard

```
~/pyarchinit/pyarchinit_image_export/
```

### Contingut

- Carpetes organitzades per lloc
- Subcarpetes per període/fase
- Imatges originals (no redimensionades)

## Filtre per Any

El ComboBox **Any** permet:
- Exportar només imatges d'una campanya específica
- Organitzar export per any d'excavació
- Reduir mida export

## Bones Pràctiques

### 1. Abans de l'Export

- Verificar connexions imatges-entitats
- Controlar periodització US
- Assegurar-se d'espai en disc suficient

### 2. Durant l'Export

- No interrompre el procés
- Esperar missatge de finalització

### 3. Després de l'Export

- Verificar estructura carpetes
- Controlar completesa imatges
- Crear còpia de seguretat si cal

## Usos Típics

### Preparació Memòria

```
1. Seleccionar lloc
2. Exportar totes les imatges
3. Utilitzar estructura per capítols memòria
```

### Lliurament Superintendència

```
1. Seleccionar lloc i any
2. Exportar per tipologia requerida
3. Organitzar segons estàndards ministerials
```

### Còpia de Seguretat Campanya

```
1. A fi de campanya, exportar tot
2. Arxivar a emmagatzematge extern
3. Verificar integritat
```

## Resolució de Problemes

### Export Incomplet

**Causes**:
- Imatges no connectades
- Rutes fitxers errònies

**Solucions**:
- Verificar connexions al Gestor Media
- Controlar existència fitxer font

### Estructura No Correcta

**Causes**:
- Periodització absent
- US sense període/fase

**Solucions**:
- Emplenar periodització US
- Assignar període/fase a totes les US

## Referències

### Fitxers Font
- `tabs/Images_directory_export.py` - Interfície export
- `gui/ui/Images_directory_export.ui` - Layout UI

### Carpetes
- `~/pyarchinit/pyarchinit_image_export/` - Sortida export

---

## Vídeo Tutorial

### Export Imatges
`[Placeholder: video_exporta_imatges.mp4]`

**Continguts**:
- Configuració export
- Estructura sortida
- Organització arxiu

**Durada prevista**: 10-12 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../pyarchinit_image_export_animation.html)
