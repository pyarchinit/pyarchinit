# Tutorial 14: GIS i Cartografia

## Introducció

PyArchInit està profundament integrat amb **QGIS**, aprofitant totes les seves funcionalitats GIS per a la gestió espacial de les dades arqueològiques. Aquest tutorial cobreix la integració cartogràfica, les capes predefinides i les funcionalitats avançades com la **segmentació automàtica SAM**.

### Funcionalitats GIS Principals

- Visualització US al mapa
- Capes vectorials predefinides
- Estilització QML personalitzada
- Cotes i mesuraments GIS
- Segmentació automàtica (SAM)
- Exportació cartogràfica

## Capes Predefinides PyArchInit

### Capes Vectorials Principals

| Capa | Geometria | Descripció |
|------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | US dipòsit |
| `pyunitastratigrafiche_usm` | MultiPolygon | US muràries |
| `pyarchinit_quote` | Point | Punts cota |
| `pyarchinit_siti` | Point | Localització llocs |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Àrees d'excavació |
| `pyarchinit_strutture_ipotesi` | Polygon | Estructures hipotètiques |
| `pyarchinit_documentazione` | Point | Referències documentació |

### Atributs Capa US

| Camp | Tipus | Descripció |
|------|-------|-------------|
| `gid` | Integer | ID únic |
| `scavo_s` | Text | Nom lloc |
| `area_s` | Text | Número àrea |
| `us_s` | Text | Número US |
| `stratigraph_index_us` | Integer | Índex estratigràfic |
| `tipo_us_s` | Text | Tipus US |
| `rilievo_originale` | Text | Aixecament d'origen |
| `disegnatore` | Text | Autor aixecament |
| `data` | Date | Data aixecament |

## Visualització US al Mapa

### Des de la Pestanya "Map" a la Fitxa US

1. Obrir una fitxa US
2. Seleccionar la pestanya **Map**
3. Funcions disponibles:

| Botó | Funció |
|------|--------|
| View US | Visualitza US actual al mapa |
| View All | Visualitza totes les US de l'àrea |
| New Record | Crea nova geometria |
| Pan to | Centra mapa sobre US |

### Visualització des de Cerca

1. Executar una cerca US
2. Botó **"View Record"** → visualitza individual
3. Botó **"View All"** → visualitza tots els resultats

### Elecció de l'Estil (US i USM)

Des de la **5.13.112-alpha** la finestra **Style Choice** descrita tot seguit apareix **només si la vista no té cap estil per defecte desat**: amb un estil per defecte (per al lloc o per a tots els llocs) la fitxa carrega la vista, l'aplica i no pregunta res. Els estils per defecte es creen a la finestra **View styles** (vegeu la secció «Estils de les vistes», més avall).

Quan les US o les US muràries (USM) dels resultats de cerca es carreguen al mapa apareix la finestra **Style Choice** ("How do you want to manage the layer style?"). Els botons es mostren en anglès:

| Botó | Efecte |
|------|--------|
| **Save new style** | Crea l'estil segons el camp triat i el desa a la base de dades amb un nom |
| **Load existing style** | Fa servir com a model un estil ja preparat, triat d'una llista (vegeu més avall), i crea l'estil segons el camp triat sense desar-lo a la base de dades |
| **Use temporary style** | Crea l'estil segons el camp triat sense desar-lo a la base de dades |
| **Single symbol (outline only)** | Dibuixa només el contorn de les geometries, sense emplenament |

Des de la 5.13.19-alpha **Load existing style** obre la finestra **Existing style** ("Choose the style to use as a template:", en anglès) amb la llista dels estils disponibles: els estils desats a la base de dades (*Database: nom*), els estils QML inclosos amb pyArchInit (`us_*.qml`, llistats com a *pyArchInit: …*) i **Other QML file…**, per triar qualsevol fitxer `.qml`. L'estil triat es carrega a la capa (la transparència i el mode de fusió hi arriben amb ell, les etiquetes no: a les vistes US i USM de polígons són, des de la 5.13.110-alpha, les del paràgraf **Etiquetes** més avall, el número de la unitat en cercle, digui el que digui l'estil model) i fa de **model**: després de triar el camp de categorització, els valors que l'estil ja té conserven el seu color i símbol, i els altres reben una còpia del seu símbol amb un color propi. Si s'anul·la la tria, funciona com **Use temporary style**. Abans només buscava entre els estils de la base de dades i, si no en trobava cap, passava directament a la finestra de categorització.

Amb **Save new style**, **Load existing style** i **Use temporary style** després es tria el camp de categorització (finestra **Select Categorization Field**, en anglès): **Stratigraphic Definition** (definició estratigràfica), **SU Type** (tipus US), **Interpretive Definition** (definició interpretativa) o **Period/Phase (cont_per)** (període/fase, des de la 5.13.19-alpha); cada valor del camp rep un color propi, que des de la 5.13.19-alpha és el mateix cada vegada que es carrega la capa. Amb **Period/Phase (cont_per)** l'entrada de la llegenda de cada codi mostra també la datació del període/fase presa de la periodització. Només hi apareixen els camps presents a la capa.

**Ordre de dibuix.** Des de la 5.13.19-alpha les unitats es dibuixen en l'ordre que fa servir el Gestor de Temps (Time Manager): primer les que no tenen període, després per cronologia del període (segons la periodització del període/fase inicial de la US, o segons `cont_per`), després per `order_layer` (0 = el més antic) i finalment el tall sobre el seu farciment, de manera que les unitats més recents queden a sobre. Val per a totes les opcions d'estil, també per a **Single symbol (outline only)**. Quan les capes es carreguen període per període, l'estil es demana una sola vegada i es fa servir per a tots els períodes.

**Etiquetes.** Des de la 5.13.110-alpha, amb l'estil triat la vista US (i USM) rep també les seves **etiquetes**: el número de la unitat en **negreta dins d'un cercle blanc amb vora vermella fosca**, **una per unitat**, en el seu dibuix més gran si es veu (no cobert del tot per un de nivell superior), amb la mateixa recepta de les làmines de l'atles del Time Manager (tutorial 25). Quan dos números es taparien, un es desplaça i una línia de crida l'uneix al seu dibuix. Val per a les US i les USM, amb SQLite i amb PostgreSQL, i per a totes les opcions d'estil, també per a **Single symbol (outline only)**; si l'estil carregat amb **Load existing style** ja tenia etiquetes, el número en cercle ocupa el seu lloc. Les capes de punts no reben el número en cercle. Des de la 5.13.111-alpha, però, la **vista de cotes** (els punts de cota, capa «Elevation view»), tan bon punt es carrega des de la fitxa US, porta l'**etiqueta amb el valor de la cota** (dos decimals, per exemple «12,35»), col·locada **sobre la línia horitzontal del símbol**, amb la mateixa recepta de les làmines de l'atles del Time Manager. Val per a totes les opcions que la carreguen, amb SQLite i amb PostgreSQL, i no depèn de l'estil triat; les capes que no són de punts, o que no tenen el camp de la cota, no reben aquesta etiqueta. Des de la 5.13.112-alpha el número en cercle i la cota són els **presets de partida** de les etiquetes: a la pestanya **Etiquetes** (*Labels*) de la finestra **View styles** (vegeu la secció del mateix nom, més avall) es poden canviar i desar com a estil per defecte, que en carregar ocupa el seu lloc.

