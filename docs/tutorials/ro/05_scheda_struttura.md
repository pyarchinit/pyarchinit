# Tutorial 05: Fisa Structura

## Introducere

**Fisa Structura** este modulul PyArchInit dedicat documentarii structurilor arheologice. O structura este un ansamblu organizat de Unitati Stratigrafice (US/USM) care formeaza o entitate constructiva sau functionala recognoscibila, cum ar fi un zid, o pardoseala, un mormant, un cuptor sau orice alt element construit.

### Concepte de Baza

**Structura vs Unitate Stratigrafica:**
- O **US** este unitatea singulara (strat, taietura, umplutura)
- O **Structura** grupeaza mai multe US-uri legate functional
- Exemplu: un zid (structura) este compus din fundatie, elevatie, mortar (US-uri diferite)

**Ierarhii:**
- Structurile pot avea relatii intre ele
- Fiecare structura apartine uneia sau mai multor perioade/faze cronologice
- Structurile sunt legate de US-urile care le compun

---

## Accesarea Fisei

### Din Meniu
1. Meniu **PyArchInit** din bara de meniu QGIS
2. Selectati **Gestionare Structuri** (sau **Fisa Structura**)

![Acces din meniu](images/05_scheda_struttura/02_menu_accesso.png)

### Din Bara de Instrumente
1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **Structura** (cladire stilizata)

![Acces din bara](images/05_scheda_struttura/03_toolbar_accesso.png)

---

## Vedere Generala a Interfetei

Fisa prezinta o structura organizata in sectiuni functionale:

![Interfata completa](images/05_scheda_struttura/04_interfaccia_completa.png)

### Zone Principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, cautare, salvare |
| 2 | Info BD | Starea inregistrarii, sortare, contor |
| 3 | Campuri de Identificare | Santier, Cod, Numarul structurii |
| 4 | Campuri de Clasificare | Categorie, Tip, Definitie |
| 5 | Zona de File | File tematice pentru date specifice |

---

## Bara de Instrumente DBMS

Bara principala ofera toate instrumentele pentru gestionarea inregistrarilor.

![Bara DBMS](images/05_scheda_struttura/05_toolbar_dbms.png)

### Butoane de Navigare

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Prima](../../resources/icons/5_leftArrows.png) | Prima inreg. | Mergi la prima inregistrare |
| ![Anterioara](../../resources/icons/4_leftArrow.png) | Inreg. anterioara | Mergi la inregistrarea anterioara |
| ![Urmatoarea](../../resources/icons/6_rightArrow.png) | Inreg. urmatoare | Mergi la inregistrarea urmatoare |
| ![Ultima](../../resources/icons/7_rightArrows.png) | Ultima inreg. | Mergi la ultima inregistrare |

### Butoane CRUD

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Nou](../../resources/icons/newrec.png) | Inregistrare noua | Creeaza o inregistrare noua de structura |
| ![Salvare](../../resources/icons/b_save.png) | Salvare | Salveaza modificarile |
| ![Stergere](../../resources/icons/delete.png) | Stergere | Sterge inregistrarea curenta |

### Butoane de Cautare

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Cautare Noua](../../resources/icons/new_search.png) | Cautare noua | Porneste cautare noua |
| ![Cautare](../../resources/icons/search.png) | Cauta!!! | Executa cautarea |
| ![Sortare](../../resources/icons/sort.png) | Ordoneaza dupa | Sorteaza rezultatele |
| ![Vizualizare Toate](../../resources/icons/view_all.png) | Vizualizare toate | Vizualizeaza toate inregistrarile |

