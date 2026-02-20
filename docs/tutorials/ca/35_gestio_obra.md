# PyArchInit - Gestio d'Obra (Site Management)

## Index

1. [Introduccio](#introduccio)
2. [Acces al modul](#acces-al-modul)
3. [Tauler d'Obra (Dashboard)](#tauler-dobra-dashboard)
4. [Fitxa de Personal](#fitxa-de-personal)
5. [Fitxa d'Assistencia](#fitxa-dassistencia)
6. [Fitxa d'Equipament](#fitxa-dequipament)
7. [Fitxa de Pressupost](#fitxa-de-pressupost)
8. [Barra d'Eines DBMS](#barra-deines-dbms)
9. [Flux de treball operatiu](#flux-de-treball-operatiu)
10. [Preguntes frequents (FAQ)](#preguntes-frequents-faq)
11. [Notes tecniques](#notes-tecniques)

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

<!-- IMAGE: Seccio comput metric amb selectors de capes DEM i taula historial -->
> **Fig. 5**: Seccio de comput metric amb els controls de calcul i la taula d'historial

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
