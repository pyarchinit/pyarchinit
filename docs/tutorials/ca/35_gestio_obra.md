# PyArchInit - Gestio d'Obra (Site Management)

## Index

1. [Introduccio](#introduccio)
2. [Acces al modul](#acces-al-modul)
3. [Tauler d'Obra (Dashboard)](#tauler-dobra-dashboard)
4. [Fitxa de Personal](#fitxa-de-personal)
5. [Fitxa d'Assistencia](#fitxa-dassistencia)
6. [Fitxa d'Equipament](#fitxa-dequipament)
7. [Fitxa de Pressupost](#fitxa-de-pressupost)
8. [Visualitzacio 2D i 3D del Comput Metric](#visualitzacio-2d-i-3d-del-comput-metric)
9. [Exportacio PDF i CSV del Tauler](#exportacio-pdf-i-csv-del-tauler)
10. [Barra d'Eines DBMS](#barra-deines-dbms)
11. [Flux de treball operatiu](#flux-de-treball-operatiu)
12. [Preguntes frequents (FAQ)](#preguntes-frequents-faq)
13. [Notes tecniques](#notes-tecniques)

---

## Introduccio

El modul **Gestio d'Obra** de PyArchInit proporciona un conjunt complet d'eines per a la gestio administrativa i logistica d'un lloc d'excavacio arqueologica. A traves de cinc formularis interconnectats, permet controlar el personal, les assistencies, l'equipament, el pressupost i obtenir una visio general en temps real des d'un tauler central.

Aquest modul es especialment util per a:

- **Directors d'excavacio** que necessiten una visio global del projecte
- **Responsables administratius** que gestionen pressupostos i contractes
- **Caps d'equip** que controlen l'assistencia i l'assignacio d'equipament
- **Investigadors** que necessiten calcular computs metrics a partir de dades DEM

<!-- IMAGE: Vista general del modul Gestio d'Obra amb les 5 icones de la barra d'eines -->
> **Fig. 1**: Visio general del modul Gestio d'Obra de PyArchInit amb els cinc components principals

---

## Acces al modul

El modul Gestio d'Obra es accessible des de la **barra d'eines dedicada** de PyArchInit. Hi ha **5 icones** que corresponen als cinc components del modul:

| # | Icona | Formulari | Descripcio |
|---|-------|-----------|------------|
| 1 | Tauler | **Tauler d'Obra** | Dashboard central amb resum i computs |
| 2 | Persona | **Personal** | Gestio del registre de personal |
| 3 | Calendari | **Assistencia** | Control de presencies i jornades |
| 4 | Eina | **Equipament** | Inventari d'eines i maquinaria |
| 5 | Moneda | **Pressupost** | Gestio economica per categories |

### Procediment d'acces

1. Localitzar la barra d'eines **Gestio d'Obra** a la interficie de QGIS
2. Fer clic a la icona corresponent al formulari desitjat
3. El dialeg s'obre connectat automaticament a la base de dades activa

<!-- IMAGE: Barra d'eines Gestio d'Obra amb les 5 icones destacades -->
> **Fig. 2**: La barra d'eines Gestio d'Obra amb les cinc icones identificades

> **Nota**: Si la barra d'eines no es visible, activar-la des de **Vista** > **Barres d'eines** > **PyArchInit - Gestio d'Obra**.

---

## Tauler d'Obra (Dashboard)

El **Tauler d'Obra** es el nucli del modul. Ofereix una visio consolidada de totes les dades del lloc seleccionat, sense necessitat d'obrir cada formulari individualment.

### Selectors principals

A la part superior del tauler hi ha dos selectors que filtren totes les dades mostrades:

| Selector | Descripcio |
|----------|------------|
| **Lloc** | Selector del lloc arqueologic (es preselecciona el lloc configurat) |
| **Any** | Selector de l'any de referencia (els ultims 10 anys) |

El boto **Actualitza** forca la recàrrega de totes les seccions del tauler.

<!-- IMAGE: Selectors de lloc i any a la part superior del tauler -->
> **Fig. 3**: Selectors de lloc i any que filtren totes les dades del tauler

### Seccio Pressupost

Aquesta seccio mostra un resum economic del lloc/any seleccionat:

| Element | Descripcio |
|---------|------------|
| **Import previst** | Suma total dels imports previstos de totes les partides |
| **Import efectiu** | Suma total dels imports efectivament gastats |
| **Barra de progres** | Percentatge d'execucio pressupostaria (efectiu / previst) |
| **Grafic circular** | Distribucio de la despesa per categories |

```
+---------------------------------------------------+
| PRESSUPOST                                         |
+---------------------------------------------------+
| Previst:    EUR 150.000,00                         |
| Efectiu:    EUR  87.500,00                         |
|                                                    |
| [==============              ] 58%                 |
|                                                    |
|    [Grafic circular per categories]                |
+---------------------------------------------------+
```

<!-- IMAGE: Seccio pressupost del tauler amb barra de progres i grafic circular -->
> **Fig. 4**: Resum pressupostari amb barra de progres i grafic de distribucio per categories

### Seccio Personal

Mostra un resum de l'estat del personal per al dia actual:

| Element | Descripcio |
|---------|------------|
| **Presents** | Nombre de treballadors amb jornada laborable avui |
| **Vacances** | Nombre de treballadors en vacances |
| **Malaltia** | Nombre de treballadors de baixa per malaltia |
| **Hores mes** | Total d'hores (ordinaries + extraordinaries) del mes en curs |
| **Cost mes** | Cost total del personal per al mes en curs |

```
+---------------------------------------------------+
| PERSONAL                                           |
+---------------------------------------------------+
| Presents: 12   Vacances: 2   Malaltia: 1          |
|                                                    |
| Hores del mes:  1.248,0                            |
| Cost del mes:   EUR 28.450,00                      |
+---------------------------------------------------+
```

### Seccio Equipament

Mostra l'estat actual de l'inventari d'equipament:

| Element | Descripcio |
|---------|------------|
| **Total** | Nombre total d'equips registrats per al lloc |
| **En us** | Equips amb estat `in_uso` |
| **Manteniment** | Equips amb estat `manutenzione` |
| **Alertes** | Avis vermell si hi ha manteniments vencuts |

```
+---------------------------------------------------+
| EQUIPAMENT                                         |
+---------------------------------------------------+
| Total: 24   En us: 18   Manteniment: 3            |
|                                                    |
| !! 2 scadences manteniment!                        |
+---------------------------------------------------+
```

> **Atencio**: Les alertes de manteniment es mostren en vermell i negreta quan hi ha equips amb la data de proxim manteniment vencuda i que no estan fora de servei.

### Seccio Comput Metric

Aquesta seccio permet calcular diferencies volumetriques a partir de models digitals del terreny (DEM) carregats al projecte QGIS.

#### Metodes de calcul

| Metode | Descripcio |
|--------|------------|
| **Diferencia DEM** | Calcula el volum a partir de la diferencia entre dos DEM (pre i post excavacio) |
| **DEM + Poligon** | Calcula area i volum dins d'un poligon sobre un DEM |

#### Procediment

1. Seleccionar el metode de calcul (radioButton)
2. Triar les capes DEM des dels desplegables (es llisten automaticament les capes raster del projecte)
3. Per al metode DEM + Poligon, seleccionar tambe la capa vectorial de poligons
4. Fer clic a **Calcula**
5. El resultat es mostra i es pot desar amb **Desa comput**

#### Historial de computs

La taula inferior mostra l'historial de tots els computs metrics realitzats per al lloc:

| Columna | Descripcio |
|---------|------------|
| **Data calcul** | Data en que es va realitzar el calcul |
| **Tipus** | Metode de calcul utilitzat |
| **Area (m2)** | Superficie calculada |
| **Volum (m3)** | Volum calculat |
| **Notes** | Observacions |

<!-- IMAGE: Seccio comput metric amb selectors de capes DEM, botons 2D/3D i taula historial -->
> **Fig. 5**: Seccio de comput metric amb els controls de calcul, els nous botons de visualitzacio 2D / 3D i la taula d'historial

A partir de la versio 5.1, al costat del boto **Calcula** tambe hi ha els botons **Mostra 2D**, **Mostra 3D** i **Crea malla 3D** per veure el resultat del calcul directament al mapa i en una vista tridimensional interactiva. Vegeu la seccio [Visualitzacio 2D i 3D del Comput Metric](#visualitzacio-2d-i-3d-del-comput-metric).

### Nou disseny amb pestanyes del Tauler d'Obra

A partir de la versio actual, la finestra **Tauler d'Obra** s'ha reorganitzat en **tres pestanyes** per fer lloc al nou panell d'**Analisi de Costos** sense sobrecarregar la vista. La fila de capcalera amb **Jaciment**, **Any** i el boto **Actualitza** es mante visible sobre les pestanyes, de manera que es pot canviar de jaciment o d'any en qualsevol moment i totes les pestanyes s'actualitzen automaticament.

| Pestanya | Contingut |
|----------|-----------|
| **Resum** | Es la vista que es mostra en obrir el tauler. A dalt, a tota l'amplada, el **Resum de Pressupost** (barra de progres i grafic de sectors); a sota, en paral-lel, els resums de **Personal** i **Equipament** |
| **Comput Metric** | Recull tot el flux de calcul DEM: desplegables **DEM Pre**, **DEM Post** i **Poligon**, botons d'opcio **Diferencia DEM** / **DEM sobre Poligon**, boto **Calcula**, etiquetes d'**area** i **volum**, el nou grup **Analisi de Costos** (EUR/m3, m3/dia -> cost total, dies estimats, cost diari), boto **Desa Registre**, botons **Mostra 2D** / **Mostra 3D** / **Exporta 2DM + 3D** i la **taula d'historial** a baix |
| **Exportacio** | Els botons d'**exportacio PDF** i **CSV** acompanyats d'una breu descripcio |

<!-- IMAGE: Nou disseny amb pestanyes del Tauler d'Obra (Resum / Comput Metric / Exportacio) -->
> **Fig. 5a**: El nou disseny amb pestanyes del Tauler d'Obra amb la capcalera Jaciment / Any / Actualitza sempre visible

**Fix**: els DEM ja no desapareixen en prémer **Calcula** (regressio de la 5.0.13-alpha en que l'actualitzacio automatica dels desplegables reiniciava la seleccio actual).

---

## Visualitzacio 2D i 3D del Comput Metric

A partir de la versio 5.1, despres de fer clic al boto **Calcula** al panell Comput Metric, el Tauler d'Obra ja no nomes mostra els valors numerics (area i volum): crea automaticament un conjunt de capes cartografiques i posa a disposicio una vista 3D interactiva.

### Que passa en fer clic a "Calcula"

En finalitzar un calcul de diferencia DEM, el Tauler executa automaticament els passos seguents:

1. **Desament permanent del raster diferencia**: el raster resultant (DEM post - DEM pre) es desa com a GeoTIFF permanent a `<PYARCHINIT_HOME>/site_dashboard/<nom del lloc>/`. Aixi el raster no es perd en tancar QGIS i es pot reutilitzar en qualsevol moment.
2. **Afegit al projecte QGIS**: el raster s'afegeix al panell de capes dins d'un grup dedicat anomenat **"Site Dashboard - Computi"**, per mantenir organitzats tots els calculs.
3. **Estil automatic**: s'aplica al raster una **rampa de colors divergent**:
   - **Vermell** per a les zones d'excavacio (valors negatius, terra retirada)
   - **Blau** per a les zones d'aportacio (valors positius, terra afegida)
   - **Transparent / neutre** per a celles amb variacio negligible (|diff| <= 1 cm)
4. **Poligonitzacio de l'area d'intervencio**: les celles raster amb |diff| > 1 cm es converteixen en una capa vectorial de poligons, tambe afegida al grup "Site Dashboard - Computi" amb un estil destacat, per mostrar d'un cop d'ull l'extensio total de la intervencio.
5. **Zoom automatic**: el llenc principal del mapa de QGIS es centra automaticament a l'extensio del calcul.

### Requisits

Per utilitzar les noves visualitzacions 2D / 3D cal:

- Tenir **dues capes raster DEM** carregades al projecte QGIS (normalment un DEM **pre** i un DEM **post** excavacio)
- Seleccionar-les als desplegables **DEM Pre** i **DEM Post** del panell Comput Metric
- El sistema de referencia (CRS) dels dos rasters ha de ser coherent

### Nous botons

Al costat del boto **Calcula** hi ha ara tres botons nous:

| Boto | Descripcio |
|------|------------|
| **Mostra 2D** | Torna a centrar el mapa de QGIS a l'extensio del darrer calcul. Util per tornar rapidament al Comput Metric actiu despres d'haver treballat en altres zones. |
| **Mostra 3D** | Obre un dialeg 3D interactiu que utilitza el DEM **pre** com a terreny i hi superposa el raster diferencia. Inclou: un control d'**exageracio vertical**, caselles per activar / desactivar capes individuals i un boto **Reinicia la vista**. |
| **Crea malla 3D** | Construeix malles TIN a partir dels DEMs pre i post (via algorismes de QGIS Processing). Les malles es poden mostrar dins del visualitzador 3D per comparar visualment les dues superficies i el volum entre elles. |

<!-- IMAGE: Els nous botons Mostra 2D, Mostra 3D i Crea malla 3D al costat del boto Calcula -->
> **Fig. 6**: Els nous botons **Mostra 2D**, **Mostra 3D** i **Crea malla 3D** al costat del boto **Calcula**

<!-- IMAGE: Dialeg 3D interactiu amb el DEM pre com a terreny i el raster diferencia superposat -->
> **Fig. 7**: El dialeg 3D interactiu del Comput Metric amb exageracio vertical i control de capes

### Flux de treball tipic

1. Carregar al projecte QGIS els dos rasters DEM (pre i post)
2. Obrir el **Tauler d'Obra**
3. Al panell **Comput Metric** seleccionar els dos DEMs a **DEM Pre** i **DEM Post**
4. Fer clic a **Calcula**: el raster diferencia i el poligon d'intervencio es creen automaticament i el mapa s'ajusta a l'extensio
5. Llegir els valors numerics (area, volum, excavacio, aportacio) directament al panell
6. Fer clic a **Mostra 3D** per obrir la vista tridimensional
7. (Opcional) Fer clic a **Crea malla 3D** per generar i mostrar les malles TIN dels dos DEMs
8. Fer clic a **Desa comput** per arxivar el resultat a l'historial

### Organitzacio al disc

Tots els rasters i capes generats pel Comput Metric es desen a:

```
<PYARCHINIT_HOME>/site_dashboard/<nom del lloc>/
```

on `<PYARCHINIT_HOME>` es la carpeta de treball configurada a la configuracio de PyArchInit i `<nom del lloc>` es el lloc actualment seleccionat al tauler. Aixi es mante un historial fisic de tots els calculs i les capes es poden reutilitzar en altres projectes de QGIS.

### Actualitzacio: "Mostra 2D" -- Dialeg de seccio analitica

A partir de la propera versio, el boto **Mostra 2D** del panell Comput Metric ja no nomes torna a centrar el mapa al darrer calcul: obre un **dialeg analitic basat en matplotlib** que presenta els resultats de l'excavacio com una seccio arqueologica classica.

El dialeg esta disponible **nomes quan el calcul s'ha fet en mode "Diferencia DEM"** (amb DEM pre i DEM post). Si has fet servir el mode **DEM + Poligon**, el boto es comporta com abans i simplement fa zoom del mapa de QGIS a l'extensio del calcul.

Quan esta disponible, el dialeg conte els panells seguents:

| Panell | Descripcio |
|--------|------------|
| **Mapa de calor de la diferencia DEM** | Mapa de calor 2D del raster d'excavacio/aportacio amb una rampa de colors divergent (vermell per a excavacio, blau per a aportacio) |
| **Histograma** | Distribucio de les profunditats d'**excavacio** i les altures d'**aportacio**, per obtenir immediatament un resum estadistic del volum mogut |
| **Seccio longitudinal (E-O)** | La seccio arqueologica classica: el **DEM pre** es dibuixa en **blau**, el **DEM post** en **vermell**, i el volum excavat queda **emplenat** entre les dues linies |
| **Seccio transversal (N-S)** | Mateixa logica que la seccio E-O pero en la direccio Nord-Sud |
| **Spinbox fila / columna** | Permeten desplacar interactivament la posicio de les dues seccions sobre el raster per explorar tota l'excavacio |
| **Boto "Desa PNG"** | Exporta la figura completa (mapa de calor, histograma i les dues seccions) com a imatge PNG, llesta per incloure a l'informe d'excavacio |

<!-- IMAGE: Dialeg analitic Mostra 2D amb mapa de calor, histograma i seccions E-O / N-S -->
> **Fig. 10**: El nou dialeg analitic **Mostra 2D** amb mapa de calor de la diferencia DEM, histograma d'excavacio / aportacio i les dues seccions longitudinal i transversal (DEM pre en blau, DEM post en vermell, volum excavat emplenat entre les dues linies)

### Actualitzacio: "Mostra 3D" -- Alternativa matplotlib

El boto **Mostra 3D** gestiona ara automaticament dos escenaris segons la versio de QGIS instal.lada:

1. **QGIS amb el modul 3D natiu (Qt3D disponible)**: com abans, s'obre el dialeg `Qgs3DMapCanvas` incrustat, amb terreny generat a partir del DEM pre, exageracio vertical i control de capes.
2. **QGIS sense el modul 3D (error "QGIS 3D module not available")**: el Tauler canvia automaticament a un **visualitzador 3D basat en matplotlib**. Com que matplotlib forma part de les dependencies que el plugin ja instal.la, aquest visualitzador **sempre funciona**, fins i tot en compilacions de QGIS sense suport 3D.

El visualitzador alternatiu ofereix:

| Control | Descripcio |
|---------|------------|
| **Mode de visualitzacio** | Tres modes seleccionables: **Pre + Post** (les dues superficies superposades), **Nomes diferencia** (nomes la superficie d'excavacio/aportacio), **Nomes pre** (el DEM pre com a superficie de referencia) |
| **Exageracio vertical** | Un control lliscant per emfatitzar la diferencia de cota entre les dues superficies -- util quan l'excavacio es poc profunda |
| **Rotacio interactiva** | Arrossegant amb el ratoli es pot fer girar l'escena 3D en temps real per explorar l'excavacio des de qualsevol angle |

<!-- IMAGE: Visualitzador 3D matplotlib alternatiu en mode Pre + Post -->
> **Fig. 11**: El visualitzador 3D matplotlib alternatiu, utilitzat quan el modul Qt3D natiu de QGIS no esta disponible: mostra les superficies pre i post amb exageracio vertical ajustable

### Actualitzacio: "Crea malla 3D" -- Estil automatic de terreny

El boto **Crea malla 3D** aplica ara automaticament una **rampa de colors tipus terreny** al grup de datasets d'elevacio de la malla (**Bed Elevation**). Abans la malla semblava una superficie plana i poc llegible; ara es converteix immediatament en un mapa de cotes expressiu:

- **Verd** per a les cotes mes baixes
- **Taronja** per a les cotes intermedies
- **Marro** per a les cotes mes altes

D'aquesta manera la malla es immediatament visible i significativa al mapa de QGIS, fins i tot abans d'obrir la vista 3D. Despres de construir-la nomes cal fer clic a **Mostra 3D** per veure-la renderitzada com a superficie tridimensional, ja sigui a traves del modul 3D natiu de QGIS o del visualitzador matplotlib alternatiu descrit mes amunt.

<!-- IMAGE: Malla 3D amb la nova rampa verd / taronja / marro tipus terreny -->
> **Fig. 12**: La malla 3D amb la nova rampa de colors tipus terreny aplicada automaticament al seu dataset d'elevacio

### Actualitzacio: poligon com a mascara de retall

Si al panell Comput Metric, a mes dels dos DEMs, tambe trieu una capa vectorial al combo **Capa Poligon** deixant activa la modalitat **Diferencia DEM**, el poligon s'utilitza ara com a **mascara de retall**: els dos DEMs es retallen sobre el poligon abans del calcul de la diferencia, de manera que la seccio analitica 2D, l'alternativa 3D amb matplotlib i la malla TIN treballen nomes sobre l'area d'intervencio. El flux tipic es: dibuixar un poligon al voltant de l'excavacio, seleccionar els DEMs pre i post, triar el poligon al combo **Capa Poligon** i fer clic a **Calcula**. Els dos rasters retallats s'afegeixen automaticament al grup **"Cruscotto Cantiere - Computi"** de l'arbre de capes, a punt per ser reutilitzats.

### Actualitzacio: "Crea malla 3D" -- s'han acabat els fallades

Les versions anteriors podien provocar una fallada de QGIS en algunes compilacions a causa d'un segfault C++ dins dels algorismes de Processing utilitzats per construir la malla. La generacio s'ha reescrit en **Python pur**: el Tauler llegeix el DEM amb GDAL i escriu directament un fitxer 2DM amb una **malla de quadrangles en graella regular**, sense dependre dels algorismes natius. El resultat es segur en qualsevol versio de QGIS. Les malles amb mes de **15 000 cel.les** aproximadament es submostren automaticament per mantenir la construccio rapida i el fitxer lleuger, mentre que les cel.les nodata es descarten: quan hi ha una mascara poligonal activa, la malla segueix exactament la forma de l'area d'intervencio retallada. En el rar cas que la generacio falli per altres motius (disc ple, permisos), el dialeg ara suggereix obrir directament **Mostra 3D**, que fa servir el visualitzador matplotlib alternatiu i no necessita cap capa de malla.

### Actualitzacio: refresc automatic dels combos en fer clic a "Calcula"

El panell Comput Metric **ara actualitza automaticament les llistes de DEM i poligon cada vegada que es fa clic a "Calcula"**: ja no cal tancar i tornar a obrir el Tauler d'Obra despres de carregar un nou raster o dibuixar un nou poligon al projecte. Nomes cal afegir la capa a QGIS, tornar al panell i prémer **Calcula** -- els combos **DEM Pre**, **DEM Post** i **Capa Poligon** es reomplen al vol amb l'estat actual del projecte. La possible diagnostica del retall (exit, SRC incompatible, interseccio buida) apareix a la **barra de missatges de QGIS**, de manera que sempre quedi clar quines capes s'han fet servir realment en el calcul.

### Actualitzacio: boto reanomenat "Exporta 2DM + 3D"

El boto anteriorment anomenat **Crea malla 3D** s'ha reanomenat a **Exporta 2DM + 3D** per reflectir el seu nou comportament: **ja no** carrega la malla com a capa al projecte QGIS (l'API de malla nativa pot provocar fallades en algunes compilacions de QGIS) i en el seu lloc realitza dues accions segures i complementaries. Escriu els fitxers **2DM** al disc a partir dels DEMs pre i post (utils per importar-los en programari extern de post-processament) i obre directament la **vista 3D matplotlib** sobre els DEMs retallats, de manera que el resultat es pot valorar visualment de seguida. D'aquesta manera, el risc de fallada queda completament eliminat, perque l'API de malla de QGIS mai no s'utilitza.

### Actualitzacio: retall del poligon amb diagnostica visible

Quan trieu una capa al combo **Capa Poligon** juntament amb els dos DEMs, el retall dels rasters sobre el poligon **ara es registra a la barra de missatges de QGIS**: en cas d'exit es mostra la llista dels fitxers retallats escrits al disc, mentre que en cas de fallada se n'indica el motiu concret (per exemple poligon en un SRC diferent al dels DEMs, cap interseccio geometrica entre poligon i raster, fitxer d'origen no trobat o illegible). Aixi es immediat entendre per que no s'ha aplicat un retall i que cal corregir (reprojectar el poligon, moure'l sobre l'area dels DEMs, revisar el cami del fitxer), sense haver d'obrir els logs ni la consola de Python.

### Actualitzacio: retall del poligon tambe en mode "DEM sobre Poligon"

El retall del poligon funciona ara tambe quan se selecciona el boto de radio **DEM sobre Poligon** (mode d'estadistiques zonals amb un sol DEM): el raster es retalla a l'extensio del poligon **abans** de ser passat als visualitzadors **Mostra 2D**, **Mostra 3D** i **Exporta 2DM + 3D**, de manera que la seccio i la vista 3D mostren nomes l'area d'intervencio en comptes del DEM sencer com passava abans. El missatge de diagnostica del retall apareix a la **barra de missatges de QGIS** exactament igual que en el mode Diferencia DEM. En aquest escenari amb un sol DEM, el visualitzador **Mostra 2D** s'adapta automaticament: la heat-map mostra les cotes amb una rampa de colors **terrain**, l'histograma representa la distribucio de cotes amb la linia de la mitjana, i les dues seccions longitudinal/transversal dibuixen una sola linia de cota (sense emplenat entre pre i post, perque no hi ha DEM post).

### Actualitzacio: Analisi de Costos del Comput Metric

Al panell Comput Metric del Tauler d'Obra s'ha afegit un nou bloc **Analisi de Costos** amb dos parametres d'entrada: **Cost unitari** (en euros/m3) i **Productivitat** (en m3/dia). A cada pulsacio del boto **Calcula**, el panell actualitza automaticament tres valors derivats visibles d'un cop d'ull: **Cost total** (volum x cost unitari), **Dies estimats** (volum / productivitat) i **Cost diari** (cost unitari x productivitat). Les dues entrades es desen automaticament **per obra** a la configuracio de QGIS (claus `pyArchInit/site_dashboard/costs/<obra>/...`), de manera que nomes cal introduir-les una vegada per cada obra: en canviar d'obra els valors desats es tornen a carregar automaticament, i els tres totals es recalculen en temps real amb cada nou comput.

### Actualitzacio: retall pre/post alineat

El calcul de la diferencia DEM requereix que els dos DEM (pre i post) estiguin exactament alineats sobre la mateixa graella de pixels. A les versions anteriors, quan s'utilitzava un poligon de retall, els dos DEM retallats podien acabar sobre graelles lleugerament diferents i el calcul `pre - post` resultava erroni o buit. Ara els dos retalls utilitzen la **resolucio nativa del DEM pre** com a referencia (mateixa `xRes` / `yRes` i mateix alineament de graella), de manera que els dos rasters retallats coincideixen sempre a nivell de pixel i la diferencia produeix un resultat valid. Fins i tot les trinxeres minimes de les quals nomes s'han retirat "10 galledes de terra" (aproximadament 1 m3) es detecten ara correctament al comput.

### Actualitzacio: nou desplegable "Murs / Estructures"

Al panell Comput Metric s'ha afegit un segon desplegable **Murs / Estructures** que permet seleccionar una capa de poligons que representen murs, estructures en alcat, pilars o altres elements construits que **no s'han de comptar** en el calcul dels metres cubics d'excavacio. Quan es prem **Calcula**, els poligons dels murs es rasteritzen com a NODATA sobre el raster de diferencia retallat i les seves cel-les s'exclouen del total de volum; el missatge de diagnostica apareix a la barra de missatges de QGIS (per exemple `walls masked: muri_trincea_42`). Flux de treball arqueologic tipic: carregar DEM pre + DEM post + poligon de l'area d'excavacio + poligon dels murs trobats, seleccionar-los tots dos en els dos desplegables i prement **Calcula** -- el volum excavat exclou automaticament el volum de les estructures.

---

## Exportacio PDF i CSV del Tauler

El Tauler d'Obra permet exportar un resum complet de les dades de gestio en dos formats: **PDF** (document paginat, ideal per lliurar al client o per a arxiu) i **CSV** (ideal per a analisis posteriors en Excel o altres fulls de calcul).

### Exportacio PDF

El boto **Exporta PDF** genera un informe complet de l'obra. A partir de la versio 5.1, el PDF inclou:

- **Portada renovada** amb el nom del lloc, l'any de referencia i la data de generacio
- **Resum de pressupost** amb taules detallades per categoria i totals (previst vs efectiu)
- **Resum de personal** amb estadistiques d'assistencia, hores treballades i costos
- **Resum d'equipament** amb estat de l'inventari i manteniments vencuts
- **Nova seccio "Comput Metric"** que conte:
  - Una taula detallada de tots els calculs desats
  - **Totals**: area total (m2) i volum total (m3)
  - **Estadistiques**: volum d'excavacio, volum d'aportacio, area afectada
- **Nova seccio "Analisi de Costos"** (inserida entre **Comput Metric** i **Estadistiques**) amb una parameter card dels valors configurats (cost unitari en euros/m3 i productivitat en m3/dia), una taula detallada per registre (data, tipus, volum, cost, dies estimats, cost diari) i una fila de **totals** al peu de la taula; el bloc **Estadistiques** s'ha estes amb **cost total** i **dies totals** d'obra
- **Suport complet per a caracters especials**: la generacio del PDF s'ha corregit per a totes les llengues suportades, incloent les lletres accentuades del romanes (**a**, **a**, **i**, **s**, **t**), els caracters **grecs**, **arabs**, **portuguesos** i **catalans**.

### Exportacio CSV

El boto **Exporta CSV** genera un fitxer CSV compatible amb els principals fulls de calcul. A partir de la versio 5.1:

- **Codificacio UTF-8 amb BOM**: garanteix que Excel (especialment la versio europea) obri el fitxer correctament sense malmetre les lletres accentuades i els caracters especials
- **Separador `;`** (punt i coma): compatible amb la configuracio regional europea d'Excel
- **Seccio COMPUTO METRICO**: inclou totes les dades del comput metric, amb tipologia, area, volum i notes de cada calcul
- **Nova seccio `=== ANALISI DE COSTOS ===`**: comenca amb els dos parametres (cost unitari en euros/m3 i productivitat en m3/dia) i continua amb la taula detallada per registre (data, tipus, volum, cost, dies estimats, cost diari), llesta per ser filtrada o agregada a Excel
- **Bloc SUMMARY final ampliat**: un resum agregat amb totals i estadistiques, util per a analisis rapides sense haver d'escriure formules; ara inclou tambe **Cost total** i **Dies totals** calculats a partir de la nova Analisi de Costos

<!-- IMAGE: PDF exportat amb la nova seccio Comput Metric -->
> **Fig. 8**: Exemple de PDF exportat amb la nova seccio **Comput Metric** (taula, totals i estadistiques)

<!-- IMAGE: CSV exportat obert a Excel amb la seccio COMPUTO METRICO i el bloc SUMMARY -->
> **Fig. 9**: Exemple de CSV exportat obert a Excel amb la seccio **COMPUTO METRICO** i el bloc **SUMMARY** final

---

## Fitxa de Personal

La **Fitxa de Personal** permet gestionar el registre complet dels treballadors associats a cada lloc d'excavacio.

### Camps del formulari

#### Camps d'identificacio

| Camp | Camp DB | Descripcio | Obligatori |
|------|---------|------------|------------|
| **Lloc** | `sito` | Lloc d'excavacio associat | Si |
| **Nom** | `nome` | Nom del treballador | Si |
| **Cognom** | `cognome` | Cognom del treballador | Si |
| **Codi fiscal** | `codice_fiscale` | Document d'identificacio fiscal | No |
| **Data de naixement** | `data_nascita` | Data de naixement | No |
| **Adreca** | `indirizzo` | Adreca de residencia | No |

#### Camps professionals

| Camp | Camp DB | Descripcio |
|------|---------|------------|
| **Qualificacio** | `qualifica` | Titulacio o qualificacio professional |
| **Rol** | `ruolo` | Funcio dins l'equip (director, tecnic, peo, etc.) |
| **Tipus contracte** | `tipo_contratto` | Modalitat contractual |
| **Inici contracte** | `data_inizio_contratto` | Data d'inici del contracte |
| **Fi contracte** | `data_fine_contratto` | Data de finalitzacio del contracte |

#### Camps economics i contacte

| Camp | Camp DB | Descripcio |
|------|---------|------------|
| **Tarifa horaria** | `tariffa_oraria` | Cost per hora del treballador |
| **Tarifa diaria** | `tariffa_giornaliera` | Cost diari del treballador |
| **Email** | `email` | Adreca electronica |
| **Telefon** | `telefono` | Numero de telefon |
| **IBAN** | `iban` | Compte bancari |
| **Notes** | `note` | Camp de text lliure |
| **Actiu** | `attivo` | Indica si el treballador es actiu |

<!-- IMAGE: Formulari de Personal amb tots els camps visibles -->
> **Fig. 6**: La fitxa de Personal amb els camps d'identificacio, professionals i economics

### Operacions CRUD

| Operacio | Procediment |
|----------|-------------|
| **Crear** | Fer clic a *Nou registre*, emplenar els camps, *Desa* |
| **Llegir** | Navegar amb les fletxes o cercar amb *Nova cerca* |
| **Actualitzar** | Modificar els camps desitjats i fer clic a *Desa* |
| **Eliminar** | Navegar al registre, fer clic a *Elimina registre*, confirmar |

---

## Fitxa d'Assistencia

La **Fitxa d'Assistencia** registra la presencia diaria de cada treballador, incloent-hi hores treballades, tipus de jornada i cost associat.

### Camps del formulari

| Camp | Camp DB | Descripcio | Obligatori |
|------|---------|------------|------------|
| **Lloc** | `sito` | Lloc d'excavacio | Si |
| **ID Personal** | `id_personale` | Referencia al treballador | Si |
| **Data** | `data` | Data de la jornada | Si |
| **Tipus jornada** | `tipo_giornata` | Tipus de jornada (veure taula seguent) | Si |
| **Hora entrada** | `ora_ingresso` | Hora d'entrada al lloc | No |
| **Hora sortida** | `ora_uscita` | Hora de sortida del lloc | No |
| **Hores ordinaries** | `ore_ordinarie` | Nombre d'hores ordinaries treballades | No |
| **Hores extra** | `ore_straordinario` | Nombre d'hores extraordinaries | No |
| **Torn** | `turno` | Torn de treball (mati, tarda, etc.) | No |
| **Area de treball** | `area_lavoro` | Area on ha treballat | No |
| **Cost jornada** | `costo_giornata` | Cost total de la jornada | No |
| **Notes** | `note` | Observacions | No |

### Tipus de jornada

| Valor | Descripcio |
|-------|------------|
| `lavorativa` | Jornada laboral ordinaria |
| `ferie` | Vacances |
| `malattia` | Baixa per malaltia |
| `permesso` | Permis especial (personal, sindical, etc.) |

<!-- IMAGE: Formulari d'Assistencia amb la seleccio del tipus de jornada -->
> **Fig. 7**: La fitxa d'Assistencia amb els camps de registre de presencia

> **Nota**: El camp *Cost jornada* es pot calcular automaticament a partir de la tarifa diaria/horaria definida a la fitxa de Personal i les hores registrades.

---

## Fitxa d'Equipament

La **Fitxa d'Equipament** gestiona l'inventari de totes les eines, maquinaria i equips tecnics associats al lloc.

### Camps del formulari

#### Identificacio de l'equip

| Camp | Camp DB | Descripcio | Obligatori |
|------|---------|------------|------------|
| **Lloc** | `sito` | Lloc d'excavacio | Si |
| **Codi inventari** | `codice_inventario` | Codi unic d'inventari | Si |
| **Nom** | `nome` | Nom descriptiu de l'equip | Si |
| **Categoria** | `categoria` | Tipus d'equip (topografia, excavacio, etc.) |
| **Marca** | `marca` | Fabricant | No |
| **Model** | `modello` | Model de l'equip | No |
| **Numero de serie** | `numero_serie` | Numero de serie del fabricant | No |

#### Estat i assignacio

| Camp | Camp DB | Descripcio |
|------|---------|------------|
| **Propietat** | `proprieta` | Propietari de l'equip (propi, lloguer, etc.) |
| **Estat** | `stato` | Estat actual (veure taula seguent) |
| **Assignat a** | `assegnato_a` | Persona o area responsable |

#### Dades economiques i manteniment

| Camp | Camp DB | Descripcio |
|------|---------|------------|
| **Data compra** | `data_acquisto` | Data d'adquisicio |
| **Cost compra** | `costo_acquisto` | Preu d'adquisicio |
| **Cost lloguer/dia** | `costo_noleggio_giorno` | Cost diari de lloguer (si aplica) |
| **Ultima manut.** | `data_ultima_manutenzione` | Data de l'ultim manteniment realitzat |
| **Propera manut.** | `data_prossima_manutenzione` | Data del proxim manteniment programat |
| **Notes** | `note` | Observacions |

### Estats de l'equipament

| Valor | Descripcio |
|-------|------------|
| `in_uso` | L'equip esta operatiu i en us actiu |
| `manutenzione` | L'equip esta en fase de manteniment o reparacio |
| `fuori_uso` | L'equip esta fora de servei (avariat, obsolet, etc.) |

<!-- IMAGE: Formulari d'Equipament amb el selector d'estat i les dates de manteniment -->
> **Fig. 8**: La fitxa d'Equipament amb els camps de gestio d'inventari

> **Atencio**: Quan la data de *Propera manut.* es anterior a la data actual i l'equip no esta *fuori_uso*, el tauler d'obra mostra una alerta vermella.

---

## Fitxa de Pressupost

La **Fitxa de Pressupost** permet registrar i controlar les partides pressupostaries del lloc, comparant imports previstos amb imports reals.

### Camps del formulari

| Camp | Camp DB | Descripcio | Obligatori |
|------|---------|------------|------------|
| **Lloc** | `sito` | Lloc d'excavacio | Si |
| **Any** | `anno` | Any pressupostari | Si |
| **Categoria** | `categoria` | Categoria de despesa (personal, material, etc.) | Si |
| **Descripcio** | `descrizione` | Detall de la partida | No |
| **Import previst** | `importo_previsto` | Quantitat pressupostada | No |
| **Import efectiu** | `importo_effettivo` | Quantitat realment gastada | No |
| **Data registracio** | `data_registrazione` | Data d'entrada del registre | No |
| **Data despesa** | `data_spesa` | Data efectiva de la despesa | No |
| **Proveidor** | `fornitore` | Nom del proveidor o empresa | No |
| **Numero factura** | `numero_fattura` | Referencia de la factura | No |
| **Notes** | `note` | Observacions addicionals | No |

<!-- IMAGE: Formulari de Pressupost amb els camps economics -->
> **Fig. 9**: La fitxa de Pressupost amb els camps de gestio economica

### Exemple de categories pressupostaries

| Categoria | Exemples |
|-----------|----------|
| **Personal** | Sous, dietes, desplacaments |
| **Material** | Eines, consumibles, equip de proteccio |
| **Equipament** | Lloguer de maquinaria, compra d'equips |
| **Laboratori** | Analisis, restauracio, datacions |
| **Logistica** | Transport, allotjament, alimentacio |
| **Documentacio** | Fotografia, topografia, dibuix |

---

## Barra d'Eines DBMS

Tots els formularis CRUD (Personal, Assistencia, Equipament, Pressupost) comparteixen la mateixa barra d'eines DBMS estandard de PyArchInit.

### Indicadors d'estat

| Indicador | Descripcio |
|-----------|------------|
| **DB Info** | Tipus de base de dades connectada (SQLite/PostgreSQL) |
| **Estat** | Mode actual: `Usa` (navegar), `Troba` (cercar), `Nou Registre` |
| **Ordenacio** | `No ordenats` / `Ordenats` |
| **Registre n.** | Numero del registre actual |
| **Registre tot.** | Total de registres |

### Navegacio

| Boto | Funcio |
|------|--------|
| **\|<** | Primer registre |
| **<** | Registre anterior |
| **>** | Registre seguent |
| **>\|** | Ultim registre |

### Gestio de registres

| Boto | Funcio |
|------|--------|
| **Nou registre** | Prepara el formulari per a un nou registre |
| **Desa** | Desa el registre actual (nou o modificat) |
| **Elimina registre** | Elimina el registre actual (amb confirmacio) |
| **Visualitza tots** | Mostra tots els registres |

### Cerca i ordenacio

| Boto | Funcio |
|------|--------|
| **Nova cerca** | Activa el mode de cerca (buidar camps i inserir criteris) |
| **Cerca !!!** | Executa la cerca amb els criteris inserits |
| **Ordena per** | Obre el panell d'ordenacio per camp i direccio |

---

## Flux de treball operatiu

### Configuracio inicial d'un nou lloc

#### Pas 1: Crear el lloc a la Fitxa de Lloc

Abans d'utilitzar el modul Gestio d'Obra, el lloc ha d'existir a la base de dades. Consulteu el [Tutorial Fitxa de Lloc](02_fitxa_lloc.md).

#### Pas 2: Registrar el personal

1. Obrir la **Fitxa de Personal**
2. Fer clic a **Nou registre**
3. Seleccionar el lloc al desplegable
4. Emplenar nom, cognom, qualificacio, rol, dates de contracte i tarifes
5. Fer clic a **Desa**
6. Repetir per a cada membre de l'equip

#### Pas 3: Registrar l'equipament

1. Obrir la **Fitxa d'Equipament**
2. Per a cada equip: nou registre, emplenar codi inventari, nom, categoria, estat, dates de manteniment
3. Desar cada registre

#### Pas 4: Definir el pressupost

1. Obrir la **Fitxa de Pressupost**
2. Crear un registre per a cada partida pressupostaria
3. Indicar l'any, la categoria i l'import previst
4. Desar cada partida

#### Pas 5: Verificar al tauler

1. Obrir el **Tauler d'Obra**
2. Seleccionar el lloc i l'any
3. Verificar que les dades es mostren correctament a totes les seccions

### Gestio diaria

```
1. Obrir el Tauler d'Obra al comencament de la jornada
2. Verificar el resum de personal, equipament i pressupost
3. Registrar les assistencies del dia a la Fitxa d'Assistencia
4. Actualitzar l'estat de l'equipament si cal
5. Registrar despeses al Pressupost quan es produeixin
6. Al final de la jornada, verificar el tauler actualitzat
```

### Comput metric periodic

```
1. Carregar els DEM (pre i post excavacio) al projecte QGIS
2. Obrir el Tauler d'Obra
3. A la seccio Comput Metric:
   a. Seleccionar el metode (Diferencia DEM o DEM + Poligon)
   b. Triar les capes corresponents
   c. Fer clic a Calcula
   d. Revisar els resultats
   e. Fer clic a Desa comput per registrar-ho a l'historial
```

<!-- IMAGE: Flux de treball complet des del registre de personal fins al tauler actualitzat -->
> **Fig. 10**: Diagrama del flux de treball operatiu del modul Gestio d'Obra

---

## Preguntes frequents (FAQ)

### El tauler no mostra dades

**Causa probable**: No hi ha connexio a la base de dades o el lloc seleccionat no te dades.

**Solucions**:
1. Verificar la connexio a la base de dades des de la configuracio de PyArchInit
2. Comprovar que el lloc seleccionat al desplegable es correcte
3. Fer clic a **Actualitza** per forcar la recàrrega
4. Verificar que hi ha registres de pressupost, personal i equipament per al lloc

### L'alerta de manteniment no desapareix

**Causa**: L'alerta es mostra mentre hi hagi equips amb la data de proxim manteniment vencuda i estat diferent de `fuori_uso`.

**Solucio**: Obrir la Fitxa d'Equipament, localitzar l'equip afectat i actualitzar la data de proxim manteniment o canviar l'estat a `fuori_uso`.

### El grafic circular del pressupost no es mostra

**Causa probable**: No hi ha registres de pressupost per al lloc i any seleccionats.

**Solucio**: Verificar que existeixin registres a la Fitxa de Pressupost per al lloc i any actius al tauler.

### Com filtrar les assistencies d'un treballador concret?

1. Obrir la **Fitxa d'Assistencia**
2. Fer clic a **Nova cerca**
3. Seleccionar el lloc i introduir l'ID del treballador al camp corresponent
4. Fer clic a **Cerca !!!**

### El calcul DEM dona error

**Causes probables**:
- No s'han seleccionat les dues capes DEM
- Les capes DEM tenen sistemes de referencia de coordenades (SRC) incompatibles
- Les capes DEM no es superposen espacialment

**Solucions**:
1. Verificar que les dues capes raster estan seleccionades als desplegables
2. Comprovar que ambdues capes tenen el mateix SRC
3. Assegurar-se que les capes cobreixen la mateixa area geografica

### Es poden exportar les dades del tauler?

Actualment, el tauler es una eina de consulta en temps real. Per exportar dades, utilitzar les funcionalitats d'exportacio de cada formulari individual o les eines d'exportacio generals de PyArchInit.

---

## Notes tecniques

### Arquitectura del modul

El modul Gestio d'Obra segueix el patro MVC (Model-View-Controller) estandard de PyArchInit:

| Component | Fitxer | Descripcio |
|-----------|--------|------------|
| **Tauler** (Controller) | `tabs/Cantiere.py` | Dashboard central, calculs DEM |
| **Tauler** (UI) | `gui/ui/Cantiere.ui` | Disseny del tauler Qt Designer |
| **Personal** (Controller) | `tabs/Personale.py` | Gestio CRUD de personal |
| **Personal** (UI) | `gui/ui/Personale.ui` | Disseny del formulari |
| **Assistencia** (Controller) | `tabs/Presenze.py` | Gestio CRUD d'assistencies |
| **Assistencia** (UI) | `gui/ui/Presenze.ui` | Disseny del formulari |
| **Equipament** (Controller) | `tabs/Attrezzature.py` | Gestio CRUD d'equipament |
| **Equipament** (UI) | `gui/ui/Attrezzature.ui` | Disseny del formulari |
| **Pressupost** (Controller) | `tabs/Budget.py` | Gestio CRUD de pressupost |
| **Pressupost** (UI) | `gui/ui/Budget.ui` | Disseny del formulari |

### Taules de la base de dades

| Taula | Entitat | Descripcio |
|-------|---------|------------|
| `personale_table` | `PERSONALE` | Registre de treballadors |
| `presenze_table` | `PRESENZE` | Registre de presencies diaries |
| `attrezzature_table` | `ATTREZZATURE` | Inventari d'equipament |
| `budget_table` | `BUDGET` | Partides pressupostaries |
| `computo_metrico` | `COMPUTO_METRICO` | Historial de computs metrics |

### Compatibilitat

| Component | Versio minima |
|-----------|--------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| PostgreSQL | 12+ (amb PostGIS) |
| SQLite | 3.x (amb Spatialite) |

### Idiomes suportats

El modul es completament traduible i admet els 10 idiomes de PyArchInit: italia (it), angles (en), alemany (de), castella (es), frances (fr), arab (ar), catala (ca), romanes (ro), portugues (pt) i grec (el).

---

*Documentacio PyArchInit - Gestio d'Obra*
*Versio: 5.0.x*
*Ultima actualitzacio: Febrer 2026*
