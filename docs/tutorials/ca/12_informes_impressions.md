# Tutorial 12: Informes i Impressions PDF

## Introducció

PyArchInit ofereix un sistema complet de generació d'**informes PDF** per a totes les fitxes arqueològiques. Aquesta funcionalitat permet exportar la documentació en format imprimible, conforme als estàndards ministerials i preparats per a l'arxivament.

### Tipologies d'Informes Disponibles

| Tipus | Descripció | Fitxa Origen |
|-------|------------|--------------|
| Fitxes US | Informes complets US/USM | Fitxa US |
| Índex US | Llista sintètica US | Fitxa US |
| Fitxes Periodització | Informes períodes/fases | Fitxa Periodització |
| Fitxes Estructura | Informes estructures | Fitxa Estructura |
| Fitxes Troballes | Informes inventari materials | Fitxa Inventari |
| Fitxes Tomba | Informes sepultures | Fitxa Tomba |
| Fitxes Mostres | Informes mostratges | Fitxa Mostres |
| Fitxes Individus | Informes antropològics | Fitxa Individus |

## Accés a la Funció

### Des del Menú Principal
1. **PyArchInit** a la barra del menú
2. Seleccionar **Export PDF**

### Des de la Barra d'Eines
Fer clic a la icona **PDF** a la barra d'eines de PyArchInit

## Interfície d'Exportació

### Panoràmica Finestra