### Butoane Speciale

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Previzualizare Harta](map_preview.png) | Previzualizare harta | Activare/dezactivare previzualizare harta |
| ![Previzualizare Media](../../resources/icons/photo.png) | Previzualizare media | Activare/dezactivare previzualizare media |
| ![Deseneaza Structura](../../resources/icons/iconStrutt.png) | Deseneaza structura | Deseneaza structura pe harta |
| ![GIS](../../resources/icons/GIS.png) | Incarca in GIS | Incarca structura pe harta |
| ![Straturi](../../resources/icons/layers-icon.png) | Incarca toate | Incarca toate structurile |
| ![PDF](../../resources/icons/pdf-icon.png) | Export PDF | Exporta in PDF |
| ![Director](../../resources/icons/directoryExp.png) | Deschide director | Deschide dosarul de export |

---

## Campuri de Identificare

Campurile de identificare definesc in mod unic structura in baza de date.

![Campuri de identificare](images/05_scheda_struttura/06_campi_identificativi.png)

### Santier

**Camp**: `comboBox_sito`
**Baza de date**: `sito`

Selectati santierul arheologic de apartenenta. Meniul derulant afiseaza toate santierele inregistrate in baza de date.

**Note:**
- Camp obligatoriu
- Combinatia Santier + Cod + Numar trebuie sa fie unica
- Blocat dupa crearea inregistrarii

### Codul Structurii

**Camp**: `comboBox_sigla_struttura`
**Baza de date**: `sigla_struttura`

Cod alfanumeric care identifica tipul structurii. Conventii comune:

| Cod | Semnificatie | Exemplu |
|-----|-------------|---------|
| WL | Zid | WL 1 |
| ST | Structura | ST 5 |
| FL | Pardoseala | FL 2 |
| KN | Cuptor | KN 1 |
| TK | Bazin | TK 3 |
| TB | Mormant | TB 10 |
| WE | Fantana | WE 2 |
| CN | Canal | CN 1 |

**Note:**
- Editabil cu introducere libera
- Blocat dupa creare

### Numarul Structurii

**Camp**: `numero_struttura`
**Baza de date**: `numero_struttura`

Numarul progresiv al structurii in cadrul codului.

**Note:**
- Camp numeric
- Trebuie sa fie unic pentru combinatia Santier + Cod
- Blocat dupa creare

---

## Sincronizare cu Fisa US

Structurile create in aceasta fisa apar automat in campul **Structura** al **Fisei US** pentru acelasi santier.

### Cum functioneaza legatura

1. **Creati structura** completand cel putin:
   - **Santier**: santierul arheologic (de ex., "Roma_Forum")
   - **Cod**: codul structurii (de ex., "MUR")
   - **Numar**: numarul progresiv (de ex., 1)
   - Salvati inregistrarea

2. **In Fisa US** pentru acelasi santier:
   - Campul **Structura** va afisa structura in format `COD-NUMAR`
   - Exemplu: "MUR-1", "PV-2", "ST-3"

### Formatul de afisare

Structurile apar in Fisa US in formatul:
```
COD_STRUCTURA - NUMAR_STRUCTURA
```

**Exemple:**
| Fisa Structura | Afisat in Fisa US |
|----------------|-------------------|
| Santier=Roma, Cod=MUR, Numar=1 | MUR-1 |
| Santier=Roma, Cod=PV, Numar=2 | PV-2 |
| Santier=Roma, Cod=ST, Numar=10 | ST-10 |

### Note importante

- Structura trebuie **salvata** inainte de a aparea in Fisa US
- Sunt vizibile doar structurile de la **acelasi santier**
- In Fisa US puteti **selecta mai multe structuri** (selectie multipla cu casute de bifare)
- Pentru a **elimina** o structura din US: deschideti meniul derulant si debifati casuta
- Pentru a **goli** toate structurile: clic dreapta → "Golire camp Structura"

---

## Campuri de Clasificare

Campurile de clasificare definesc natura structurii.

![Campuri de clasificare](images/05_scheda_struttura/07_campi_classificazione.png)

### Categoria Structurii

**Camp**: `comboBox_categoria_struttura`
**Baza de date**: `categoria_struttura`

Macro-categoria functionala a structurii.