Des de la 5.13.18-alpha l'estil triat (i el camp de categorització) es respecta també amb les bases de dades SQLite, tant per a les US com per a les USM; abans el mapa sortia sempre amb un color per a cada US.

## Estils de les vistes

Des de la versió **5.13.112-alpha** una sola finestra, **View styles** (Estils de les vistes), serveix per compondre l'estil —**simbologia i etiquetes**— de cada vista de pyArchInit: les vistes de les US i de les USM, les cotes, la documentació, les estructures i les tombes, les UT, els llocs, les troballes, les seccions. L'estil es veu a l'instant en una **previsualització** amb les dades del lloc, es desa amb un nom a la base de dades i es pot fer **per defecte** per a un lloc o per a tots: a partir d'aquell moment les fitxes que carreguen la vista l'apliquen soles, sense preguntar res.

<!-- IMMAGINE: Captura de pantalla de la finestra «View styles»: a l'esquerra la llista de vistes i d'estils desats amb els seus botons; a la dreta la previsualització i les pestanyes Symbology i Labels; a baix Apply to loaded layers, Save, Save as… i Close -->
![La finestra View styles](images/14_gis_cartografia/01_stili_delle_viste.png)
*Figura 1: La finestra «View styles»*

Els textos de la finestra només existeixen en italià i en anglès: amb QGIS en català apareix en anglès. A continuació, cada etiqueta traduïda va seguida de l'anglesa entre parèntesis. El mateix val per a l'entrada de menú: amb QGIS en català es diu «View styles…».

### Des d'on s'obre

La finestra no és modal: roman oberta mentre es treballa al mapa. S'obre de quatre maneres.

- **Des de la barra d'eines de pyArchInit** (a partir de la 5.13.113-alpha): el **quart botó**, amb la icona de la paleta, just després del de GPT («AI Query Database»). Si la capa activa és una vista de pyArchInit, la finestra s'obre ja sobre aquella vista; si no, sobre la vista US.
- **Des del menú del connector**: **Plugins → pyArchInit - Archaeological GIS Tools → View styles…** (Estils de les vistes; amb QGIS en italià l'entrada es diu «Stili delle viste…»). Si la capa activa és una vista de pyArchInit, la finestra s'obre ja sobre aquella vista; si no, sobre la vista US.
- **Des del menú de la capa**: clic dret sobre una capa vectorial al tauler de capes de QGIS → **View styles…**. És la mateixa entrada, amb el mateix nom i la mateixa regla: si la capa és una vista de pyArchInit, la finestra s'obre ja sobre aquella.
- **Des de la fitxa US**: el botó **Style…** (amb QGIS en italià, **Stile…**), al costat del botó que carrega les capes. Obre la finestra sobre la vista US, amb el lloc de la fitxa.

La previsualització mostra les geometries d'un **lloc**: el de la fitxa si la finestra s'obre des del botó «Style…»; si no, el **lloc actiu** establert a la configuració de pyArchInit (tutorial 01). Sense lloc actiu mostra tots els llocs.

### Les vistes i els estils desats

La columna de l'esquerra té dues llistes.

**Vistes** (*Views*). Les vistes de pyArchInit, per grups:

| Grup | Vistes |
|------|--------|
| «Unitats estratigràfiques» (*Stratigraphic units*) | US, USM, US negatives |
| «Cotes» (*Elevations*) | cotes de les US, cotes de les USM |
| «Documentació» (*Documentation*) | documentació (dues vistes) |
| «Estructures i tombes» (*Structures and burials*) | estructures, tombes, individus |
| «Unitats topogràfiques» (*Topographic units*) | UT puntuals, lineals, poligonals |
| «Llocs» (*Sites*) | llocs puntuals, llocs poligonals |
| «Troballes» (*Finds*) | troballes |
| «Seccions» (*Sections*) | seccions d'excavació |

També les vistes que fins ara es carregaven sense estil (documentació, estructures i tombes, UT, llocs, troballes, seccions) en tenen aquí un. Una vista que no és a la base de dades es torna **grisa** quan se la tria, i la línia d'estat diu «Vista no present en aquesta base de dades» (*View not present in this database.*).

**Estils desats** (*Saved styles*). Sota, els estils desats per a la vista triada, un per fila: *nom · lloc (o «tots els llocs») · «✓ per defecte»* (*all sites*, *✓ default*). Un clic en un estil el carrega a la previsualització i a les pestanyes, per mirar-lo o retocar-lo. Els estils que QGIS ha desat a la base de dades per a aquella capa apareixen com a *nom · Desat amb QGIS* (*Saved with QGIS*): es poden carregar, però pyArchInit no els reescriu; per conservar-ne una còpia entre els seus propis estils s'usa **Desa com a…** (*Save as…*). Els botons sota la llista:

| Botó | Què fa |
|------|--------|
| **Nou** (*New*) | Parteix d'un estil per compondre: només contorn, amb les etiquetes de partida de la vista. El nom es demana al primer **Desa** (*Save*) |
| **Duplica** (*Duplicate*) | Copia l'estil triat amb el nom «… (2)»; la còpia no és per defecte |
| **Canvia el nom…** (*Rename…*) | Canvia el nom de l'estil triat |
| **Elimina** (*Delete*) | Elimina l'estil triat, després d'una confirmació |
| **Per defecte per a aquest lloc** (*Default for this site*) | L'estil triat passa a ser el que s'aplica en carregar la vista per al lloc actual (si l'estil és de «tots els llocs», en fa una còpia per al lloc actual i fa per defecte la còpia; l'original queda com està) |
| **Per defecte per a tots els llocs** (*Default for all sites*) | Passa a ser el que s'aplica als llocs que no en tenen un de propi (si l'estil és d'un lloc, en fa una còpia per a tots els llocs i fa per defecte la còpia; l'original queda com està) |
| **Exporta QML…** (*Export QML…*), **Importa QML…** (*Import QML…*) | Vegeu «Exportar i importar» |

