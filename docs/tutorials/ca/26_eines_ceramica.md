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

### Models d'IA

**Models d'entintat (PotteryInk).** A la pestanya **🏺 PotteryInk**, grup **Enhancement Settings**, la llista **Model:** mostra els models de PyPotteryInk 2.1.2; el botó **Download** del costat baixa el model seleccionat des de Hugging Face (`lrncrd/PyPotteryInk`) a la carpeta `~/pyarchinit_5/bin/models/` (si el fitxer ja existeix, pregunta si es vol tornar a baixar). Cada model ocupa uns 38 MB.

| Model (entrada de la llista) | Fitxer | Ús |
|------------------------------|--------|----|
| 10k Model (General) | `model_10k.pkl` | Model general per a dibuixos de ceràmica |
| 6h-MCG Model (Bronze Age) | `6h-MCG.pkl` | Dibuixos de l'edat del bronze |
| 6h-MC Model (Protohistoric) | `6h-MC.pkl` | Dibuixos protohistòrics i històrics |
| 4h-PAINT Model (Historic/Painted) | `4h-PAINT.pkl` | Ceràmica històrica i pintada |
| 5h-PAPERGRID Model (Paper grid tables) | `5h_PAPERGRID.pkl` | Dibuixos en paper mil·limetrat (làmines quadriculades); no admet ombres |

**Detector de dibuixos (YOLO).** El model `BasicModelv8_v01.pt` de PyPotteryLens, que localitza els dibuixos a les pàgines extretes dels PDF (opció **Auto-detect pottery (ML)** i pestanya **2. Apply Model**), s'instal·la amb el botó **Download YOLO Model** de la pestanya **PDF Extraction**: si troba una còpia local de PyPotteryLens, la copia; si no, el baixa de Hugging Face (`lrncrd/PyPotteryLens`, uns 144 MB) i, si la baixada falla, del fork de GitHub com a alternativa. El fitxer es desa a `~/pyarchinit_5/bin/`; una baixada fallida no deixa fitxers a mitges.

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
1. Crea entorn virtual a `~/pyarchinit_5/bin/pottery_venv/`
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
- `modules/utility/pottery_models.py` - Registre de models (PotteryInk i detector YOLO)
- `gui/ui/Pottery_tools.ui` - Layout UI

### Carpetes
- `~/pyarchinit_5/bin/pottery_venv/` - Entorn virtual
- `~/pyarchinit_5/bin/models/` - Models PotteryInk (`.pkl`)
- `~/pyarchinit_5/bin/BasicModelv8_v01.pt` - Detector YOLO

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

*Última actualització: Octubre 2026*