**Valori tipice:**
- Rezidentiala
- Productiva
- Funerara
- Religioasa
- Defensiva
- Hidraulica
- Rutiera
- Artizanala

### Tipul Structurii

**Camp**: `comboBox_tipologia_struttura`
**Baza de date**: `tipologia_struttura`

Tipul specific in cadrul categoriei.

**Exemple pe categorie:**
| Categorie | Tipuri |
|-----------|--------|
| Rezidentiala | Casa, Vila, Palat, Coliba |
| Productiva | Cuptor, Moara, Teasc |
| Funerara | Mormant in groapa, Mormant cu camera, Sarcofag |
| Hidraulica | Fantana, Cisterna, Apeduct, Canal |

### Definitia Structurii

**Camp**: `comboBox_definizione_struttura`
**Baza de date**: `definizione_struttura`

Definitie sintetica si specifica a elementului structural.

**Exemple:**
- Zid perimetral
- Pardoseala de cocciopesto
- Prag de piatra
- Scara
- Baza de coloana

---

## Fila Date Descriptive

Prima fila contine campuri text pentru descriere detaliata.

![Fila Date Descriptive](images/05_scheda_struttura/08_tab_descrittivi.png)

### Descriere

**Camp**: `textEdit_descrizione_struttura`
**Baza de date**: `descrizione`

Camp text liber pentru descrierea fizica a structurii.

**Continut recomandat:**
- Tehnica de constructie
- Materiale utilizate
- Starea de conservare
- Dimensiuni generale
- Orientare
- Caracteristici particulare

**Exemplu:**
```
Zid in opus incertum construit cu blocuri de calcar local
de dimensiuni variabile (15-30 cm). Liant de mortar de var albicios.
Pastrat la o inaltime maxima de 1,20 m.
Latime medie 50 cm. Orientare NE-SV. Prezinta urme
de tencuiala pe latura interna.
```

### Interpretare

**Camp**: `textEdit_interpretazione_struttura`
**Baza de date**: `interpretazione`

Interpretarea functionala si istorica a structurii.

**Continut recomandat:**
- Functia originala presupusa
- Faze de utilizare/reutilizare
- Comparatii tipologice
- Cadrul cronologic
- Relatii cu alte structuri

**Exemplu:**
```
Zid perimetral nord al unei cladiri rezidentiale din epoca
romana imperiala. Tehnica de constructie si materialele sugereaza
o datare in secolul al II-lea d.Hr. Intr-o faza ulterioara (sec. III-IV)
zidul a fost partial spoliat si incorporat intr-o
structura productiva.
```

---

## Fila Periodizare

Aceasta fila gestioneaza cadrul cronologic al structurii.

![Fila Periodizare](images/05_scheda_struttura/09_tab_periodizzazione.png)

### Perioada si Faza Initiala

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Perioada Initiala | `periodo_iniziale` | Perioada de constructie/inceput de utilizare |
| Faza Initiala | `fase_iniziale` | Faza in cadrul perioadei |

Valorile sunt populate automat pe baza perioadelor definite in Fisa de Periodizare pentru santierul selectat.

### Perioada si Faza Finala

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Perioada Finala | `periodo_finale` | Perioada de abandonare/desfiintare |
| Faza Finala | `fase_finale` | Faza in cadrul perioadei |

### Datare Extinsa

**Camp**: `comboBox_datazione_estesa`
**Baza de date**: `datazione_estesa`

Datare literala calculata automat sau introdusa manual.

**Formate:**
- "Sec. I i.Hr. - Sec. II d.Hr."
- "100 i.Hr. - 200 d.Hr."
- "Epoca romana imperiala"

**Note:**
- Propusa automat pe baza perioadei/fazei
- Editabila manual pentru cazuri speciale

---

## Fila Relatii

Aceasta fila gestioneaza relatiile intre structuri.

![Fila Relatii](images/05_scheda_struttura/10_tab_rapporti.png)

### Tabelul Relatiilor Structurale

