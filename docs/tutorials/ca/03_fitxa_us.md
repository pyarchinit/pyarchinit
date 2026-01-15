# PyArchInit - Fitxa US/USM (Unitat Estratigràfica)

## Índex
1. [Introducció](#introducció)
2. [Conceptes Fonamentals](#conceptes-fonamentals)
3. [Accés a la Fitxa](#accés-a-la-fitxa)
4. [Interfície General](#interfície-general)
5. [Camps Identificatius](#camps-identificatius)
6. [Pestanya Localització](#pestanya-localització)
7. [Pestanya Dades Descriptives](#pestanya-dades-descriptives)
8. [Pestanya Periodització](#pestanya-periodització)
9. [Pestanya Relacions Estratigràfiques](#pestanya-relacions-estratigràfiques)
10. [Pestanya Dades Físiques](#pestanya-dades-físiques)
11. [Pestanya Dades de Fitxació](#pestanya-dades-de-fitxació)
12. [Pestanya Mesures US](#pestanya-mesures-us)
13. [Pestanya Documentació](#pestanya-documentació)
14. [Pestanya Tècnica Edilícia USM](#pestanya-tècnica-edilícia-usm)
15. [Pestanya Lligants USM](#pestanya-lligants-usm)
16. [Pestanya Mèdia](#pestanya-mèdia)
17. [Pestanya Ajuda - Tool Box](#pestanya-ajuda---tool-box)
18. [Matriu de Harris](#matriu-de-harris)
19. [Funcionalitats GIS](#funcionalitats-gis)
20. [Exportacions](#exportacions)
21. [Flux de Treball Operatiu](#flux-de-treball-operatiu)
22. [Resolució de Problemes](#resolució-de-problemes)

---

## Introducció

La **Fitxa US/USM** (Unitat Estratigràfica / Unitat Estratigràfica Murària) és el cor de la documentació arqueològica a PyArchInit. Representa l'eina principal per registrar tota la informació relativa a les unitats estratigràfiques identificades durant l'excavació.

Aquesta fitxa implementa els principis del **mètode estratigràfic** desenvolupat per Edward C. Harris, permetent documentar:
- Les característiques físiques de cada estrat
- Les relacions estratigràfiques entre les unitats
- La cronologia relativa i absoluta
- La documentació gràfica i fotogràfica associada

---

## Conceptes Fonamentals

### Què és una Unitat Estratigràfica (US)

Una **Unitat Estratigràfica** és la unitat d'excavació més petita identificable i distingible de les altres. Pot ser:
- **Estrat**: dipòsit de terra amb característiques homogènies
- **Interfície**: superfície de contacte entre estrats (ex. tall de fossa)
- **Element estructural**: part d'una construcció

### Tipus d'Unitats

| Tipus | Codi | Descripció |
|-------|------|------------|
| US | Unitat Estratigràfica | Estrat genèric |
| USM | Unitat Estratigràfica Murària | Element constructiu murari |
| USVA | Unitat Estratigràfica Vertical A | Alçat vertical tipus A |
| USVB | Unitat Estratigràfica Vertical B | Alçat vertical tipus B |
| USVC | Unitat Estratigràfica Vertical C | Alçat vertical tipus C |
| USD | Unitat Estratigràfica de Demolició | Estrat d'enderroc/demolició |
| CON | Dovelles | Blocs arquitectònics |
| VSF | Virtual Stratigraphic Feature | Element virtual |
| SF | Stratigraphic Feature | Feature estratigràfica |
| SUS | Sub-Unitat Estratigràfica | Subdivisió d'US |
| DOC | Documentació | Element documentari |

### Relacions Estratigràfiques

Les relacions estratigràfiques defineixen les relacions temporals entre les US:

| Relació | Inversa | Significat |
|---------|---------|------------|
| **Cobreix** | Cobert per | L'US se superposa físicament |
| **Talla** | Tallat per | L'US interromp/travessa |
| **Omple** | Omplert per | L'US omple una cavitat |
| **S'adossa a** | Li s'adossa | Relació d'adossament |

---

## Accés a la Fitxa

Per accedir a la Fitxa US:

1. Menú **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. O des de la barra d'eines PyArchInit, fer clic a la icona **US/USM**

---

## Interfície General

La Fitxa US està organitzada en diverses àrees funcionals:

### Àrees Principals

| # | Àrea | Descripció |
|---|------|------------|
| 1 | **Camps Identificatius** | Lloc, Àrea, US, Tipus, Definicions |
| 2 | **Barra d'eines DBMS** | Navegació, desament, cerca |
| 3 | **Pestanyes Dades** | Fitxes temàtiques per a les dades |
| 4 | **Barra d'eines GIS** | Eines de visualització de mapa |
| 5 | **Pestanya Tool Box** | Eines avançades i Matriu |

### Barra d'Eines DBMS

| Botó | Funció | Descripció |
|------|--------|------------|
| **New record** | Nou | Crea una nova fitxa US |
| **Save** | Desa | Desa les modificacions |
| **Delete** | Elimina | Elimina la fitxa actual |
| **View all** | Veure tots | Mostra tots els registres |
| **First/Prev/Next/Last** | Navegació | Navega entre els registres |
| **new search** | Cerca | Inicia mode de cerca |
| **search !!!** | Executa | Executa la cerca |
| **Order by** | Ordena | Ordena els registres |
| **Report** | Imprimeix | Genera informe PDF |
| **Llistat US/Fotos** | Llista | Genera llistats |

---

## Camps Identificatius

Els camps identificatius sempre són visibles a la part superior de la fitxa.

### Camps Obligatoris

| Camp | Descripció | Format |
|------|------------|--------|
| **Lloc** | Nom del lloc arqueològic | Text (de combobox) |
| **Àrea** | Número de l'àrea d'excavació | Número enter (1-20) |
| **US/USM** | Número de la unitat estratigràfica | Número enter |
| **Unitat tipus** | Tipus d'unitat (US, USM, etc.) | Selecció |

### Camps Descriptius

| Camp | Descripció |
|------|------------|
| **Definició estratigràfica** | Classificació estratigràfica (del tesaurus) |
| **Definició interpretativa** | Interpretació funcional (del tesaurus) |

### Definicions Estratigràfiques (Exemples)

| Definició | Descripció |
|-----------|------------|
| Estrat | Dipòsit genèric |
| Rebliment | Material de farciment |
| Tall | Interfície negativa |
| Pla d'ús | Superfície de trepig |
| Enderroc | Material d'enderroc |
| Pisonat | Pavimentació en terra piconada |

### Definicions Interpretatives (Exemples)

| Definició | Descripció |
|-----------|------------|
| Activitat de construcció | Fase constructiva |
| Abandonament | Fase d'abandonament |
| Pavimentació | Pla pavimentat |
| Mur | Estructura murària |
| Fossa | Excavació intencional |
| Anivellament | Estrat de preparació |

---

## Pestanya Localització

Conté les dades de posicionament dins de l'excavació.

### Camps de Localització

| Camp | Descripció | Notes |
|------|------------|-------|
| **Sector** | Sector d'excavació | Lletres A-H o números 1-20 |
| **Quadre/Paret** | Referència espacial | Per excavacions en quadrícula |
| **Ambient** | Número de l'ambient | Per edificis/estructures |
| **Sondeig** | Número del sondeig | Per sondeigs de verificació |

### Números de Catàleg

| Camp | Descripció |
|------|------------|
| **Nr. Cat. General** | Número catàleg general |
| **Nr. Cat. Intern** | Número catàleg intern |
| **Nr. Cat. Internacional** | Codi internacional |

---

## Pestanya Dades Descriptives

Conté la descripció textual de la unitat estratigràfica.

### Camps Descriptius

| Camp | Descripció | Suggeriments |
|------|------------|--------------|
| **Descripció** | Descripció física de l'US | Color, consistència, composició, límits |
| **Interpretació** | Interpretació funcional | Funció, formació, significat |
| **Elements datants** | Materials per a datació | Ceràmica, monedes, objectes datants |
| **Observacions** | Notes addicionals | Dubtes, hipòtesis, comparacions |

### Com Descriure una US

**Descripció física:**
```
Estrat de terra argilosa, de color marró fosc (10YR 3/3),
consistència compacta, amb inclusions de fragments de maó (2-5 cm),
còdols calcaris (1-3 cm) i carbó. Límits nets a dalt,
difusos a baix. Gruix variable 15-25 cm.
```

**Interpretació:**
```
Estrat d'abandonament format arran de la cessació de les
activitats a l'ambient. La presència de material edilici
fragmentat suggereix un enderroc parcial de les estructures.
```

---

## Pestanya Periodització

Gestiona la cronologia de la unitat estratigràfica.

### Periodització Relativa

| Camp | Descripció |
|------|------------|
| **Període Inicial** | Període de formació |
| **Fase Inicial** | Fase de formació |
| **Període Final** | Període d'obliteració |
| **Fase Final** | Fase d'obliteració |

**Nota**: Els períodes i les fases s'han de crear primer a la **Fitxa de Periodització**.

### Cronologia Absoluta

| Camp | Descripció |
|------|------------|
| **Datació** | Data absoluta o interval |
| **Any** | Any d'excavació |

### Altres Camps

| Camp | Descripció | Valors |
|------|------------|--------|
| **Activitat** | Tipus d'activitat | Text lliure |
| **Estructura** | Codi estructura associada | De Fitxa Estructura |
| **Excavat** | Estat d'excavació | Sí / No |
| **Mètode d'excavació** | Modalitat d'excavació | Mecànic / Estratigràfic |

---

## Pestanya Relacions Estratigràfiques

**Aquesta és la pestanya més important de la fitxa US.** Defineix les relacions estratigràfiques amb les altres unitats.

### Estructura de la Taula de Relacions

| Columna | Descripció |
|---------|------------|
| **Lloc** | Lloc de l'US correlacionada |
| **Àrea** | Àrea de l'US correlacionada |
| **US** | Número US correlacionada |
| **Tipus de relació** | Tipus de relació |

### Tipus de Relacions Disponibles

| Català | Anglès | Alemany |
|--------|--------|---------|
| Cobreix | Covers | Liegt über |
| Cobert per | Covered by | Liegt unter |
| Talla | Cuts | Schneidet |
| Tallat per | Cut by | Geschnitten von |
| Omple | Fills | Verfüllt |
| Omplert per | Filled by | Verfüllt von |
| S'adossa a | Abuts | Stützt sich auf |
| Li s'adossa | Supports | Wird gestützt von |
| Igual a (=) | Same as | Gleich |
| Anterior (>>) | Earlier | Früher |
| Posterior (<<) | Later | Später |

### Inseriment de Relacions

1. Fer clic a **+** per afegir una fila
2. Inserir Lloc, Àrea, US de l'US correlacionada
3. Seleccionar el tipus de relació
4. Desar

### Botons de Relacions

| Botó | Funció |
|------|--------|
| **+** | Afegeix fila |
| **-** | Elimina fila |
| **Insert or update inverse relat.** | Crea automàticament la relació inversa |
| **Vés a l'US** | Navega a l'US seleccionada |
| **visualitza matriu** | Mostra la Matriu de Harris |
| **Fix** | Corregeix errors a les relacions |

### Relacions Inverses Automàtiques

Quan insereixes una relació, pots crear automàticament la inversa:

| Si insereixes | Es crea |
|---------------|---------|
| US 1 **cobreix** US 2 | US 2 **coberta per** US 1 |
| US 1 **talla** US 2 | US 2 **tallada per** US 1 |
| US 1 **omple** US 2 | US 2 **omplerta per** US 1 |

### Control de Relacions

El botó **Check relacions** verifica la coherència de les relacions:
- Detecta relacions mancants
- Troba inconsistències
- Senyala errors lògics

---

## Pestanya Dades Físiques

Descriu les característiques físiques de la unitat estratigràfica.

### Característiques Generals

| Camp | Valors |
|------|--------|
| **Color** | Marró, Groc, Gris, Negre, etc. |
| **Consistència** | Argilosa, Compacta, Friable, Sorrenca |
| **Formació** | Artificial, Natural |
| **Posició** | - |
| **Mode de formació** | Aportació, Sostracció, Acumulació, Esllavissada |
| **Criteris de distinció** | Text lliure |

### Taules de Components

| Taula | Contingut |
|-------|-----------|
| **Comp. orgànics** | Ossos, fusta, carbons, llavors, etc. |
| **Comp. inorgànics** | Pedres, maons, ceràmica, etc. |
| **Inclusions Artificials** | Materials antròpics inclosos |

Per a cada taula:
- **+** Afegeix fila
- **-** Elimina fila

### Mostratges

| Camp | Valors |
|------|--------|
| **Flotació** | Sí / No |
| **Tamisatge** | Sí / No |
| **Fiabilitat** | Escassa, Bona, Discreta, Òptima |
| **Estat de conservació** | Insuficient, Escàs, Bo, Discret, Òptim |

---

## Pestanya Dades de Fitxació

Informació sobre la compilació de la fitxa.

### Entitat i Responsables

| Camp | Descripció |
|------|------------|
| **Entitat Responsable** | Entitat que gestiona l'excavació |
| **Superintendència** | SABAP competent |
| **Responsable científic** | Director de l'excavació |
| **Responsable de compilació** | Qui ha compilat la fitxa al camp |
| **Responsable de reelaboració** | Qui ha reelaborat les dades |

### Referències

| Camp | Descripció |
|------|------------|
| **Ref. TM** | Referència fitxa TM (Taula Materials) |
| **Ref. RA** | Referència fitxa RA (Troballes Arqueològiques) |
| **Ref. Pottery** | Referència fitxa Ceràmica |

### Dates

| Camp | Format |
|------|--------|
| **Data de rellevament** | DD/MM/AAAA |
| **Data de fitxació** | DD/MM/AAAA |
| **Data de reelaboració** | DD/MM/AAAA |

---

## Pestanya Mesures US

Conté totes les mesures de la unitat estratigràfica.

### Cotes

| Camp | Descripció | Unitat |
|------|------------|--------|
| **Cota absoluta** | Cota sobre el nivell del mar | metres |
| **Cota relativa** | Cota respecte a punt de referència | metres |
| **Cota màx. absoluta** | Cota màxima absoluta | metres |
| **Cota màx. relativa** | Cota màxima relativa | metres |
| **Cota mín. absoluta** | Cota mínima absoluta | metres |
| **Cota mín. relativa** | Cota mínima relativa | metres |

### Dimensions

| Camp | Descripció | Unitat |
|------|------------|--------|
| **Llargada màx.** | Llargada màxima | metres |
| **Amplada mitjana** | Amplada mitjana | metres |
| **Alçada màx.** | Alçada màxima | metres |
| **Alçada mín.** | Alçada mínima | metres |
| **Gruix** | Gruix de l'estrat | metres |
| **Profunditat màx.** | Profunditat màxima | metres |
| **Profunditat mín.** | Profunditat mínima | metres |

---

## Pestanya Documentació

Gestiona les referències a la documentació gràfica i fotogràfica.

### Taula de Documentació

| Columna | Descripció |
|---------|------------|
| **Tipus de documentació** | Foto, Planta, Secció, Alçat, etc. |
| **Referències** | Número/codi del document |

### Tipus de Documentació

| Tipus | Descripció |
|-------|------------|
| Foto | Documentació fotogràfica |
| Planta | Planta d'excavació |
| Secció | Secció estratigràfica |
| Alçat | Alçat murari |
| Aixecament | Aixecament gràfic |
| 3D | Model tridimensional |

### Botons

| Botó | Funció |
|------|--------|
| **insereix fila** | Afegeix referència |
| **elimina fila** | Elimina referència |
| **Actualitza doc** | Actualitza de la taula documentació |
| **Visualitza documentació** | Mostra els documents associats |

---

## Pestanya Tècnica Edilícia USM

Pestanya específica per a les Unitats Estratigràfiques Muràries (USM).

### Dades Específiques USM

| Camp | Descripció |
|------|------------|
| **Llargada USM** | Llargada de la muralla (metres) |
| **Alçada USM** | Alçada de la muralla (metres) |
| **Superfície analitzada** | Percentatge analitzat |
| **Secció murària** | Tipus de secció |
| **Mòdul** | Mòdul constructiu |
| **Tipologia de l'obra** | Tipus de muralla |
| **Orientació** | Orientació de l'estructura |
| **Reutilització** | Sí / No |

### Materials i Tècniques

| Secció | Camps |
|--------|-------|
| **Maons** | Materials, Elaboració, Consistència, Forma, Color, Pasta, Col·locació |
| **Elements Lítics** | Materials, Elaboració, Consistència, Forma, Color, Tall, Col·locació |

### Mostres

| Camp | Descripció |
|------|------------|
| **Mostres morter** | Referències mostres de morter |
| **Mostres maó** | Referències mostres de maons |
| **Mostres pedra** | Referències mostres lítiques |

---

## Pestanya Lligants USM

Descriu les característiques dels lligants (morter) a les estructures muràries.

### Característiques del Lligant

| Camp | Descripció |
|------|------------|
| **Tipus de lligant** | Morter, Fang, Absent, etc. |
| **Consistència** | Tenaç, Friable, etc. |
| **Color** | Color del lligant |
| **Acabat** | Tipus d'acabat |
| **Gruix del lligant** | Gruix en cm |

### Composició

| Secció | Descripció |
|--------|------------|
| **Agregats** | Components grossers |
| **Inerts** | Components fins |
| **Inclusions** | Materials inclosos |

---

## Pestanya Mèdia

Visualitza les imatges associades a la unitat estratigràfica.

### Llista US

La taula mostra totes les US amb les imatges associades:
- Vés a la fitxa
- Checkbox per selecció múltiple
- Previsualització thumbnail

### Botons

| Botó | Funció |
|------|--------|
| **Cerca imatges** | Cerca imatges associades |
| **Save** | Desa associacions |
| **Revert** | Cancel·la modificacions |

---

## Pestanya Ajuda - Tool Box

Conté eines avançades per al control i l'exportació.

### Sistemes de Control

| Eina | Descripció |
|------|------------|
| **Check relacions estratigràfiques** | Verifica coherència de les relacions |
| **Check, go!!!!** | Executa el control |

### Exportació de Matriu

| Botó | Sortida |
|------|---------|
| **Exporta Matriu** | Fitxer DOT per Graphviz |
| **Export Graphml** | Fitxer GraphML per yEd |
| **Export to Extended Matrix** | Format S3DGraphy |
| **Interactive Matrix** | Visualització interactiva |

### Eines Addicionals

| Eina | Descripció |
|------|------------|
| **Ordre estratigràfic** | Calcula seqüència estratigràfica |
| **Crea Codi Període** | Genera codis de període |
| **csv2us** | Importa US des de CSV |
| **Graphml2csv** | Exporta GraphML a CSV |

### Funcions GIS

| Botó | Funció |
|------|--------|
| **Dibuixa US** | Carrega capa per dibuix |
| **Preview planta US** | Previsualització al mapa |
| **Obre fitxes US** | Obre fitxes seleccionades |
| **Pan** | Eina panoràmica |
| **Mostra imatges** | Visualitza fotos |

### Exportacions de Taules

| Botó | Sortida |
|------|---------|
| **Exportació Taules** | Taules d'excavació |
| **symbology** | Gestió de simbologia |
| **Open folder** | Obre carpeta de sortida |

---

## Matriu de Harris

La Matriu de Harris és una representació gràfica de les relacions estratigràfiques.

### Generació de la Matriu

1. Seleccionar el lloc i l'àrea
2. Verificar que les relacions siguin correctes
3. Anar a **Pestanya Ajuda** → **Tool Box**
4. Fer clic a **Export Matrix**

### Formats d'Exportació

| Format | Programari | Ús |
|--------|------------|-----|
| DOT | Graphviz | Visualització bàsica |
| GraphML | yEd, Gephi | Edició avançada |
| Extended Matrix | S3DGraphy | Visualització 3D |
| CSV | Excel | Anàlisi de dades |

### Extended Matrix

L'Extended Matrix afegeix informació suplementària:
- Periodització
- Definicions interpretatives
- Dades cronològiques
- Compatibilitat amb CIDOC-CRM

### Interactive Matrix

Visualització interactiva de la Matriu:
- Zoom i panoràmica
- Selecció de nodes
- Navegació a les fitxes

---

## Funcionalitats GIS

La Fitxa US està estretament integrada amb QGIS.

### Barra d'Eines GIS

| Botó | Funció | Drecera |
|------|--------|---------|
| **GIS Viewer** | Carrega capes US | Ctrl+G |
| **Preview planta US** | Previsualització geometria | Ctrl+G |
| **Dibuixa US** | Activa dibuix | - |

### Capes GIS Associades

| Capa | Geometria | Descripció |
|------|-----------|------------|
| PYUS | Polígon | Unitats estratigràfiques |
| PYUSM | Polígon | Unitats muràries |
| PYQUOTE | Punt | Cotes |
| PYQUOTEUSM | Punt | Cotes USM |
| PYUS_NEGATIVE | Polígon | US negatives |

### Visualització de Resultats de Cerca

Quan el mode GIS està actiu:
- Les cerques es visualitzen al mapa
- Els resultats estan ressaltats
- Es pot navegar entre els resultats

---

## Exportacions

### Fitxes US PDF

1. Fer clic a **Report** a la barra d'eines
2. Escollir format (PDF, Word)
3. Seleccionar les fitxes a exportar

### Llistats

| Tipus | Contingut |
|-------|-----------|
| **Llistat US** | Llista de totes les US |
| **Llistat Fotos amb Thumbnail** | Llista amb previsualitzacions |
| **Llistat Fotos sense Thumbnail** | Llista senzilla |
| **Fitxes US** | Fitxes completes |

### Conversió a Word

El botó **Converteix a Word** permet:
1. Seleccionar un PDF
2. Convertir-lo a format DOCX
3. Editar-lo a Word

---

## Flux de Treball Operatiu

### Crear una Nova US

#### Pas 1: Obrir la Fitxa
#### Pas 2: Fer clic a New Record
#### Pas 3: Inserir Identificadors
- Seleccionar Lloc
- Inserir Àrea
- Inserir número US
- Seleccionar Tipus

#### Pas 4: Definicions
- Seleccionar definició estratigràfica
- Seleccionar definició interpretativa

#### Pas 5: Descripció
- Emplenar la descripció física
- Emplenar la interpretació

#### Pas 6: Relacions Estratigràfiques
- Inserir les relacions amb les altres US
- Crear les relacions inverses

#### Pas 7: Dades Físiques i Mesures
- Emplenar característiques físiques
- Inserir les mesures

#### Pas 8: Desar
- Fer clic a Save
- Verificar el desament

### Generar la Matriu de Harris

1. Verificar que totes les relacions estiguin inserides
2. Executar el control de relacions
3. Corregir eventuals errors
4. Exportar la Matriu

### Enllaçar Documentació

1. Crear primer les fitxes a la taula Documentació
2. A la fitxa US, pestanya Documentació
3. Afegir les referències
4. Verificar amb "Visualitza documentació"

---

## Resolució de Problemes

### Error en el desament
- Verificar que Lloc, Àrea i US estiguin emplenats
- Verificar que la combinació sigui única

### Relacions no coherents
- Usar el control de relacions
- Verificar les relacions inverses
- Corregir amb el botó Fix

### La Matriu no es genera
- Verificar que Graphviz estigui instal·lat
- Controlar la ruta a la configuració
- Verificar que hi hagi relacions

### Les capes GIS no es carreguen
- Verificar la connexió a la base de dades
- Controlar que existeixin geometries
- Verificar el sistema de referència

### Imatges no visualitzades
- Verificar les rutes thumbnail
- Controlar les associacions mèdia
- Verificar permisos de carpetes

---

## Notes Tècniques

### Base de Dades

- **Taula principal**: `us_table`
- **Camps principals**: més de 80 camps
- **Clau primària**: `id_us`
- **Clau composta**: lloc + àrea + us

### Tesaurus

Els camps amb tesaurus (definicions) usen la taula `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' per definició estratigràfica
- tipologia_sigla = '1.2' per definició interpretativa

### Capes GIS

| Capa | Taula | Tipus |
|------|-------|-------|
| PYUS | pyarchinit_us_view | Polígon |
| PYUSM | pyarchinit_usm_view | Polígon |
| PYQUOTE | pyarchinit_quote_view | Punt |

---

*Documentació PyArchInit - Fitxa US/USM*
*Versió: 4.9.x*
*Última actualització: Gener 2026*