Per a cada vista hi ha un sol estil per defecte per lloc i un sol per a tots els llocs: fer per defecte un altre estil treu la marca «✓ per defecte» a l'anterior. Duplica, Canvia el nom, Elimina i els dos «Per defecte» actuen sobre l'estil triat a la llista; si no n'hi ha cap de triat, apareix l'avís «Tria primer un estil desat» (*Choose a saved style first.*).

### Previsualització, simbologia i etiquetes

**Previsualització.** A dalt a la dreta, un mapa mostra la vista triada, llegida de la base de dades i filtrada pel lloc actual: cada canvi a l'estil es veu a l'instant. **Enquadra** (*Zoom to data*) porta el mapa a totes les geometries. La línia d'estat sota el mapa diu quantes són (*482 geometries del lloc «Scavo 2026».*, *482 geometries of site “Scavo 2026”.*) o, si el lloc no en té cap en aquella vista, «Cap geometria per al lloc actual» (*No geometry for the current site.*): l'estil es pot compondre igualment. La previsualització és una capa a part, **no afegida al projecte**: les capes del projecte de QGIS no canvien fins que es prem **Aplica a les capes carregades** (*Apply to loaded layers*). En triar una vista, la previsualització parteix d'allò que pyArchInit li aplicaria en aquell moment en carregar-la (vegeu «Estils per defecte i càrrega»).

Sota el mapa hi ha dues pestanyes: **Simbologia** (*Symbology*) i **Etiquetes** (*Labels*).

**Pestanya Simbologia.** A dalt, la llista desplegable **Preset** (*Preset:*):

| Preset | Efecte |
|--------|--------|
| «— deixa com està —» (*— keep as is —*) | No canvia res |
| «Només contorn» (*Outline only*) | Polígons sense farciment i amb la vora gris fosca, línies fines, punts com a cercles buits |
| «Estil subministrat amb pyArchInit» (*Style shipped with pyArchInit*) | El QML que acompanya el connector: existeix per a les vistes US i USM i per a les cotes |
| «Categories per “camp”» (*Categories by “field”*) | Una categoria, amb el seu color, per a cada valor del camp. Hi ha una entrada per a cadascun dels camps amb sentit per a aquella vista que la capa té: per a les unitats `d_stratigrafica`, `tipo_us_s`, `d_interpretativa` i `cont_per`; per a les altres vistes, per exemple, `tipo_doc`, `tipologia_struttura` o `tipo_reperto` |

Sota la llista hi ha l'**editor de simbologia de QGIS**, el mateix de les propietats de la capa (símbol únic, categoritzat, graduat, basat en regles…): el preset és el punt de partida i des d'allà es retoca tot; cada canvi es veu a l'instant a la previsualització.

**Pestanya Etiquetes.**

| Control | Què fa |
|---------|--------|
| **Etiquetes actives** (*Labels on*) | Encén i apaga les etiquetes de la vista |
| **Què s'escriu** (*What to write:*) | «Cap etiqueta» (*No label*); «Número de la unitat en un cercle» (*Unit number in a circle*: el número en negreta dins d'un cercle blanc amb vora vermella fosca, com a les làmines de l'atles del Time Manager, tutorial 25); «Cota sobre el símbol» (*Elevation above the symbol*: el valor de la cota sobre la línia horitzontal del símbol); «Un camp o una expressió» (*A field or an expression*) |
| **Camp** (*Field:*), **Expressió** (*Expression:*) | Per a l'última entrada: el camp de la vista que s'escriu o una expressió de QGIS (si n'hi ha una d'escrita, té prioritat sobre el camp) |
| **Posició** (*Placement:*), **Desplaçament (mm)** (*Offset (mm):*) | Per a l'última entrada: «Al centre» (*Centred*), «Al voltant del punt» (*Around the point*) o «Sobre el símbol» (*Above the symbol*); el desplaçament puja l'etiqueta aquests mil·límetres i val per a «Sobre el símbol» |
| **Una etiqueta per unitat (sobre el dibuix més gran que es veu)** (*One label per unit (on the largest visible drawing)*) | Per al número de la unitat: una sola etiqueta per unitat, sobre el seu dibuix més gran que es veu (no cobert del tot per un de nivell superior); apagada, cada dibuix té la seva |
| **Tipus de lletra i fons** (*Font and background*) | Tipus de lletra, **Mida (mm)** (*Size (mm):*), **Negreta** (*Bold*), **Color…** (*Colour…*) del text, **Halo blanc** (*White buffer*), **Fons circular** (*Circle background*) amb **Farciment…** (*Fill…*) i **Vora…** (*Stroke…*) |

El número de la unitat en un cercle és el preset de partida de les vistes US i USM, la cota sobre el símbol el de les vistes de cotes: són les etiquetes del paràgraf **Etiquetes** d'«Elecció de l'Estil (US i USM)» (a dalt), que aquí es poden canviar. Les altres vistes, de partida, no tenen etiquetes. El panell és el de pyArchInit, més simple que l'editor d'etiquetes de QGIS (basat en regles i la resta), que no es pot obrir fora de les propietats de la capa.

### Estils per defecte i càrrega

A baix hi ha quatre botons:

| Botó | Què fa |
|------|--------|
| **Aplica a les capes carregades** (*Apply to loaded layers*) | Aplica l'estil que es veu a la previsualització —simbologia i etiquetes— a les capes del projecte de QGIS que vénen d'aquella vista; la línia d'estat diu «Estil aplicat a N capes del projecte» (*Style applied to N project layers.*) o «Cap capa d'aquesta vista al projecte» (*No layer of this view in the project.*). No desa res a la base de dades |
| **Desa** (*Save*) | Desa sobre l'estil actual (el triat a la llista); si no n'hi ha cap, demana el nom i crea un estil nou |
| **Desa com a…** (*Save as…*) | Demana el nom i desa un estil nou, per a tots els llocs: «Estil “nom” desat» (*Style “name” saved.*) |
| **Tanca** (*Close*) | Tanca la finestra |

Perquè un estil sigui el que es veu a cada càrrega: (1) tria la vista; (2) compon simbologia i etiquetes mirant la previsualització; (3) **Desa com a…** amb un nom; (4) **Per defecte per a aquest lloc** o **Per defecte per a tots els llocs**; (5) si les capes ja són al projecte, **Aplica a les capes carregades**.

**En carregar mana l'estil per defecte.** Quan una fitxa de pyArchInit (per exemple la fitxa US) carrega una vista, aplica per ordre:

1. l'estil **per defecte del lloc per al qual es carrega la vista** (si n'hi ha): la fitxa US passa el lloc de la fitxa, els carregadors per període (Time Manager) el lloc que estan dibuixant; on el carregador no coneix el lloc val el lloc actiu de la configuració de pyArchInit (tutorial 01);
2. si no, l'estil **per defecte per a tots els llocs**;
3. si no, per a les vistes US, USM i de cotes, l'estil subministrat amb pyArchInit amb el número en cercle o la cota sobre el símbol (com des de la 5.13.110-alpha i la 5.13.111-alpha); les altres vistes es carreguen com abans, sense estil.

La finestra de tres passos **Style Choice** (paràgraf «Elecció de l'Estil (US i USM)», a dalt) apareix **només si per a aquella vista no hi ha cap estil per defecte desat**; amb un estil per defecte la fitxa US simplement carrega, i un estil triat a mà no el sobreescriu. «Una etiqueta per unitat» es recalcula a cada càrrega, sobre els dibuixos del filtre d'aquell moment: no depèn del filtre amb què es va desar l'estil. La pestanya **Map preview** de la fitxa US també respecta l'estil per defecte desat (amb SQLite des de la 5.13.113-alpha, abans donava un error; amb PostgreSQL ja des de la 5.13.112-alpha); sense estil per defecte mostra, com abans, la seva simbologia automàtica, i també allà els polígons queden en ordre estratigràfic.

**L'ordre de dibuix és sempre l'estratigràfic** (des de la 5.13.113-alpha). A les vistes de les unitats (US, USM, US negatives) els polígons es dibuixen de la unitat més antiga, a sota, a la més recent, a sobre: primer els períodes per cronologia, si la periodització del lloc es pot llegir (començant per les unitats sense període), després `order_layer` creixent (0 = la més antiga, dibuixada primer), després l'índex estratigràfic, com al Time Manager (tutorial 25). Val sigui quin sigui l'estil — l'estil per defecte desat, el QML inclòs, un QML importat, l'estil compost a la previsualització — també a **Aplica a les capes carregades** (*Apply to loaded layers*) i a la previsualització de la finestra. Així, en desmarcar una categoria a la llegenda de QGIS, es veu el que hi ha a sota. Les altres vistes (cotes, documentació, estructures…) no reben cap ordre.

### Exportar i importar

- **Exporta QML…** escriu en un fitxer `.qml` l'estil tal com es veu a la previsualització —simbologia i etiquetes—; el nom proposat és el de la vista (per exemple `pyarchinit_us_view.qml`). Serveix per conservar-ne una còpia o per usar-lo en una altra base de dades o a QGIS.
- **Importa QML…** llegeix un fitxer `.qml`, el mostra a la previsualització i el desa com a estil nou, per a tots els llocs, amb el nom del fitxer. Si el fitxer no es llegeix com a QML, un avís ho diu amb el nom del fitxer (*“name.qml” does not read as QML.*) i no s'escriu res.
- Els estils desats viuen a la **base de dades connectada** a pyArchInit, a la taula `pyarchinit_view_styles`, que es crea sola, amb SQLite i amb PostgreSQL: amb PostgreSQL els veuen tots els usuaris de la mateixa base de dades. Per passar-los a una altra base de dades, s'exporten i s'importen com a QML.
- Si la base de dades no està connectada (o la taula dels estils no es pot crear, per exemple a PostgreSQL sense permís per crear taules), els estils desats no estan disponibles i només es pot exportar: la línia d'estat sota la previsualització ho diu després del recompte de geometries, amb «Base de dades no connectada: els estils només es poden exportar» (*Database not connected: styles can only be exported.*) o «La taula dels estils no es pot crear en aquesta base de dades: els estils només es poden exportar» (*The styles table cannot be created in this database: styles can only be exported.*).

## Estilització de les Capes

### Fitxers QML

PyArchInit inclou estils predefinits en format QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicació Estil

1. Seleccionar la capa a la llegenda
2. Botó dret → **Propietats**
3. Pestanya **Estil**
4. **Carrega estil** → seleccionar QML

### Personalització

Els estils es poden personalitzar per:
- Colors segons el tipus US
- Etiquetes amb número US
- Transparència
- Vores i farciments

## Cotes i Mesuraments

### Capa Cotes

La capa `pyarchinit_quote` emmagatzema:
- Coordenades X, Y
- Cota Z (absoluta)
- Tipus punt cota
- US de referència
- Àrea de referència

### Càlcul Cotes Automàtic

Des de la Fitxa US, les cotes min/max es calculen:
1. Consulta als punts cota associats a l'US
2. Extracció valor mínim i màxim
3. Visualització a l'informe

### Inserció Cotes

1. Capa cotes en edició
2. Dibuixar punt al mapa
3. Emplenar atributs:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentació Automàtica SAM

### Què és SAM?

**SAM (Segment Anything Model)** és el model d'intel·ligència artificial de Meta que divideix una imatge en els seus objectes. A pyArchInit la finestra SAM converteix una imatge en **polígons**, a partir de:

- una **ortofoto** (un fitxer ràster: GeoTIFF, JPEG georeferenciat…);
- o una **capa de tessel·les o un servei** carregat a QGIS: XYZ com ESRI World Imagery o Google, WMS, ArcGIS REST.

No només pedres: també **edificis, carreteres, camps, rius, murs**. Els models són de dues famílies:

- **SAM 2.1** (Meta) troba els contorns dels objectes —tots, o els que s'indiquin amb punts, un rectangle o un polígon—, però no diu què són;
- les **classes de text** (YOLOE-26 en local, SAM 3 al núvol) cerquen el que s'escriu («building, road, river, field») i cada polígon porta la seva etiqueta.

Els polígons van a la capa que es triï: les capes US de pyArchInit, qualsevol capa de polígons del projecte o una capa temporal nova.

### Accés a la Funció

1. Des de la barra d'eines de pyArchInit: botó desplegable **Eines d'anàlisi** (Analysis Tools) → «SAM - Segmentation (stones, buildings, roads, fields…)». És l'acció per defecte del botó: un clic a la icona obre directament la finestra.
2. O des del menú **pyArchInit** → «SAM - Segmentation (stones, buildings, roads, fields…)».

La finestra es titula «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». Les seves etiquetes només existeixen en italià i en anglès: amb QGIS en català apareix en anglès, com a l'esquema. A continuació, cada etiqueta traduïda va seguida de l'anglesa entre parèntesis.

### Interfície SAM

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Cinc grups, que s'omplen de dalt a baix: «Entorn local» (*Local environment*), «Imatge» (*Image*), «Què cal segmentar» (*What to segment*), «Model» (*Model*), «Destinació» (*Target*). A sota hi ha la línia d'estat («Llest», *Ready*), on també apareixen els missatges de la feina en curs, i els botons «Inicia» (*Start*), «Cancel·la» (*Cancel*, visible només durant la feina) i «Tanca» (*Close*). Algunes files només apareixen quan cal: «Clau API:» (*API key:*) en lloc de l'estat dels pesos per als models al núvol; «Lloc:» (*Site:*), «Àrea:» (*Area:*), «Índex estratigràfic:» (*Stratigraphic index:*) i «Tipus US:» (*US type:*) per a les capes US; «Camp per a l'etiqueta:» (*Field for the label:*) per a les altres capes. La finestra recorda l'última àrea US, les classes, el costat màxim, el model triat i les claus API.

Les entrades de la llista de models estan sempre escrites en italià («Locale» = local), igual que alguns missatges de servei citats més avall.

#### Entorn local

Els models locals (SAM 2.1 i YOLOE) no s'executen en el Python de QGIS, sinó en un **Python separat**, que la finestra crea i comprova tota sola. En obrir-se, el grup mostra «comprovant…» (*checking…*) i després:

- en verd «llest — ultralytics …, torch …, mps» (*ready — …*): l'entorn hi és; l'última paraula és el dispositiu de càlcul (`mps`, `cuda` o `cpu`);
- en taronja «no instal·lat: cal per als models locals (SAM 2.1, YOLOE). Un Python del sistema 3.10–3.13, ~1,5 GB de paquets.» (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

«Instal·la / actualitza» (*Install / update*) crea l'entorn o n'actualitza els paquets (vegeu més avall «Instal·lació Local SAM»); «Mostra el registre» (*Show log*) obre i tanca el registre de la instal·lació, amb la sortida de pip línia a línia. Els models al núvol no necessiten l'entorn.

#### Imatge

- «Capa ràster:» (*Raster layer:*): la imatge que es vol segmentar, triada entre els ràsters del projecte: una ortofoto (fitxer) o una capa de tessel·les/servei. A sota, en gris, s'indica quin dels dos és: nom del fitxer i mida en píxels (`orthophoto.tif — 12000 × 9000 px`) o el tipus de servei, renderitzat des de la vista (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)`; aquesta línia és en italià, *reso dalla vista* = renderitzat des de la vista).
- «Extensió:» (*Area:*): «vista actual» (*current view*, el que es veu al mapa) o «tot el ràster» (*whole raster*). «tot el ràster» només es pot triar per als fitxers: un servei de tessel·les no té vora, així que sempre es treballa sobre la vista (o sobre un rectangle o un polígon).
- «Resolució (unitats de mapa/px):» (*Resolution (map units/px):*): només per a les tessel·les: quantes unitats de mapa (metres, o graus si el mapa és en coordenades geogràfiques) per cada píxel de la imatge renderitzada. El valor proposat és el de la vista en obrir la finestra o en triar la capa: si després es canvia el zoom, cal corregir-lo a mà. Com més petit, més detall.
- «Costat màxim (px):» (*Max side (px):*): el costat més llarg de la imatge que es passa al model: 2048 per defecte, de 512 a 8192. Per sobre d'aquest costat la imatge es redueix; SAM treballa igualment a 1024 px interns.

### Modes de Segmentació

El grup «Què cal segmentar» (*What to segment*) ofereix sis modes. En triar un mode canvia la llista de models (vegeu «Models Disponibles») i a sota apareix, en blau, la instrucció d'aquell mode.

#### 1. Tot automàtic

«Tot (automàtic)» (*Everything (automatic)*): SAM 2.1 segmenta cada objecte que troba a l'«Extensió:» triada («vista actual» o «tot el ràster»). Els polígons no tenen classe: a la capa temporal reben l'etiqueta «segment». S'engega amb «Inicia» (*Start*).

#### 2. Punts

«Punts: feu clic als objectes del mapa» (*Points: click the objects on the map*): premeu «Inicia la selecció» (*Start selection*); la finestra s'amaga i la barra de missatges de QGIS recorda les ordres. Feu clic als objectes un per un: cada clic és un objecte. Clic dret o Retorn per acabar, Retrocés treu l'últim punt, Esc cancel·la. La finestra torna a aparèixer i la segmentació s'executa sobre l'«Extensió:» triada, un objecte per punt; els punts fora de la imatge s'ignoren.

#### 3. Rectangle

«Rectangle: dibuixeu un rectangle» (*Box: draw a rectangle*): premeu «Inicia la selecció» i arrossegueu un rectangle sobre el mapa (Esc o clic dret cancel·la). La imatge es retalla al rectangle i se segmenta tot el que hi ha a dins.

#### 4. Polígon

«Polígon: dibuixeu l'àrea» (*Polygon: draw the area*): premeu «Inicia la selecció» i feu clic als vèrtexs; clic dret, Retorn o doble clic tanquen el polígon (calen almenys tres vèrtexs), Retrocés treu l'últim vèrtex, Esc cancel·la. Només se segmenta l'interior del polígon.

#### 5. Polígon des d'una capa

«Polígon des d'una capa:» (*Polygon from layer:*): trieu una capa de polígons al desplegable del costat. S'utilitza l'entitat seleccionada de la capa, o totes si no n'hi ha cap de seleccionada (diverses entitats s'uneixen en una). Com amb el polígon dibuixat, només se segmenta l'interior: útil per treballar dins d'un sondeig, una àrea d'excavació o un límit ja dibuixat. S'engega amb «Inicia».

#### 6. Classes de text

«Classes de text:» (*Text classes:*): escriviu al camp del costat què cal cercar: paraules en **anglès** separades per comes (per defecte «building, road, river, field»; altres exemples: stone, wall). Cada classe esdevé una etiqueta dels polígons. Funciona amb YOLOE-26 en local o amb SAM 3 de Roboflow al núvol, sobre l'«Extensió:» triada. S'engega amb «Inicia».

**«Llindar:»** (*Threshold:*; 0,30 per defecte, de 0,05 a 0,95) és la confiança mínima perquè un resultat es conservi: més baix dona més polígons, també incerts; més alt en dona menys però més segurs. El model al núvol de Replicate no el fa servir.

### Models Disponibles

El grup «Model» (*Model*) té un desplegable «Model:» (*Model:*) el contingut del qual depèn del mode triat:

| Model | Tipus | Requisits | Modes |
|-------|-------|-----------|-------|
| SAM 2.1 Tiny | Local | entorn local + pesos ~78 MB | tots excepte les classes de text; el més lleuger i ràpid |
| SAM 2.1 Small | Local | entorn local + pesos ~92 MB | tots excepte les classes de text |
| SAM 2.1 Base+ | Local | entorn local + pesos ~162 MB | tots excepte les classes de text |
| SAM 2.1 Large | Local | entorn local + pesos ~449 MB | tots excepte les classes de text; el més precís i el més lent |
| Cloud: Replicate SAM-2 | Núvol | clau API de Replicate | només segmentació automàtica (en el mode «Punts» els clics s'ignoren, amb un avís) |
| YOLOE-26 S | Local | entorn local + pesos ~31 MB + MobileCLIP2 254 MB (una vegada) | classes de text |
| YOLOE-26 M | Local | entorn local + pesos ~70 MB + MobileCLIP2 254 MB (una vegada) | classes de text |
| YOLOE-26 L | Local | entorn local + pesos ~79 MB + MobileCLIP2 254 MB (una vegada) | classes de text |
| Cloud: Roboflow SAM 3 | Núvol | clau API de Roboflow | classes de text |

Al desplegable les entrades es llegeixen així: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = local, *classi a testo* = classes de text, *solo automatico* = només automàtic, *chiave* = clau).

**Pesos.** Per a un model local, sota el desplegable apareix l'estat dels pesos: «pesos presents ✓» (*weights present ✓*, verd) o «falten els pesos (~N MB)» (*weights missing (~N MB)*, taronja), amb el botó «Descarrega els pesos» (*Download weights*). La descàrrega, amb barra de progrés, agafa els fitxers dels recursos públics d'ultralytics a GitHub (no cal cap compte). Per a YOLOE també es descarrega el codificador de text MobileCLIP2 (254 MB), una sola vegada per a S, M i L. Els pesos es desen a `~/pyarchinit_5/bin/models/sam/`.

**Clau API.** Per a un model al núvol, el camp «Clau API:» (*API key:*) i l'enllaç per obtenir-la substitueixen l'estat dels pesos (vegeu «Configuració API»).

### SAM-3 amb Text Prompt

Amb el mode «Classes de text» no es demana «divideix-ho tot», sinó «troba aquestes coses»:

- s'escriuen una o més classes en anglès, separades per comes: `building, road, river, field`, o bé `stone, wall`…;
- **YOLOE-26** (local, S/M/L) entén les paraules gràcies al codificador de text MobileCLIP2; **SAM 3** de Roboflow (núvol) rep les mateixes classes com a prompts de text (16 com a màxim);
- cada polígon porta la classe que l'ha trobat: a la capa temporal, al camp `label`; en una capa pròpia, al «Camp per a l'etiqueta:» (*Field for the label:*). A les capes US de pyArchInit la classe no s'escriu.

En canvi, SAM 2.1 en «Tot (automàtic)» no assigna classes: troba contorns, no noms.

### Configuració API

Les claus només calen per als models al núvol. Trieu el model al núvol al desplegable, enganxeu la clau al camp «Clau API:» (*API key:*; el text queda ocult) i premeu «Inicia»: la clau es desa a la configuració de QGIS i es torna a proposar la vegada següent. Amb els models al núvol la imatge preparada s'envia al servei.

#### Replicate API (SAM-2)
1. Crear un compte a [replicate.com](https://replicate.com)
2. Crear un testimoni (token) a [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (l'enllaç «Clau de Replicate» (*Replicate key*) al costat del camp obre la mateixa pàgina)
3. Enganxar-lo a «Clau API:» amb el model «Cloud: Replicate SAM-2»

#### Roboflow API (SAM-3)
1. Crear un compte a [roboflow.com](https://roboflow.com)
2. Copiar la clau des de [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (enllaç «Clau de Roboflow» (*Roboflow key*) al costat del camp)
3. Enganxar-la a «Clau API:» amb el model «Cloud: Roboflow SAM 3»

### Instal·lació Local SAM

No cal cap ordre al terminal: l'entorn dels models locals s'instal·la des de la finestra.

1. Cal un **Python del sistema 3.10–3.13**: els paquets no s'instal·len al Python de QGIS, per no arriscar-se a espatllar-lo. La finestra el cerca tota sola: a **macOS** el Python de [python.org](https://www.python.org/downloads/) o de Homebrew, a **Windows** el llançador `py` del Python de python.org, a **Linux** `python3.10`…`python3.13` o el `python3` del sistema.
2. Premeu «Instal·la / actualitza» (*Install / update*) al grup «Entorn local»: es crea l'entorn virtual `~/pyarchinit_5/bin/sam_venv` i s'hi instal·len `ultralytics` (que porta torch, torchvision, OpenCV, numpy) i `requests`: uns **1,5 GB** de paquets, una sola vegada. A Linux sense targeta NVIDIA s'instal·la torch per a CPU, molt més lleuger.
3. «Mostra el registre» (*Show log*) permet veure pip treballant. Al final l'estat es posa en verd: «llest — ultralytics …, torch …, mps».
4. Descarregueu els pesos del model que vulgueu fer servir amb «Descarrega els pesos» (*Download weights*, grup «Model»).

Prement de nou «Instal·la / actualitza» s'actualitzen els paquets. El dispositiu de càlcul es tria sol: **MPS** als Mac amb Apple Silicon, **CUDA** amb una targeta NVIDIA i, si no, **CPU** (funciona, però és més lent). Si MPS o CUDA fallen, la feina torna a començar sola a la CPU.

| Què | On |
|-----|----|
| Entorn Python | `~/pyarchinit_5/bin/sam_venv` |
| Pesos dels models | `~/pyarchinit_5/bin/models/sam/` |
| Claus API | configuració de QGIS |

`~/pyarchinit_5` és la carpeta de dades de pyArchInit (o la indicada per la variable `PYARCHINIT_HOME`).

### Destinació i Atributs

El grup «Destinació» (*Target*) decideix on van els polígons. El desplegable «Capa:» (*Layer:*) conté les capes de polígons del projecte i «— nova capa temporal —» (*— new temporary layer —*); si `pyunitastratigrafiche` està carregada, es proposa aquesta.

| Destinació | Què s'escriu |
|------------|--------------|
| «— nova capa temporal —» | una capa en memòria `SAM_<ràster>_<data_hora>`, en el SRC de la imatge, amb els camps `label` (la classe, o «segment»), `score` (confiança), `area`, `source` (el model) i `created` (data i hora) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Lloc:» (*Site:*; de la configuració, no editable), `area_s` = «Àrea:» (*Area:*; obligatòria), `stratigraph_index_us` = «Índex estratigràfic:» (*Stratigraphic index:*; 1 = pedres/objectes, 2 = estrat/superfície), `tipo_us_s` = «Tipus US:» (*US type:*; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <model>` (p. ex. `SAM sam2.1_t.pt`), `data` = avui; `us_s` queda buit |
| una altra capa de polígons | la classe al «Camp per a l'etiqueta:» (*Field for the label:*), un camp de text (es proposa `label`, `etichetta`, `classe`, `class`, `tipo` o `nome`, si existeix; buit = no escriure); si la capa té camps `score`, `area`, `source` o `created`, també s'omplen |

- A les capes US el número d'US s'assigna després, a la taula d'atributs; el missatge final ho recorda: «Assigna després els números d'US a la taula d'atributs.» (*Then assign the US numbers in the attribute table.*).
- Els polígons es reprojecten al SRC de la capa de destinació i s'hi desen de seguida (si la capa ja estava en edició, també se'n desen els canvis pendents).
- La capa temporal només dura fins que es tanca QGIS: per conservar-la, exporteu-la a un fitxer (clic dret sobre la capa → Exporta).

### Com Funciona

1. **La imatge.** En un fitxer, l'extensió es retalla i, si cal, es redueix amb GDAL: els píxels són els reals del fitxer, no els dibuixats al mapa (l'estil de la capa no compta; els ràsters que no són de 8 bits es reescalen a 0–255). Les tessel·les i els serveis no tenen fitxer: QGIS renderitza la vista amb el seu propi motor de dibuix, a la resolució triada —només aquella capa, sense les altres capes del mapa—, i se segmenta aquest renderitzat.
2. **L'àrea.** Amb un polígon (dibuixat o des d'una capa) es pren el rectangle que el conté, es pinta de blanc tot el que queda fora i, al final, els resultats es retallen al polígon.
3. **El model.** La feina la fa `scripts/sam_worker.py`, que s'executa fora de QGIS amb el Python de `sam_venv` (o crida el servei al núvol): QGIS no es bloqueja. Els seus missatges de progrés (les línies `[sam] …` del worker, en italià) apareixen a la línia d'estat: model i dispositiu, i després quants polígons en quants segons. Els polígons de menys de 20 píxels es descarten i els contorns se simplifiquen.
4. **La tornada al mapa.** El worker retorna els polígons en píxels; pyArchInit els passa a coordenades amb la georeferència de la imatge, repara les geometries no vàlides i les reprojecta al SRC de la capa de destinació.

### Flux de Treball SAM

**1. Preparació**
- Carregar l'ortofoto, o una capa de tessel·les (p. ex. ESRI World Imagery com a tessel·les XYZ)
- Comprovar el sistema de referència del projecte
- Per escriure a les US: carregar `pyunitastratigrafiche` (o `pyunitastratigrafiche_usm`) i comprovar el lloc a la configuració
- La primera vegada, per als models locals: «Instal·la / actualitza» i després «Descarrega els pesos»

**2. Configuració**
- «Imatge»: capa ràster, extensió, resolució (per a les tessel·les) i costat màxim
- «Què cal segmentar»: el mode, el llindar i, per a les classes de text, les classes
- «Model»: un model local amb els pesos presents, o un model al núvol amb la seva clau
- «Destinació»: la capa i els seus atributs

**3. Execució**
- «Inicia», o «Inicia la selecció» i després punts, rectangle o polígon al mapa
- Seguir la línia d'estat; «Cancel·la» interromp la feina
- Al final apareix «Fet: N polígons afegits a “capa” (model).» (*Done: N polygons added to “layer” (model).*)

**4. Postprocessament**
- Revisar els polígons; els possibles avisos apareixen a la barra de missatges de QGIS
- Capes US: assignar els números d'US (`us_s`) a la taula d'atributs
- Corregir, unir o esborrar els polígons erronis amb les eines d'edició de QGIS
- Capa temporal: exportar-la si cal conservar-la

## Integració Cartogràfica

### Exportació Dades GIS

Des de la Fitxa US, pestanya Map:
- **Export GeoPackage**: Capa com GPKG
- **Export Shapefile**: Capa com SHP
- **Export GeoJSON**: Capa com JSON

### Importació Dades GIS

Importar geometries existents:
1. Carregar capa a QGIS
2. Seleccionar feature
3. Usar funció import

### Geoprocessament

Operacions espacials disponibles:
- Buffer
- Intersecció
- Unió
- Diferència
- Centroids

## Bones Pràctiques

### 1. Ortofotos

- Resolució mínima: 1-2 cm/píxel
- Format: GeoTIFF georeferenciat
- Sistema referència: coherent amb projecte

### 2. Digitalització

- Usar snap per a precisió
- Verificar topologia
- Mantenir consistència atributs

### 3. SAM Segmentation

- Ortofoto de bona qualitat, il·luminació uniforme, bon contrast entre objectes i fons
- **Ortofotos grans**: treballar per vista o per rectangle, no sobre «tot el ràster». SAM treballa a 1024 px interns i, per sobre del «Costat màxim (px):», la imatge es redueix: en una àrea massa gran els objectes petits es perden
- **Tessel·les**: triar un nivell de zoom en què els objectes es reconeguin a simple vista (p. ex. 0,3–0,6 m/px per a edificis i carreteres). La «Resolució (unitats de mapa/px):» proposa la de la vista; si l'extensió és gran, la imatge es redueix al costat màxim i la resolució real empitjora
- **Classes de text**: substantius anglesos senzills (building, road, river, field, stone, wall)
- Les classes només les donen YOLOE o SAM 3: SAM 2.1 en «Tot (automàtic)» troba contorns però no assigna classes
- **Maquinari**: els Mac amb Apple Silicon fan servir MPS, una targeta NVIDIA fa servir CUDA i, si no, la CPU, més lenta (millor aleshores SAM 2.1 Tiny o Small, YOLOE-26 S i àrees petites)
- Post-verificació sempre necessària

### 4. Organització Capes

- Agrupar per tipologia
- Usar estils consistents
- Mantenir ordre a la llegenda

## Resolució de Problemes

### Capes No Visualitzades

**Causes possibles**:
- Extensió errònia
- Sistema referència diferent
- Filtre actiu

**Solucions**:
- Zoom to Layer
- Verificar CRS
- Eliminar filtres

### SAM No Funciona

| Missatge o símptoma | Què cal fer |
|---------------------|-------------|
| «Entorn local» en taronja: «no instal·lat…» (*not installed…*), o «L'entorn local no està instal·lat: premeu “Instal·la / actualitza” (o trieu un model al núvol).» (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | Prémer «Instal·la / actualitza». Cal un Python del sistema 3.10–3.13; si no n'hi ha, apareix `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (no s'ha trobat cap Python 3.10–3.13: instal·leu Python des de python.org o Homebrew). Si pip falla, l'error és a «Mostra el registre». A Linux sense targeta NVIDIA s'instal·la torch per a CPU |
| «falten els pesos (~N MB)» (*weights missing (~N MB)*), o «Falten els pesos del model: premeu “Descarrega els pesos”.» (*The model weights are missing: press “Download weights”.*) | Prémer «Descarrega els pesos» (cal connexió a internet) |
| «Cal la clau API del servei.» (*The service API key is needed.*) | Amb un model al núvol, enganxar la clau a «Clau API:» (vegeu «Configuració API») |
| «No s'ha trobat cap polígon: proveu una àrea més petita, un llindar més baix o un altre model.» (*No polygon found: try a smaller area, a lower threshold or another model.*) | Extensió més petita, «Llindar:» més baix, un altre model (un SAM 2.1 més gran, o les classes de text); per a les tessel·les, una resolució més fina |
| «L'àrea triada no cobreix el ràster» (missatge en italià: `l'area scelta non copre il raster`) | La vista, el rectangle o el polígon queden fora del ràster: enquadrar el ràster i tornar-ho a provar |
| «Ompliu l'àrea per a la capa US.» (*Fill in the area for the US layer.*) | Escriure l'«Àrea:» al grup «Destinació» |
| «Ràster girat: no admès (reprojecteu-lo abans)» (missatge en italià: `raster ruotato: non supportato (riproiettalo prima)`) | Reprojectar el ràster amb gdalwarp (menú Ràster de QGIS) i fer servir el fitxer nou |
| «La segmentació ha fallat» (*Segmentation failed*) amb les últimes línies del worker | Llegir les línies del missatge; tornar-ho a provar amb una extensió o un «Costat màxim (px):» més petits, o amb un model més petit |

### Geometries Corruptes

**Causes possibles**:
- Errors de digitalització
- Import problemàtic

**Solucions**:
- Usar "Fix Geometries"
- Redibuixar element

### Capa carregada però geometries no visibles (SQLite)

**Símptoma**:
- Una capa pyArchInit d'una base de dades SQLite/SpatiaLite (p. ex. US `pyunitastratigrafiche`, USM, materials, US negatives) es carrega i la taula d'atributs mostra els registres, però al mapa no es dibuixa res i "Zoom to Layer" no funciona

**Causa**:
- L'índex espacial (R*Tree) de la capa no s'ha mantingut: els seus triggers es van perdre quan es va recrear una taula (p. ex. amb antics scripts d'actualització de l'esquema) o les dades es van importar saltant-los
- QGIS tria les entitats a dibuixar mitjançant aquest índex, per tant resten invisibles
- També s'hi veuen afectades les bases de dades creades amb la plantilla SQLite entre octubre de 2025 i setembre de 2026

**Solució (automàtica)**:
- En connectar-se a una base de dades SQLite, pyArchInit comprova tots els índexs espacials (uns instants; si la base de dades està sana no escriu res) i reconstrueix automàticament els malmesos
- Des de la versió 5.13.16-alpha la mateixa comprovació repara també les **vistes espacials** (`pyarchinit_us_view`, `pyarchinit_quote_view`, estructures, materials, les vistes UT, etc.):
  - cada vista es vincula al ROWID de la seva taula geomètrica
  - s'eliminen els registres de vistes que ja no existeixen
  - es tornen a crear les vistes estàndard que falten
  - les vistes UT es registren com a vistes espacials
  - les taules geomètriques sense índex espacial en reben un: cal quan el GDAL inclòs amb QGIS no té les funcions SpatiaLite (p. ex. QGIS a macOS), on sense índex aquestes capes no dibuixaven res
- Abans de modificar res desa UNA sola còpia de seguretat al costat de la base de dades: `<base_de_dades>.sqlite.pre_spatial_index_repair_<data-hora UTC>`
- El resultat s'escriu al tauler de missatges de registre de QGIS (View → Panels → Log Messages), pestanya "PyArchInit"

**Què fer**:
- No cal iniciar res a mà: la comprovació s'executa automàticament a la PRIMERA connexió a cada base de dades en cada sessió de QGIS (és a dir, després d'actualitzar el plugin o de reiniciar QGIS)
- Si les capes ja estaven carregades, treure-les i tornar-les a afegir (o reobrir el projecte) després de la reparació
- Si el registre "PyArchInit" indica que un índex NO s'ha pogut reparar (p. ex. SpatiaLite no es pot carregar), resoldre la causa i reiniciar QGIS: la comprovació només es repeteix en una nova sessió
- El fitxer de còpia de seguretat es pot eliminar un cop verificades les capes
- Per repetir la comprovació (p. ex. després de restaurar una còpia de seguretat), reiniciar QGIS
- Nota: a `inventario_materiali_view` el punt del lloc es repeteix per a cada material, per això "Identify" sobre aquest punt mostra un dels materials

## Referències

### Fitxers Font
- `modules/gis/pyarchinit_pyqgis.py` - Integració GIS
- `tabs/Sam_Segmentation_Dialog.py` - Finestra SAM: grups, modes, destinació
- `modules/utility/sam_environment.py` - Entorn Python separat, paquets i pesos
- `modules/gis/sam_raster_source.py` - Imatge que se segmenta (retall GDAL o renderitzat de la vista) i georeferència
- `modules/gis/sam_map_tools.py` - Eines de mapa per a punts, rectangle i polígon
- `scripts/sam_worker.py` - Worker fora de QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

### Capes
- `pyunitastratigrafiche` - US dipòsit
- `pyunitastratigrafiche_usm` - US muràries
- `pyarchinit_quote` - Cotes

---

## Vídeo Tutorial

### Integració GIS
`[Placeholder: video_gis_integration.mp4]`

**Continguts**:
- Capes predefinides
- Visualització US
- Estilització i etiquetes
- Exportació cartogràfica

**Durada prevista**: 15-18 minuts

### Segmentació SAM
`[Placeholder: video_sam_segmentation.mp4]`

**Continguts**:
- Configuració SAM
- Modes de segmentació
- Post-elaboració
- Bones pràctiques

**Durada prevista**: 12-15 minuts

---

*Última actualització: Octubre 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/pyarchinit_image_classification_animation.html)