**Widget**: `tableWidget_rapporti`
**Baza de date**: `rapporti_struttura`

Inregistreaza relatiile intre structura curenta si alte structuri.

**Coloane:**
| Coloana | Descriere |
|---------|-----------|
| Tip relatie | Relatia stratigrafica/functionala |
| Santier | Santierul structurii asociate |
| Cod | Codul structurii asociate |
| Numar | Numarul structurii asociate |

**Tipuri de relatii:**

| Relatie | Inversa | Descriere |
|---------|---------|-----------|
| Se leaga de | Se leaga de | Conexiune fizica contemporana |
| Acopera | Acoperit de | Relatie de suprapunere |
| Taie | Taiat de | Relatie de taiere |
| Umple | Umplut de | Relatie de umplere |
| Se sprijina pe | Este sprijinit de | Relatie de rezemare |
| Identic cu | Identic cu | Aceeasi structura cu nume diferit |

### Gestionare Randuri

| Buton | Functie |
|-------|---------|
| + | Adauga rand nou |
| - | Elimina randul selectat |

---

## Fila Elemente Constructive

Aceasta fila documenteaza materialele si elementele ce compun structura.

![Fila Elemente Constructive](images/05_scheda_struttura/11_tab_elementi.png)

### Materiale Utilizate

**Widget**: `tableWidget_materiali_impiegati`
**Baza de date**: `materiali_impiegati`

Lista materialelor utilizate in constructie.

**Coloana:**
- Materiale: descrierea materialului

**Exemple de materiale:**
- Blocuri de calcar
- Caramizi
- Mortar de var
- Pietris de rau
- Tigle
- Marmura
- Tuf

### Elemente Structurale

**Widget**: `tableWidget_elementi_strutturali`
**Baza de date**: `elementi_strutturali`

Lista elementelor constructive cu cantitati.

**Coloane:**
| Coloana | Descriere |
|---------|-----------|
| Tip element | Tipul elementului |
| Cantitate | Numarul de elemente |

**Exemple de elemente:**
| Element | Cantitate |
|---------|-----------|
| Baza de coloana | 4 |
| Capitel | 2 |
| Prag | 1 |
| Bloc echariat | 45 |

### Gestionare Randuri

Pentru ambele tabele:
| Buton | Functie |
|-------|---------|
| + | Adauga rand nou |
| - | Elimina randul selectat |

---

## Fila Masuratori

Aceasta fila inregistreaza dimensiunile structurii.

![Fila Masuratori](images/05_scheda_struttura/12_tab_misure.png)

### Tabelul Masuratorilor

**Widget**: `tableWidget_misurazioni`
**Baza de date**: `misure_struttura`

**Coloane:**
| Coloana | Descriere |
|---------|-----------|
| Tip masuratoare | Tipul dimensiunii |
| Unitate de masura | m, cm, mp etc. |
| Valoare | Valoare numerica |

### Tipuri Comune de Masuratori

| Tip | Descriere |
|-----|-----------|
| Lungime | Dimensiunea mai mare |
| Latime | Dimensiunea mai mica |
| Inaltime pastrata | Elevatia pastrata |
| Inaltime originala | Elevatia originala estimata |
| Adancime | Pentru structuri ingropate |
| Diametru | Pentru structuri circulare |
| Grosime | Pentru ziduri, pardoseli |
| Suprafata | Aria in mp |

### Exemplu de Completare

| Tip masuratoare | Unitate de masura | Valoare |
|-----------------|-------------------|---------|
| Lungime | m | 8,50 |
| Latime | cm | 55 |
| Inaltime pastrata | m | 1,20 |
| Suprafata | mp | 4,68 |

---

## Fila Media

Gestionarea imaginilor, videoclipurilor si modelelor 3D asociate structurii.

![Fila Media](images/05_scheda_struttura/13_tab_media.png)

### Functionalitati

**Widget**: `iconListWidget`

