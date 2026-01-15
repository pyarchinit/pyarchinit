# Tutorial 26: Eines Ceràmica (Pottery Tools)

## Introducció

**Eines Ceràmica** és un mòdul avançat per a l'elaboració d'imatges ceràmiques. Ofereix eines per extreure imatges de PDF, generar layouts de taules, processar dibuixos amb AI (PotteryInk) i altres funcionalitats especialitzades per a la documentació ceràmica.

### Funcionalitats Principals

- Extracció imatges de PDF
- Generació layouts taules ceràmiques
- Elaboració imatges amb AI
- Conversió format dibuixos
- Integració amb Fitxa Pottery

## Accés

### Des del Menú
**PyArchInit** → **Pottery Tools**

## Interfície

### Panell Principal

```
+--------------------------------------------------+
|              Eines Ceràmica                       |
+--------------------------------------------------+
| [Tab: Extracció PDF]                             |
| [Tab: Generador Layouts]                         |
| [Tab: Processament Imatges]                      |
| [Tab: PotteryInk AI]                             |
+--------------------------------------------------+
| [Barra de Progrés]                               |
| [Missatges Log]                                  |
+--------------------------------------------------+
```

## Tab Extracció PDF

### Funció

Extreu automàticament les imatges de documents PDF que contenen taules ceràmiques.

### Ús

1. Seleccionar fitxer PDF font
2. Especificar carpeta destinació
3. Fer clic **"Extreu"**
4. Les imatges es desen com a fitxers separats

### Opcions

| Opció | Descripció |
|-------|------------|
| DPI | Resolució extracció (150-600) |
| Format | PNG, JPG, TIFF |
| Pàgines | Totes o rang específic |

## Tab Generador Layouts

### Funció

Genera automàticament taules de ceràmica amb layout estandarditzat.

### Tipus de Layout

| Layout | Descripció |
|--------|------------|
| Graella | Imatges en graella regular |
| Seqüència | Imatges en seqüència numerada |
| Comparació | Layout per comparació |
| Catàleg | Format catàleg amb llegendes |

### Ús

1. Seleccionar imatges a incloure
2. Escollir tipus layout
3. Configurar paràmetres (dimensions, marges)
4. Generar taula

### Paràmetres Layout

| Paràmetre | Descripció |
|-----------|------------|
| Mida pàgina | A4, A3, Custom |
| Orientació | Vertical, Horitzontal |
| Marges | Espai vores |
| Espaiat | Distància entre imatges |
| Llegendes | Text sota imatges |

## Tab Processament Imatges

### Funció

Elaboració per lots d'imatges ceràmiques.

### Operacions Disponibles

| Operació | Descripció |
|----------|------------|
| Redimensiona | Escala imatges |
| Retalla | Crop automàtic/manual |
| Rota | Rotació graus |
| Converteix | Canvi format |
| Optimitza | Compressió qualitat |

### Elaboració per Lots

1. Seleccionar carpeta font
2. Escollir operacions a aplicar
3. Especificar destinació
4. Executar elaboració

## Tab PotteryInk AI

### Funció

Utilitza intel·ligència artificial per:
- Conversió foto → dibuix tècnic
- Reconeixement formes ceràmiques
- Suggeriments classificació
- Mesurament automàtic

### Requisits

- Entorn virtual Python configurat
- Models AI descarregats (YOLO, etc.)
- GPU recomanada (però no obligatòria)

### Ús

1. Carregar imatge ceràmica
2. Seleccionar tipus elaboració
3. Esperar processament AI
4. Verificar i desar resultat

### Tipus d'Elaboració AI

| Tipus | Descripció |
|-------|------------|
| Ink Conversion | Converteix foto en dibuix tècnic |
| Shape Detection | Reconeix forma del vas |
| Profile Extraction | Extreu perfil ceràmic |
| Decoration Analysis | Analitza decoracions |

## Entorn Virtual

### Setup Automàtic

Al primer inici, Eines Ceràmica:
1. Crea entorn virtual a `~/pyarchinit/bin/pottery_venv/`
2. Instal·la dependències necessàries
3. Descarrega models AI (si es requereixen)

### Dependències

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Verificació Instal·lació

El log mostra l'estat:
```
✓ Entorn virtual creat
✓ Dependències instal·lades
✓ Models descarregats
✓ Eines Ceràmica inicialitzades correctament!
```

## Integració Base de Dades

### Connexió a Fitxa Pottery

Les imatges processades poden ser:
- Connectades automàticament a registres Pottery
- Desades amb metadades apropiades
- Organitzades per lloc/inventari

## Bones Pràctiques

### 1. Qualitat Imatges d'Entrada

- Resolució mínima: 300 DPI
- Il·luminació uniforme
- Fons neutre (blanc/gris)
- Escala mètrica visible

### 2. Elaboració AI

- Verificar sempre resultats AI
- Corregir manualment si cal
- Desar originals i elaborats

### 3. Organització Sortida

- Usar naming consistent
- Organitzar per lloc/campanya
- Mantenir traçabilitat

## Resolució de Problemes

### Entorn Virtual No Creat

**Causes**:
- Python no trobat
- Permisos insuficients

**Solucions**:
- Verificar instal·lació Python
- Controlar permisos carpeta

### Elaboració AI Lenta

**Causes**:
- Cap GPU disponible
- Imatges massa grans

**Solucions**:
- Reduir mida imatges
- Usar CPU (més lent però funciona)

### Extracció PDF Fallida

**Causes**:
- PDF protegit
- Format no suportat

**Solucions**:
- Verificar protecció PDF
- Provar amb altre software PDF

## Referències

### Fitxers Font
- `tabs/Pottery_tools.py` - Interfície principal
- `modules/utility/pottery_utilities.py` - Utilitats elaboració
- `gui/ui/Pottery_tools.ui` - Layout UI

### Carpetes
- `~/pyarchinit/bin/pottery_venv/` - Entorn virtual
- `~/pyarchinit/models/` - Models AI

---

## Vídeo Tutorial

### Eines Ceràmica Complet
`[Placeholder: video_eines_ceramica.mp4]`

**Continguts**:
- Extracció de PDF
- Generació layouts
- Elaboració AI
- Integració base de dades

**Durada prevista**: 20-25 minuts

---

*Última actualització: Gener 2026*