La finestra d'exportació PDF presenta:

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Lloc: [ComboBox selecció lloc]     [v]   |
+------------------------------------------+
| Fitxes a exportar:                        |
| [x] Fitxes US                             |
| [x] Fitxes Periodització                  |
| [x] Fitxes Estructura                     |
| [x] Fitxes Troballes                      |
| [x] Fitxes Tomba                          |
| [x] Fitxes Mostres                        |
| [x] Fitxes Individus                      |
+------------------------------------------+
| [Obre Carpeta]  [Exporta PDF]  [Cancel·la]|
+------------------------------------------+
```

### Selecció Lloc

| Camp | Descripció |
|------|------------|
| ComboBox Lloc | Llista de tots els llocs a la base de dades |

**Nota**: L'exportació es fa per lloc individual. Per exportar diversos llocs, repetir l'operació.

### Checkbox Fitxes

Cada checkbox habilita l'exportació d'un tipus específic:

| Checkbox | Genera |
|----------|--------|
| Fitxes US | Fitxes completes + Índex US |
| Fitxes Periodització | Fitxes períodes + Índex |
| Fitxes Estructura | Fitxes estructures + Índex |
| Fitxes Troballes | Fitxes materials + Índex |
| Fitxes Tomba | Fitxes sepultures + Índex |
| Fitxes Mostres | Fitxes mostres + Índex |
| Fitxes Individus | Fitxes antropològiques + Índex |

## Procés d'Exportació

### Pas 1: Selecció Dades

```python
# El sistema executa per a cada tipus seleccionat:
1. Consulta base de dades per lloc seleccionat
2. Ordenació dades (per número, àrea, etc.)
3. Preparació llista per a generació
```

### Pas 2: Generació PDF

Per a cada tipus de fitxa:
1. **Fitxa individual**: PDF detallat per a cada registre
2. **Índex**: PDF recapitulatiu amb tots els registres

### Pas 3: Desament

Sortida a la carpeta:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Contingut dels Informes

### Fitxa US

Informacions incloses:
- **Dades identificatives**: Lloc, Àrea, Número US, Tipus unitat
- **Definicions**: Estratigràfica, Interpretativa
- **Descripció**: Text descriptiu complet
- **Interpretació**: Anàlisi interpretativa
- **Periodització**: Període/Fase inicial i final
- **Característiques físiques**: Color, consistència, formació
- **Mesures**: Cotes min/max, dimensions
- **Relacions**: Llista relacions estratigràfiques
- **Documentació**: Referències gràfiques i fotogràfiques
- **Dades USM**: (si aplicable) Tècnica muràlia, materials

### Índex US

Taula recapitulativa amb columnes:
| Lloc | Àrea | US | Def. Estratigràfica | Def. Interpretativa | Període |

### Fitxa Periodització

- Lloc
- Número Període
- Número Fase
- Cronologia inicial/final
- Datació estesa
- Descripció període

### Fitxa Estructura

- Dades identificatives (Lloc, Sigla, Número)
- Categoria, Tipologia, Definició
- Descripció i Interpretació
- Periodització
- Materials emprats
- Elements estructurals
- Relacions estructura
- Mesures i cotes

### Fitxa Troballes

- Lloc, Número inventari
- Tipus troballa, Definició
- Descripció
- Procedència (Àrea, US)
- Estat conservació
- Datació
- Elements i mesuraments
- Bibliografia

### Fitxa Tomba

- Dades identificatives
- Ritu (inhumació/cremació)
- Tipus sepultura i deposició
- Descripció i interpretació
- Parament (presència, tipus, descripció)
- Periodització
- Cotes estructura i individu
- US associades

### Fitxa Mostres

- Lloc, Número mostra
- Tipus mostra
- Descripció
- Procedència (Àrea, US)
- Lloc conservació
- Número caixa

### Fitxa Individus

- Dades identificatives
- Sexe, Edat (min/max), Classes edat
- Posició esquelet
- Orientació (eix, azimut)
- Estat conservació
- Observacions

## Llengües Suportades

El sistema genera informes segons la llengua del sistema:

| Llengua | Codi | Template |
|---------|------|----------|
| Italià | IT | `build_*_sheets()` |
| Alemany | DE | `build_*_sheets_de()` |
| Anglès | EN | `build_*_sheets_en()` |

La llengua es detecta automàticament des de les configuracions QGIS.

## Carpeta de Sortida

### Ruta Estàndard
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Estructura Fitxers Generats

```
pyarchinit_PDF_folder/
├── US_[lloc]_fitxes.pdf           # Fitxes US completes
├── US_[lloc]_index.pdf            # Índex US
├── Perioditzacio_[lloc].pdf       # Fitxes Periodització
├── Estructura_[lloc]_fitxes.pdf   # Fitxes Estructura
├── Estructura_[lloc]_index.pdf    # Índex Estructura
├── Troballes_[lloc]_fitxes.pdf    # Fitxes Troballes
├── Troballes_[lloc]_index.pdf     # Índex Troballes
├── Tomba_[lloc]_fitxes.pdf        # Fitxes Tomba
├── Mostres_[lloc]_fitxes.pdf      # Fitxes Mostres
├── Individus_[lloc]_fitxes.pdf    # Fitxes Individus
└── ...
```

### Obertura Carpeta

El botó **"Obre Carpeta"** obre directament el directori de sortida al gestor de fitxers del sistema.

## Personalització Informes

### Templates PDF

Els templates estan definits als mòduls:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Llibreria Utilitzada

Els PDF es generen amb **ReportLab**, que permet:
- Disseny personalitzable
- Inserció imatges
- Taules formatejades
- Capçaleres/peu de pàgina

### Fonts Requerides

El sistema utilitza fonts específiques:
- **Cambria** (font principal)
- Instal·lació automàtica al primer inici del connector

## Flux de Treball Recomanat

### 1. Preparació Dades

```
1. Completar totes les fitxes del lloc
2. Verificar completesa de les dades
3. Controlar periodització
4. Verificar relacions estratigràfiques
```

### 2. Exportació

```
1. Obrir Export PDF
2. Seleccionar el lloc
3. Seleccionar els tipus de fitxes
4. Fer clic "Exporta PDF"
5. Esperar finalització
```

### 3. Verificació

```
1. Obrir carpeta sortida
2. Controlar els PDF generats
3. Verificar formatació
4. Imprimir o arxivar
```

## Resolució de Problemes

### Error: "No form to print"

**Causa**: Cap registre trobat per al tipus seleccionat

**Solució**:
- Verificar que existeixin dades per al lloc seleccionat
- Controlar la base de dades

### PDF Buits o Incomplets

**Causes possibles**:
1. Camps obligatoris no emplenats
2. Problemes de codificació caràcters
3. Fonts absents

**Solucions**:
- Completar els camps obligatoris
- Verificar instal·lació font Cambria

### Error Font

**Causa**: Font Cambria no instal·lada

**Solució**:
- El connector intenta la instal·lació automàtica
- En cas de problemes, instal·lar manualment

### Exportació Lenta

**Causa**: Molts registres a exportar

**Solució**:
- Exportar per tipologia separadament
- Esperar la finalització

## Bones Pràctiques

### 1. Organització

- Exportar regularment durant l'excavació
- Crear còpies de seguretat dels PDF generats
- Organitzar per campanya/any

### 2. Completesa Dades

- Emplenar tots els camps abans de l'exportació
- Verificar les cotes des dels mesuraments GIS
- Controlar les relacions estratigràfiques

### 3. Arxivament

- Desar PDF a emmagatzematge segur
- Incloure a la documentació final
- Annexar a la memòria d'excavació

### 4. Impressió

- Usar paper acid-free per a arxivament
- Imprimir en format A4
- Enquadernar per campanya

## Integració amb Altres Funcions

### Cotes des de GIS

El sistema recupera automàticament:
- Cotes mínimes i màximes des de les geometries
- Referències a les plantes GIS

### Documentació Fotogràfica

Els informes poden incloure referències a:
- Fotografies connectades
- Dibuixos i aixecaments

### Periodització

Els informes US inclouen automàticament:
- Datació estesa des del període/fase assignat
- Referències cronològiques

## Referències

### Fitxers Font
- `tabs/Pdf_export.py` - Interfície exportació
- `modules/utility/pyarchinit_exp_*_pdf.py` - Generadors PDF

### Dependències
- ReportLab (generació PDF)
- Font Cambria

---

## Vídeo Tutorial

### Exportació PDF Complet
`[Placeholder: video_export_pdf.mp4]`

**Continguts**:
- Selecció lloc i fitxes
- Procés d'exportació
- Verificació sortida
- Organització arxiu

**Durada prevista**: 10-12 minuts

---

*Última actualització: Gener 2026*