Afiseaza miniaturile mediilor asociate.

### Butoane

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Toate Imaginile](../../resources/icons/photo2.png) | Toate imaginile | Afiseaza toate imaginile |
| ![Eliminare Etichete](../../resources/icons/remove_tag.png) | Eliminare etichete | Elimina asocierea media |
| ![Cautare](../../resources/icons/search.png) | Cautare imagini | Cauta imaginile in baza de date |

### Tragere si Plasare

Puteti trage fisiere direct pe formular:

**Formate suportate:**
- Imagini: JPG, JPEG, PNG, TIFF, TIF, BMP
- Video: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Vizualizare

- **Dublu clic** pe miniatura: deschide vizualizatorul
- Pentru video: deschide playerul video integrat
- Pentru 3D: deschide vizualizatorul 3D PyVista

---

## Fila Harta

Previzualizare a pozitiei structurii pe harta.

![Fila Harta](images/05_scheda_struttura/14_tab_map.png)

### Functionalitati

- Afiseaza geometria structurii
- Zoom automat pe element
- Integrare cu straturile GIS ale proiectului

---

## Integrare GIS

### Vizualizare pe Harta

| Buton | Functie |
|-------|---------|
| Previzualizare Harta | Comuta previzualizarea in fila Harta |
| Deseneaza Structura | Evidentiaza structura pe harta QGIS |
| Incarca in GIS | Incarca stratul structurilor |
| Incarca Toate | Incarca toate structurile santierului |

### Straturi GIS

Fisa foloseste stratul **pyarchinit_strutture** pentru vizualizare:
- Geometrie: poligon sau multipoligon
- Atribute legate de campurile fisei

---

## Export si Tiparire

### Export PDF

![Panou Export](images/05_scheda_struttura/15_export_panel.png)

Butonul PDF deschide un panou cu optiuni de export:

| Optiune | Descriere |
|---------|-----------|
| Lista Structurilor | Lista sintetica a structurilor |
| Fise Structura | Fise complete detaliate |
| Tiparire | Genereaza PDF |
| Convertire in Word | Converteste PDF in format Word |

### Conversie PDF in Word

Functionalitate avansata pentru conversia PDF-urilor generate in documente Word editabile:

1. Selectati fisierul PDF de convertit
2. Specificati intervalul de pagini (optional)
3. Faceti clic pe "Convertire"
4. Fisierul Word este salvat in acelasi dosar

---

## Flux de Lucru Operational

### Crearea unei Structuri Noi

1. **Deschideti fisa**
   - Din meniu sau bara de instrumente

2. **Inregistrare noua**
   - Faceti clic pe butonul "Inregistrare Noua"
   - Campurile de identificare devin editabile

3. **Date de identificare**
   ```
   Santier: Vila Romana de la Settefinestre
   Cod: WL
   Numar: 15
   ```

4. **Clasificare**
   ```
   Categorie: Rezidentiala
   Tip: Zid perimetral
   Definitie: Zid in opus incertum
   ```

5. **Date descriptive** (Fila 1)
   ```
   Descriere: Zid construit in opus incertum cu
   blocuri de calcar local...

   Interpretare: Limita nordica a domus-ului, faza I
   a complexului rezidential...
   ```

6. **Periodizare** (Fila 2)
   ```
   Perioada initiala: I - Faza: A
   Perioada finala: II - Faza: B
   Datare: Sec. I i.Hr. - Sec. II d.Hr.
   ```

7. **Relatii** (Fila 3)
   ```
   Se leaga de: WL 16, WL 17
   Taiat de: ST 5
   ```

8. **Elemente constructive** (Fila 4)
   ```
   Materiale: Blocuri de calcar, Mortar de var
   Elemente: Blocuri echariate (52), Prag (1)
   ```

9. **Masuratori** (Fila 5)
   ```
   Lungime: 12,50 m
   Latime: 0,55 m
   Inaltime pastrata: 1,80 m
   ```

10. **Salvare**
    - Faceti clic pe "Salvare"
    - Verificati confirmarea salvarii

### Cautarea Structurilor

1. Faceti clic pe "Cautare Noua"
2. Completati unul sau mai multe campuri de filtrare:
   - Santier
   - Cod structura
   - Categorie
   - Perioada
3. Faceti clic pe "Cautare"
4. Navigati prin rezultate

### Modificarea Structurii Existente

1. Navigati la inregistrarea dorita
2. Modificati campurile necesare
3. Faceti clic pe "Salvare"

---

## Bune Practici

### Denumire

- Folositi coduri consistente pe tot parcursul proiectului
- Documentati conventiile utilizate
- Evitati numerotarea duplicata

### Descriere

- Fiti sistematic in descriere
- Urmati o schema: tehnica > materiale > dimensiuni > stare
- Separati descrierea obiectiva de interpretare

### Periodizare

- Legati intotdeauna de perioadele definite in Fisa de Periodizare
- Indicati atat faza initiala cat si cea finala
- Folositi datarea extinsa pentru sinteza

### Relatii

- Inregistrati toate relatiile semnificative
- Verificati reciprocitatea relatiilor
- Legati de US-urile care compun structura

### Media

- Asociati fotografii reprezentative
- Includeti fotografii de detaliu ale constructiei
- Documentati fazele sapaturii

---

## Depanare

### Problema: Structura nu este vizibila pe harta

**Cauza**: Geometria nu este asociata sau stratul nu este incarcat.

**Solutie**:
1. Verificati ca stratul `pyarchinit_strutture` exista
2. Verificati ca structura are geometrie asociata
3. Verificati sistemul de referinta a coordonatelor

### Problema: Perioadele nu sunt disponibile

**Cauza**: Perioadele nu sunt definite pentru santier.

**Solutie**:
1. Deschideti Fisa de Periodizare
2. Definiti perioadele pentru santierul curent
3. Reveniti la Fisa Structura

### Problema: Eroare de salvare "inregistrare existenta"

**Cauza**: Combinatia Santier + Cod + Numar exista deja.

**Solutie**:
1. Verificati numerotarea existenta
2. Folositi un numar progresiv liber
3. Verificati duplicatele

### Problema: Mediile nu se afiseaza

**Cauza**: Calea imaginilor este incorecta.

**Solutie**:
1. Verificati calea in configurare
2. Verificati ca fisierele exista
3. Regenerati miniaturile daca este necesar

---

## Relatii cu Alte Fise

| Fisa | Relatie |
|------|---------|
| **Fisa Santier** | Santierul contine structuri |
| **Fisa US** | US-urile compun structurile |
| **Fisa de Periodizare** | Ofera cronologia |
| **Fisa Inventar Materiale** | Descoperiri asociate structurilor |
| **Fisa Mormant** | Mormintele ca tip special de structura |

---

## Referinte

### Baza de Date

- **Tabel**: `struttura_table`
- **Clasa mapper**: `STRUTTURA`
- **ID**: `id_struttura`

### Fisiere Sursa

- **UI**: `gui/ui/Struttura.ui`
- **Controller**: `tabs/Struttura.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Tutorial Video

### Prezentare Generala Fisa Structura
**Durata**: 5-6 minute
- Prezentarea generala a interfetei
- Navigarea intre file
- Functionalitati principale

[Substituent video: video_panoramica_struttura.mp4]

### Documentarea Completa a Structurii
**Durata**: 10-12 minute
- Crearea unei inregistrari noi
- Completarea tuturor campurilor
- Gestionarea relatiilor si masuratorilor

[Substituent video: video_schedatura_struttura.mp4]

### Integrare GIS si Export
**Durata**: 6-8 minute
- Vizualizare pe harta
- Incarcarea straturilor
- Export PDF si Word

[Substituent video: video_gis_export_struttura.mp4]

---

*Ultima actualizare: Ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
