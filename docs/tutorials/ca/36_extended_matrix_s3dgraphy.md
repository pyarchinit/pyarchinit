# Tutorial 36: Exportació Extended Matrix i Bridge s3dgraphy

## Introducció

A partir de la versió **5.2.0-alpha** PyArchInit integra un **bridge bidireccional** amb la biblioteca **s3dgraphy** (model de dades Extended Matrix d'Emanuel Demetrescu). El bridge permet:

- **Exportar** el diagrama estratigràfic com a Extended Matrix en **em.json**, el format que obre EMStudio (l'antiga exportació GraphML està retirada)
- **Reimportar** modificacions fetes a yEd (moviments d'UE entre períodes/grups) actualitzant la base SQL
- **Adjuntar paradata** (Author / License / Embargo) a nivell de lloc
- **Agrupar** UE per dimensió (struttura, area, attivita, settore, ambient, saggio, quad_par o grups ad-hoc)

Tag actual: `em-media-5.13.122-alpha` (2026-10-16).

---

## 1. Requisits

- Base de dades SQLite/Spatialite **o PostgreSQL/PostGIS**: l'exportació a em.json és la mateixa en els dos motors (la connexió és la del projecte; `export_site` accepta `sqlite://` i `postgresql://`)
- **Migració Phase 1 node_uuid** aplicada automàticament en obrir la DB
- **EMStudio** per obrir l'em.json (s'instal·la des de **Extended Matrix → Installa EMStudio…**), o el panell **Vedi la matrice…** dins del QGIS, que no necessita res més. **yEd** (https://www.yworks.com/products/yed) només cal si importes fitxers GraphML dibuixats allà (§5)

> ⚠️ Per DB pre-5.2.0-alpha la migració pot requerir reiniciar QGIS.

---

## 2. Exportar Extended Matrix (botó verd)

### 2.1 Obrir el diàleg

1. Obre la **Fitxa UE** del lloc desitjat
2. Clica al botó verd **"Esporta Extended Matrix"** (sota la pestanya Rapporti)

### 2.2 Pestanya "Export"

La finestra diu a dalt per a què serveix cada format. Conté:

- **Formati** (Formats): **DOT (Graphviz) — matrice di Harris** i **em.json (Extended Matrix, per EMStudio)**, marcats de sortida, més **Matrice per fasi** (matriu per fases, anàlisi cronològica), opcional. El GraphML ja no s'exporta: el JSON d'aquesta finestra **és l'em.json**, el mateix fitxer que fa el menú **Extended Matrix → Esporta sito in em.json…** — mateix projector, mateixa simbologia.
- **Opzioni** (Opcions): **Controlla la sequenza stratigrafica e segnala i problemi** (comprovar la seqüència estratigràfica i assenyalar els problemes). És l'única opció que queda, i ara es llegeix de debò: sense la marca, la comprovació no es fa. Les dues caselles antigues que parlaven a yEd (pistes d'auto-layout, colors per període) han marxat amb l'exportació GraphML.
- **Extended Matrix**: quatre botons al costat de l'exportació — **Apri in EMStudio** i **Vedi la matrice** (tots dos s'encenen després d'una exportació em.json correcta; el segon dibuixa la matriu dins el QGIS, sense EMStudio), **Consegna alla stanza…** i **Apri la stanza**. Són les mateixes entrades del menú pyArchInit, a l'abast.

En prémer **Esporta** es demana la **carpeta de destinació**.

Autors, llicències, embargaments i grups es gestionen a la finestra **"Manage paradata"** (§3).

### 2.2.1 Sondeigs: un sol graf per a tot el lloc

A partir de la versió **5.13.109-alpha**, l'em.json porta **un sol graf**, amb les unitats de tots els sondeigs: no hi ha res a triar. La finestra «Esporta Extended Matrix» ja no té el grup «Saggi» (sondeigs), i les entrades de menú **Esporta sito in em.json…** i **Vedi la matrice…** només demanen el lloc.

El sondeig és el camp **Saggio** de la fitxa US: continua sent un camp com els altres, que es pot fer servir com a dimensió per agrupar les unitats (`saggio`, §4) i que passa al *dossier* de la narrativa (§10.4), però ja no divideix el fitxer. Un fitxer exportat amb les versions anteriors (fins a la 5.13.108-alpha), amb un graf per sondeig, encara s'obre al panell de la matriu (§10.8).

### 2.3 Clica "Esporta"

Els fitxers que neixen, segons els formats marcats:
- `<lloc>.em.json` — Extended Matrix, per obrir a EMStudio o lliurar a una sala
- `Extended_Matrix_<lloc>[_<area>].dot` — Graphviz DOT, per a la matriu de Harris clàssica
- `Extended_Matrix_<lloc>[_<area>]_phased.json` — vista per època

> **Els llocs viatgen a l'em.json.** La ubicació del lloc, la cadena toponímica i els grups d'àrees, sectors, sondeigs i ambients surten juntament amb les unitats, lligats per arestes `is_in_location` (§4).

El resum final enumera els fitxers i, per a l'em.json, **quants nodes i quantes arestes** han sortit, amb els avisos que hi hagi.

> **Des de la 5.13.122-alpha l'em.json surt més net.** Cada unitat té **una sola** aresta cap a l'època en què neix (abans en tenia dues d'iguals: la biblioteca afegia la seva després d'haver tornat a lligar ja la de l'importador); la **descripció** del node és la definició estratigràfica o, si és buida, la descripció de la fitxa (abans sortia la paraula «None»); el graf té un **nom**, el del lloc (abans EMStudio l'obria com a «Untitled»); una unitat que sobreviu fins a una època més recent té l'aresta `survive_in_epoch` cap a **cada** època intermèdia, no només cap a l'última. Per a un lloc que ve d'un em.json d'EMStudio, vegeu també §5.0, «L'em.json queda recordat».

> **El GraphML ja no s'exporta**: la matriu es mira i es valida a EMStudio, que llegeix em.json. Les files temporals (swimlanes) del GraphML antic han marxat amb ell. El GraphML només sobreviu a l'**entrada**, per als fitxers dibuixats a yEd (§5).

---

## 3. Diàleg "Manage paradata" (4 pestanyes)

### 3.1 Accés
Clica al botó **"Manage paradata"** a la fitxa UE (al costat del botó verd Export).

### 3.2 Les 4 pestanyes

| Pestanya | Contingut | Fitxer generat |
|---|---|---|
| **Authors** | Afegir autors (nom + ORCID + rol) | `paradata_<lloc>.graphml` |
| **Licenses** | Llicència del dataset (ex. CC-BY-NC-4.0 + URL) | ídem |
| **Embargoes** | Dates d'embargament + motiu | ídem |
| **Groups** | Grups ad-hoc (nom + selecció UE membres) | `groups_<lloc>.graphml` |

Els fitxers es desen al costat de la DB SQLite i són **versionables a Git**.

---

## 4. Dimensions i tipus de grup a l'em.json

L'em.json que exporta pyArchInit porta els **grups de lloc** (`LocationNodeGroup`) de la fitxa UE, distingits pel tipus `kind`: `toponym`, la cadena nazione → regione → provincia → comune i la ubicació del lloc (§4.1); `study`, les **àrees**, els **sectors** i els **sondeigs**; `functional`, els **ambients**. Cada unitat està lligada als grups en què es troba per arestes `is_in_location`; l'identificador del grup diu el camp del qual neix (per exemple `loc::area::study::1`). El fitxer no porta colors: els decideix qui el llegeix, EMStudio amb el seu propi estil i el panell de la matriu al QGIS amb les regles visuals de la biblioteca s3dgraphy. L'antiga exportació GraphML donava color als grups per dimensió: aquesta paleta ha quedat retirada amb ella. La biblioteca també sap agrupar per **estructura**, **activitat**, **quadre** i per grups ad-hoc, amb una pertinença primària i les altres secundàries (`is_primary`): pyArchInit avui no li ho demana, i al fitxer aquest atribut només apareix a les arestes de la cadena toponímica, sempre fals.

### 4.1 Cadena toponímica (5.6.0-alpha)

Els camps `site_table.{nazione, regione, provincia, comune}` s'emeten automàticament com a cadena recursiva de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Els nivells administratius buits s'ometen sense trencar la cadena. Una desduplicació cross-lloc garanteix que la mateixa `comune` present en 2 llocs esdevingui **un sol node compartit** a l'em.json.

---

## 4.2 Pertinença multidimensional (5.6.0-alpha)

Una unitat pot estar en diversos grups alhora — una àrea, un sector, un sondeig, un ambient, a més de la ubicació del lloc — i al fitxer té una aresta `is_in_location` per a cadascun, totes en peu d'igualtat. Exemple: una UE amb `area=1`, `settore=1` i `ambient=Ambiente 3` té tres arestes, cap a «1» (àrea, `study`), «1» (sector, `study`) i «Ambiente 3» (`functional`), més la que va cap a la ubicació del lloc, des d'on puja la cadena toponímica. La distinció entre pertinença primària i secundària (`is_primary`, amb `struttura` en primer lloc i `toponym` mai primari) és del model de la biblioteca, per a qui li demana els grups per dimensió: a l'em.json de pyArchInit no hi és.

---

## 5. Round-trip (pestanya Import)

> **Què es pot importar**: la pestanya Import llegeix ara també **em.json** — el d'EMStudio o el del node StratiGraph — i tria el lector segons l'extensió del fitxer; el `.graphml` de yEd continua acceptant-se per als fitxers d'abans. El procediment de sota, moure UE entre grups, es refereix a la via yEd/GraphML.

### 5.0 Importar un em.json d'EMStudio (fins i tot amb la base de dades buida)

Un em.json escrit per **EMStudio** (no per pyArchInit) s'importa a la base de dades de pyArchInit **fins i tot quan la base de dades és buida** (des de la 5.13.121-alpha): el lloc, els períodes, les fitxes, les relacions i els mèdia neixen del fitxer, sense haver de crear abans cap lloc.

1. Obrir el menú **Plugins → pyArchInit - Archaeological GIS Tools** i triar l'entrada **Extended Matrix → Importa em.json…** (Importar em.json): la finestra de l'Extended Matrix s'obre ja a la pestanya **Import**, encara que la base de dades no tingui cap lloc. Des de la fitxa US s'arriba al mateix punt: el botó verd **Esporta Extended Matrix**, sense cap lloc triat, obre la mateixa finestra a la pestanya Import en lloc d'aturar-se (l'**exportació**, en canvi, continua demanant un lloc).
2. Prémer **Browse…** i triar l'em.json.
3. Comprovar el **Sito target:** (lloc de destinació). Si és buit —el cas d'una base de dades sense llocs—, es proposa el nom del graf escrit a l'em.json (per exemple «Temple») o, si falta, el nom del fitxer sense «.em.json»; es pot modificar. Si el camp ja mostra un lloc (amb una base de dades que en té: el de la fitxa US de la qual es parteix o, des del menú, el primer per ordre alfabètic), no es proposa cap nom: escriure el nom del lloc nou o triar aquell on s'ha d'importar. A sota hi ha dues caselles, marcades per defecte: **Crea periodi mancanti se assenti** (Crea els períodes que manquen — si es desmarca i el lloc no té ja els períodes del fitxer, la importació s'atura amb l'error «MissingEpochError») i **Importa anche i media citati (immagini, video, 3D, documenti)** (Importa també els mèdia citats — imatges, vídeos, 3D, documents). A sota hi ha el camp **Cartella dei file** (Carpeta dels fitxers), opcional, amb el botó **Sfoglia…** (Explora…): serveix quan l'em.json s'ha copiat sol, lluny dels fitxers que cita — indicar la carpeta del projecte d'EMStudio (la que conté `EM/`, `DosCo`, `proxies`, `RB`…).
4. Prémer **Anteprima** (Previsualització): no escriu res, i diu quantes fitxes són noves, actualitzades i sense canvis, quants períodes són nous i, en llista, quantes fitxes de quin tipus, quants nodes del fitxer no esdevenen fitxes i quantes unitats tenen el seu **proxy 3D** (des de la 5.13.124-alpha; per a TempluMare «65 unità su 112 hanno il loro proxy 3D.»: les mateixes 65 que mostra EMStudio, que compta 114 unitats perquè inclou també els 2 nodes de continuïtat).
5. Prémer **Applica** (Aplica; s'activa després de la previsualització): importa i mostra el mateix resum, més el dels mèdia.

Què passa, en breu:

- **Què esdevé fitxa.** Només les unitats de les quals pyArchInit coneix el tipus (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt…) i els paradata: propietats (`property`), extractors (`Extractor`), combinadors (`Combinar`) i documents (`DOC`). Els recursos, fitxers, models 3D, formes semàntiques, processos del bessó digital, grups, èpoques i la narrativa **no** esdevenen fitxes: abans de la 5.13.121-alpha esdevenien totes «US».
- **Els noms (camp US).** El nom del node sense el prefix del tipus: USV105 → 105, D.05 → 05, D.05.02 → 05.02. Les propietats que tenen el mateix nom (per exemple «height», que apareix en moltes unitats) reben entre parèntesis el nom de la unitat a la qual pertanyen: «height (105)». Si dos tipus diferents donarien el mateix número —el combinador «C.10» i el document «D.10», la US «SU002» i la USD «USD002»—, el tipus més fort (la US, després les altres unitats, després els documents, els extractors i els combinadors) conserva el número i l'altre conserva el nom complet d'EMStudio («C.10», «USD002»), perquè les relacions no es confonguin.
- **Les relacions.** Entre dues US/USM són les de sempre de pyArchInit («Copre» (cobreix), «Taglia» (talla)…), i la relació «ve després de» (`is_after`: la unitat és més recent que l'altra) entre dues US s'escriu «Copre». Entre unitats de tipus diferents les relacions físiques s'escriuen senceres («Taglia», «Si appoggia a» (es recolza a)), la relació «ve després de» amb `>` (`A > B`: A és més recent que B), i la cadena dels paradata —unitat → propietat → extractor o combinador → document, i la troballa «part de» una troballa virtual— amb `>>`. Els períodes, les activitats, els grups i els recursos no són relacions. A l'exportació, aquests signes tornen a ser les arestes de l'Extended Matrix (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`). Cada relació s'escriu a **les dues** fitxes, invertida a la segona —«Copre»/«Coperto da» (cobreix/cobert per), «Taglia»/«Tagliato da» (talla/tallat per), `>`/`<`, `>>`/`<<`—, com exigeix la verificació de relacions de la fitxa US; una fitxa sense relacions té la llista buida, no el camp buit. Abans de la 5.13.125-alpha la verificació donava «malformed node or string: None» i «Rapporto reciproco non trovato» (relació recíproca no trobada).
- **Activitat i descripció.** L'activitat del node (el grup ActivityNodeGroup) va al camp **Activitat** de la fitxa; la descripció del node, al camp **Descripció**.
- **Periodització.** Les èpoques d'EMStudio, que només tenen nom i dates, es localitzen pel nom a la periodització del lloc; les que no hi són esdevenen períodes nous, des del més antic, numerats després de l'últim període del lloc, en fase 1, amb les dates d'inici i de fi i el nom com a datació estesa. Cada unitat pren el període i la fase inicials de l'època en què neix, i els finals de l'última època en què sobreviu (o iguals als inicials). Els períodes sense **codi de període** el reben en seqüència, 1, 2, 3…, per ordre de període i fase; cada unitat pren la **datació** del seu període inicial i el **codi de període** tal com l'escriu «Crea codice periodo» (Crea codi període) —per exemple 1/2/3 per a una unitat que viu del període 1 al 3—, si encara no els té (des de la 5.13.125-alpha).
- **Fitxa del lloc.** Si el lloc no existeix, es crea. La **definició** és el bé cultural del qual parla l'estudi, si l'em.json el declara, i si no el nom del graf (per a TempluMare «Temple»); **nació, regió, província i municipi** provenen de la cadena d'ubicacions de l'em.json, quan n'hi ha. Els cinc acaben també al **tesaurus** (fitxa del lloc, codis 1.1–1.5), del qual la fitxa del lloc els llegeix. La descripció es pren del graf: nom, codi, autors i posició (EPSG i origen). Si el lloc ja existeix només s'emplena el que és buit, i la definició «Extended Matrix», escrita per les versions anteriors a la 5.13.125-alpha, se substitueix.
- **Mèdia.** Seguint els vincles de l'em.json —fitxa → recurs → fitxer, fitxa → model 3D → recurs → fitxer, i l'url del document o de l'extractor—, els fitxers citats esdevenen mèdia de la fitxa. Es busquen com els busca EMStudio: a la carpeta de l'em.json i a l'arbre del seu projecte EM (`EM/`, `EM/DosCo`, `EM/proxies`, `RB`, `RM`, `SB`), a més de la carpeta del camp **Cartella dei file**, si s'ha indicat. Compten les imatges, els vídeos, els models 3D (també **GLB** i **GLTF**) i els documents (**PDF, Word, Excel, ODT, ODS, RTF, CSV, TXT**). El mèdia apunta al **fitxer original**, com els afegits des de la fitxa; la miniatura i la còpia van a les carpetes **Thumbnail path** i **Image resize** de la configuració (tutorial 01): els models 3D tenen la seva pròpia vista, els PDF la primera pàgina i els altres documents una icona amb el tipus. El **proxy 3D** d'una unitat —al graf és a la seva propietat «geometry»— va a la fitxa de la unitat. Si la propietat la comparteixen diverses unitats —una USV que hereta la geometria de la US que completa—, el proxy va a la unitat que la va crear, com a EMStudio (abans de la 5.13.124-alpha anava a la primera unitat trobada al fitxer). El resum diu quants mèdia són nous i de quin tipus, quants ja hi eren, quantes miniatures, quants fitxers citats no s'han trobat (amb el consell d'indicar la carpeta del projecte), quantes còpies són buides (marcadors de posició del núvol, que cal descarregar de nou), quantes referències externes (web, xarxa, núvol) continuen sent adreces i quins fitxers no són mèdia (`.blend`, `.mtl`, `.zip`…). Un fitxer arxivat en un bucket que té també una còpia al disc (a l'em.json, diverses adreces per al mateix recurs) s'importa des de la còpia del disc; abans de la 5.13.124-alpha continuava sent una referència externa. Una segona importació no duplica res. Abans de la 5.13.122-alpha els fitxers es copiaven a la carpeta principal de pyArchInit, els GLB no tenien miniatura (i la fitxa no els mostrava), els proxies eren a la propietat en lloc de la unitat, i els PDF quedaven fora.
- **Reimportar.** Tornar a importar el mateix fitxer no duplica ni els períodes ni les fitxes: les que ja hi són surten com a «invariate» (sense canvis) o «aggiornate» (actualitzades), i allà on la base de dades i el fitxer difereixen guanya el fitxer (el resum les compta com a «conflitti», conflictes). La previsualització compta com a «aggiornate» també les fitxes a les quals la importació afegeix relacions, datació o codi de període (abans figuraven com a «invariate»). Reimportar l'em.json en una base de dades importada abans de la 5.13.125-alpha la repara: definició del lloc, relacions a les dues fitxes, datació i codis de període.
- **L'em.json queda recordat.** pyArchInit conserva a les seves taules les unitats, els paradata, les relacions i les èpoques; tota la resta del graf —recursos, fitxers, models, formes semàntiques, processos del bessó digital, grups de paradata i d'activitats, autors, llicències, la narrativa—, juntament amb el títol, el **codi de l'estudi** (per exemple GT16: és el prefix amb què Blender torna a lligar els proxies), la georeferenciació (EPSG i desplaçaments) i els noms d'EMStudio, es recorda a la importació (taula `pyarchinit_em_sources`, una fila per lloc; guanya l'última importació). A l'**exportació** de l'em.json del lloc, tot això torna: els noms originals (SU006, D.07.08, height…) per a les fitxes que encara tenen el número donat a la importació —una fitxa reanomenada a pyArchInit conserva el nom nou—, les dades dels nodes (per exemple la propietat «geometry» amb la seva forma, a partir de la qual EMStudio compta els proxies) i els nodes que no són fitxes, amb les seves arestes, lligats a les fitxes que encara existeixen: una branca que ha quedat sense fitxa (per exemple la forma d'una propietat esborrada) no torna. Les relacions, els períodes i les descripcions surten sempre de la base de dades. El missatge del final de l'exportació diu quant ha tornat, per exemple «Dall'em.json importato tornano 851 nomi, 1090 nodi e 1969 archi, codice dello studio GT16.» (De l'em.json importat tornen 851 noms, 1090 nodes i 1969 arestes, codi de l'estudi GT16). Provat a TempluMare_v3.2 (1946 nodes): cap nom ni cap descripció diferents de l'original, i a EMStudio 65 unitats de 114 amb el proxy i 2 èpoques de 3 amb un model, com a l'original. Continuen sent diferents els 9 «ve després de» entre dues US, que pyArchInit escriu «Copre», i els grups d'ubicació del lloc i de l'àrea amb l'estudi, que pyArchInit afegeix.

La via yEd/GraphML, per moure unitats entre grups, és la que segueix.

Per modificar la base SQL movent UE entre grups en GraphML:

1. Obrir el GraphML a **yEd**
2. Arrossegar una UE a un altre grup, desar
3. Tornar al diàleg → pestanya **"Import"**
4. **Marcar** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carregar el GraphML modificat

El sistema executa una transacció atòmica: si alguna cosa falla, **rollback complet** (la DB queda inalterada). Els grups `adhoc` mai escriuen SQL — només actualitzen `groups_<lloc>.graphml`.

A partir de 5.6.0-alpha el walker d'import és **recursiu** i suporta folders niats (p. ex. cadena toponímica `nazione > regione > provincia > comune > UE`). Si es detecten cicles al graf de folders, es llança l'excepció `CycleDetectedError` i s'avorta l'import amb rollback.

---

## 6. CLI (alternativa al diàleg)

Per a scripts / batch:

```bash
# Exportar
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Llistar grups ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Afegir autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = èxit, 1 = error de bridge, 2 = error argparse.

---

## 7. Resolució de problemes

| Símptoma | Causa | Solució |
|---|---|---|
| "no such column: node_uuid" | Migració Phase 1 no executada | Reiniciar QGIS, reobrir la DB |
| GraphML buit | DB sense rapporti / area filter massa estricte | Verificar us_table.rapporti |
| "rapporti han de ser TEXT" | Has introduït un número com a integer | Els camps UE/Area són **TEXT**, no integer |
| Capitalització incorrecta a rapporti | "copre" en minúscula a la DB | Usar "Copre", "Coperto da" capitalitzats |
| `DeprecationWarning` en fitxer 5.5.x | Fitxer legacy `ActivityNodeGroup + group_kind` | El projector el promociona en memòria a `LocationNodeGroup`. Reexporta per migrar el fitxer al disc. |
| Les files de la swimlane mostren un text llarguíssim | Les versions anteriors usaven la Descrizione de la periodització com a etiqueta | Actualitza el plugin i reexporta, i/o omple **Datazione estesa** amb un nom breu |
| Les èpoques de la swimlane estan en ordre incorrecte (ex. Bronze per sobre del Tardoantic) | Les files s'ordenen per **Cronologia Inicial**; les dates aC introduïdes com a nombres positius (1650 en lloc de -1650) s'ordenen com a dC | A la Fitxa Periodització introdueix els anys aC com a nombres negatius i reexporta. El resum de l'exportació mostra ara un avís "⚠️ Periodizzazione: ..." amb la llista de períodes a corregir |

---

## 8. Documentació tècnica

Per aprofundir en arquitectura, decisions de disseny i roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferits:
- **AI08-F3**: heurístiques d'auto-layout (bin-packing de sub-grups) — encara diferit
- **AI09**: TimeBranchNodeGroup mapping — futur
- **Phase 3**: SyncEngine + REST API — futur
- **Phase 4**: GraphDBBackend + SPARQL — futur

Lliurats:
- **AI07** (5.6.0-alpha, 2026-05-10): migració `LocationNodeGroup` amb enum `kind` + cadena toponímica + pertinences multidimensionals
- **AI08-F1** (fusionat en AI07): nesting jeràrquic natiu via `is_primary`

---

## 5. yEd-aware Import — importar graphmls editats externament (5.8.x)

A partir de **5.8.0-alpha** el bridge és **bidireccional també per a graphmls creats directament a yEd** (és a dir, sense passar abans per una exportació pyarchinit). Pyarchinit reconeix automàticament els graphmls «yEd-raw» — aquells que no porten data keys `pyarchinit.*` — i els importa mitjançant un dispatch dedicat que mapeja el prefix del label del node → tipus estratigràfic, reconeix files de TableNode com a períodes, recorre els group folder com a dimensions arqueològiques i deixa que l'usuari triï una política per a les edges que toquen folders.

### 5.1 Desplegament en 6 fites

| Fita | Tag | Què afegeix |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` amb 13 valors (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate des de files de TableNode) + `yed_group_walker.py` (FolderCandidate amb auto-dimension des del prefix del label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orquestrador `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinel `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` amb 5 pàgines (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistència sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Aquesta documentació + dev-log + CHANGELOG. |

### 5.2 Com funciona — flux d'usuari

1. **Obre un graphml a QGIS via el menú Import GraphML** (mateix path que el flux pyarchinit-projected existent).
2. Pyarchinit detecta automàticament que és yEd-raw (sense keys `pyarchinit.*`) → fa dispatch al nou branch en lloc de caure al path legacy.
3. S'obre l'assistent `YedImportDialog` amb **5 pàgines**:
   - **1/5 Classifier** — taula amb una fila per leaf node. Cada fila mostra `label` + `auto_kind` (p. ex. `us_real` / `usv_virtual` / `property`) + un combobox d'override `user_kind`. El botó **Accepta auto** reinicia cada fila al seu `auto_kind` (esborra tots els overrides).
   - **2/5 Periods** — una fila per TableNode-row parsejada, columnes editables `periodo` + `fase`. Les dates (`datazione_iniziale`/`finale`) queden buides: els graphmls yEd-raw no porten dates.
   - **3/5 Folders** — una fila per group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` per excloure). `value` editable (default = `auto_value` derivat del prefix del label).
   - **4/5 Rapporti policy** — 4 radio buttons per tractar les edges que toquen folders:
     - **SKIP** (default): descarta les edges folder-touching. Les edges leaf-to-leaf passen intactes.
     - **FAN_OUT**: una edge `folder_A → folder_B` s'expandeix a `N×M` parells de leaves (producte cartesià dels membres).
     - **REPRESENTATIVE**: utilitza el primer membre de cada folder com a proxy.
     - **SYNTHETIC**: crea una fila us_table per folder (`unita_tipo='VA'` virtual activity) + reconnecta les edges a través d'aquests anchors.
   - **5/5 Preview** — dry-run de `import_yed_raw(overrides=..., dry_run=True)`. Mostra counts (us / inv / period / paradata) **sense commit**. Clic a **Finish** confirma, **Cancel** abandona.
4. En prémer **Finish** l'assistent desa els teus overrides en un **sidecar JSON** `<graphml>.yed_overrides.json` al costat del fitxer. Reobrir el mateix graphml precarrega el sidecar i els teus overrides previs tornen preaplicats.

### 5.3 Encaminament de destinacions

El dispatch fa servir `_classify_destination` (a `yed_import_pipeline.py`) per classificar cada leaf:

| ClassificationKind | Destinació | Nota |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | des de label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | des de `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | des de `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | des de `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivat del prefix del label: USVs/USVn/USVc) | des de `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | des de `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | des de `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | des de `^VSF\d+` |
| DOCUMENT | `paradata` | des de `^D\.\d+` |
| COMBINER | `paradata` | des de `^C\.\d+` |
| PROPERTY | `paradata` | paraula clau al label (`material`/`position`/`width`/...) |

**Decisió de l'usuari 2026-05-13**: les USV* (virtuals) són «unità tipo» (segueixen sent unitats estratigràfiques) i van a `us_table`, no a paradata. Només DOC/COMB/PROP/VIRTUAL_FIND es queden a paradata.

### 5.4 Sidecar JSON — esquema

Versionat per a forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Només es persisteixen els camps MODIFICATS per l'usuari (diff). Els valors `ClassificationKind` desconeguts (p. ex. de futures releases de s3dgraphy) es descarten silenciosament en carregar.

### 5.5 CLI per a ingest scripted

Per a CI / re-runs en batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mútex `--db` / `--conn-str` per a backend SQLite vs PostgreSQL. `--overrides` és opcional (sense overrides = defaults yE-D). `--auto-defaults` és un flag no-op forward-compat.

### 5.6 Limitacions conegudes

- **Sense edició de dates a l'assistent**: els graphmls yEd-raw no porten `datazione_iniziale`/`datazione_finale`. La pàgina Periods només edita `periodo` + `fase` (targets FK).
- **API ParadataStore parcial**: l'upstream s3dgraphy encara no proporciona `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D registra «skip — method missing» per leaf paradata però compta els intents al preview.
- **PropertyNode → Path B (sense enllaç a US)**: els nodes PROPERTY s'escriuen sense US target. L'assistent emet un warning. Futur: follow-up yE-Closure per afegir «assign target» a la UI.
- **Multi-DB**: el sidecar JSON és per graphml, no per DB. Si importes el mateix graphml a DBs diferents, es reutilitzen els mateixos overrides per a totes.

### 5.7 Cobertura de tests final

| Suite | Test | Cobertura |
|---|---|---|
| yE-A | `test_yed_detector.py` | detecció de flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistència sidecar + CLI |

**Suite total post-rollout**: 354 passed / 42 skipped (PG-L1 requereixen psycopg2).

### 5.8 Actualització 5.8.5-alpha (yed-fastfix)

Pack de correccions de comportament sobre `5.8.3-alpha` que millora la qualitat del re-export GraphML després d'un import yEd-aware. Canvis rellevants per a l'usuari final:

- **Paradata multi-folder**: les labels DOC / Combinar / Extractor / property compartides entre diversos folders yEd (p. ex. `material` referenciat des de VA01 + VA04 + VA05) generen ara UNA fila a `us_table` PER ocurrència — visibilitat multi-folder restaurada al GraphML re-exportat. Compromís: el dedup per identitat (col·lapse de `D.01` / `D.01-2` / `D.01bis` en una sola fila) ja no s'aplica a la segona/tercera ocurrència.
- **Rapporti recíprocs**: cada edge yEd `a → b` escriu el rapporto directe sobre la fila d'`a` I l'invers sobre la fila de `b` (`<<` / «Coperto da» / etc.). Els DOC mostren ara totes les connexions extractor entrants al formulari Scheda US.
- **Strip del prefix `us` numèric**: `US100` → `us='100'` `unita_tipo='US'` (abans `us='US100'`). SF/VSF/RSF s'escriuen dualment a `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: la pertinença d'una fila TableNode yEd a un període es propaga a `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva la distinció semàntica EM 1.5.
- **Re-import idempotent**: tornar a executar el mateix import salta les files ja presents; cap rollback per col·lisió UNIQUE en la passada repetida.
- **Paleta USV**: els nodes USV es renderitzen ara amb el paral·lelogram blau canònic d'EM (abans rectangle amb vora vermella).

### 5.9 yE-F paradata multi-carpeta (5.9.0-alpha)

Evolució estructural de `yed-fastfix-5.8.5-alpha`: el compromís del Bug R B1 (una fila `us_table` per ocurrència, amb `us='D.01_2'` / `us='D.01_3'`) ha estat superat. Una fulla paradata (DOC / Combinar / Extractor / property) compartida entre diverses carpetes yEd produeix ara **una sola fila** a `us_table` per label canònic, i la multi-pertinença es preserva en una nova columna `other_locations`.

Canvis visibles per a l'usuari final:

1. **Nou widget "Altres activitats" a la fitxa US/USM**: a la pestanya *Periodizzazione* apareix un `QListWidget` etiquetat "Altres activitats" — visible **només** quan `unita_tipo` és una tipologia paradata (`DOC`, `Combinar`, `Extractor`, `property`). L'usuari pot seleccionar diversos codis d'activitat; la selecció es serialitza com a llista JSON a la nova columna `other_locations`.
2. **Nova entrada de menú QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Cal executar-la **una vegada** a cada DB preexistent per afegir la nova columna (les DB creades post-5.9 ja tenen la columna).
3. **Import yEd-aware millorat**: una fulla paradata que apareix en N carpetes yEd genera ara **només 1** fila `us_table` (ja no N files amb sufix `_2`/`_3` com a 5.8.5). La primera carpeta trobada es converteix en l'`attivita` principal; les carpetes secundàries es llisten a `other_locations`. En **export** s'emeten N còpies visuals yEd (una per carpeta), totes compartint el mateix `node_uuid` canònic per garantir la identitat round-trip.

**Compatibilitat enrere**: les dades produïdes pel Bug R B1 a 5.8.5-alpha (files amb sufix `_2`/`_3`) continuen sent llegibles sense cap conversió automàtica. La nova lògica s'aplica als nous imports; les files legacy continuen comportant-se com abans.

Predecessor: vegeu la secció 5.8 (`yed-fastfix-5.8.5-alpha`) per al comportament substituït.

---

## 6. Generar continuïtat (fitxes CON)

Al panell **«Verifica rapporti»** — disponible com a pestanya dins del diàleg d'importació/exportació de s3dgraphy — hi ha el botó **«Genera continuità»** (etiqueta mantinguda en italià com al connector). Per al jaciment actualment seleccionat, aquesta funció crea automàticament les **fitxes de continuïtat** de les US/USM la vida de les quals abasta més d'un període.

### 6.1 Què fa

1. Escaneja totes les US/USM del jaciment on **període inicial ≠ període final** (és a dir, la vida de les quals abasta més d'un període).
2. Per a cadascuna crea o actualitza una fitxa de continuïtat anomenada **`CON_<us>`** (p. ex. `US5` → `CON_US5`).
3. La fitxa CON **hereta** de la unitat mare: jaciment, àrea (més les àrees secundàries), estructura i tot l'arc de períodes (inicial → final). La seva descripció es genera automàticament.
4. Escriu una **relació de continuïtat recíproca** a tots dos costats: a la CON i a la seva unitat mare.

> **La fase, tota sola, no compta.** La regla mira el **període**: una USM que va de **2/3 a 2/4** —mateix període, només canvia la fase— no genera res. Si les teves unitats sobreviuen de fase en fase dins del mateix període, marca **«anche i salti di fase»** («també els salts de fase») al costat del botó: aleshores aquests salts també compten, sempre que **totes dues** fases estiguin omplertes. Una unitat que no es mou —mateix període i mateixa fase— no és mai una continuïtat. La casella comença **sense marcar**, i val per a la previsualització i per a l'escriptura alhora.

### 6.2 Idempotència

L'operació és **idempotent**: tornar-la a executar no duplica les fitxes existents — actualitza les `CON_<us>` existents si les dades de la unitat mare han canviat.

### 6.3 Previsualització (dry-run) i còpia de seguretat

Abans d'escriure es mostra una **previsualització dry-run** amb els recomptes: quantes fitxes cal **crear**, **actualitzar**, **sense canvis** i quantes **òrfenes**. Els canvis s'apliquen **només després de la confirmació** (botó «Genera»). En aplicar-los es fa primer una **còpia de seguretat de la base de dades** automàtica.

Una fitxa CON és **òrfena** quan la seva unitat mare ja no abasta diversos períodes (p. ex. se n'han igualat el període inicial i final). Per defecte les òrfenes només se **senyalen**; una **casella de selecció** («Rimuovi anche le CON orfane») permet optar per eliminar-les.

**Una continuïtat escrita a mà es reconeix.** Una fitxa CON les relacions de la qual anomenen una sola unitat —`> 12`, o «Continuïtat posterior a 12»— és la continuïtat d'aquella unitat, es digui com es digui: el generador l'**actualitza** (arc de períodes, etiqueta canònica) i el nom continua sent seu. No en neix una segona: la continuïtat és **una per unitat**. Si també existeix una `CON_<us>` canònica, guanya aquesta i l'altra queda com a òrfena per decidir a mà.

### 6.4 A l'exportació Extended Matrix

Les fitxes `CON_<us>` generades així apareixen a l'**em.json** de l'Extended Matrix com a **elements de continuïtat** (l'exportació GraphML està retirada, §2.3).

---

## 7. Verificació de paradoxes temporals (estratigràfics)

Al panell **"Verifica rapporti"** (Verificar relacions — una pestanya del diàleg d'import/export de s3dgraphy), la verificació ara també assenyala les **paradoxes temporals**: quan el període/fase assignat a una unitat contradiu l'estratigrafia observada. L'estratigrafia és la dada de referència, per això les correccions automàtiques desplacen els **períodes**, no les relacions.

### 7.1 Què detecta
- **Inversió temporal**: dues unitats datades unides per una relació d'ordre (p. ex. US5 «cobreix» US7) en què la unitat més recent en l'estratigrafia resulta enterament més **antiga** per període.
- **Contemporaneïtat incoherent**: unitats declarades contemporànies (igualtat física / vincle) però amb intervals cronològics **disjunts**.
- **No avaluable**: relació d'ordre en què almenys una de les dues unitats no té un període datable (només assenyalat, sense correcció).

Nota sobre el límit: dos períodes **adjacents que es toquen** en un únic punt cronològic es consideren superposats → **no** són una paradoxa (benefici del dubte).

### 7.2 Correcció automàtica i suggeriments
- Quan un sol desplaçament resol el conflicte, la verificació proposa desplaçar la unitat **monoperíode** en conflicte amb la majoria dels seus veïns, escollint el període de desplaçament mínim; per a les contemporaneïtats amb una unitat no datable copia el període del veí datat.
- En els casos ambigus — empat, unitats **multiperíode** (p. ex. fitxes CON), cap període vàlid — no corregeix automàticament: proporciona un **suggeriment «què + com»** (p. ex. «Desplaça US5 a un període ≥ 3, o US7 a un període ≤ 1, o verifica la relació»).

### 7.3 Vista prèvia i còpia de seguretat
- La **vista prèvia** mostra els canvis de període proposats abans d'aplicar-los.
- Abans d'escriure els períodes es realitza una **còpia de seguretat automàtica de la base de dades** (SQLite i PostgreSQL).
- Després d'aplicar, torna a llançar la verificació per comprovar eventuals paradoxes residuals.

---

## 8. Verificació de la cronologia (periodització i fitxes)

Al mateix panell **"Verifica rapporti"** (Verificar relacions — una pestanya del diàleg d'import/export de s3dgraphy), des de la versió 5.13.64-alpha la verificació també troba i corregeix problemes de **cronologia** del jaciment seleccionat. La verificació de paradoxes temporals (secció 7) compara el període d'una unitat amb l'estratigrafia; aquesta compara la periodització amb ella mateixa i amb les fitxes UE que la copien.

### 8.1 Què detecta

L'arbre del panell agrupa els problemes per tipus. Al costat dels grups de relacions apareixen quatre grups nous:

| Grup | Què assenyala | Com es tracta |
|------|---------------|---------------|
| **Fases amb intervals solapats** | Dues files de la periodització els intervals d'anys de les quals es creuen | Manual: el panell proposa escurçar els intervals només si, després d'escurçar-los, queda un interval utilitzable |
| **Datació de la fitxa desalineada** | El camp `datazione` de la fitxa UE diu una cosa diferent de la `datazione_estesa` del seu període/fase | Automàtic: la periodització és la font i la fitxa és la còpia, així que la còpia es reescriu des de la font. Un camp buit s'omple de la mateixa manera. Una UE sense període s'omet, perquè no hi ha res per copiar |
| **Periodització amb inici posterior a la fi** | `cron_iniziale` major que `cron_finale` | Manual: probablement són dates aC sense el signe menys — el panell proposa reescriure els dos anys en negatiu (`-1650` en lloc de `1650`); si en canvi és una errada, intercanvia els dos valors a mà |
| **Fase sense anys** | Una fase els anys de la qual falten o no es poden llegir | Només s'assenyala: no hi ha res de què heretar-los |

Un exemple per als solapaments. La base de dades d'exemple en té dos i cap no porta proposta: les dues fases tenen intervals **idèntics**, i qualsevol retall faria que una fase acabés abans de començar. El panell es limita a dir-ho; la decisió (fusionar les fases, corregir els anys, deixar-ho com està) correspon a l'arqueòleg.

### 8.2 Correcció automàtica i suggeriments

**Correccions automàtiques i propostes.** Les correccions automàtiques vénen **ja marcades**; les propostes **no**, i només s'apliquen si es marca la casella. Abans la regla era diferent: un problema la correcció del qual requeria una decisió humana només es podia llegir. Ara té una casella, que es deixa sense marcar. Això val també per a les dues categories antigues de relacions que ofereixen un suggeriment, és a dir, la contradicció directa i el cicle estratigràfic.

Per fer servir el panell:

1. Seleccioneu al panell el **jaciment** que voleu verificar. La verificació és **per jaciment**: mira només el jaciment triat i corregeix només aquell. En una base de dades amb deu jaciments això importa, perquè els mateixos números d'UE existeixen a tots.
2. Llegiu la **línia de resum** sobre l'arbre: indica quants problemes hi ha, quants són corregibles automàticament i **quantes són les propostes que cal marcar a mà**.
3. Obriu els grups i seleccioneu un problema per llegir-ne el detall al panell de previsualització.
4. Reviseu les caselles. Les correccions automàtiques ja estan marcades: desmarqueu les que no volgueu aplicar. Marqueu les propostes amb què estigueu d'acord.
5. Apliqueu les correccions. Abans d'escriure res es crea una **còpia de seguretat automàtica** (còpia del fitxer SQLite, o `pg_dump` per a PostgreSQL a `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); la còpia, que ja existia per a les correccions dels camps de període, ara cobreix també les cronològiques.
6. Si el resultat no convenç, premeu **Annulla ultimo fix** (desfer l'última correcció): desfer reverteix també les correccions escrites a la taula de periodització.

### 8.3 Vista prèvia i còpia de seguretat

**La previsualització mostra la data calculada.** Per a cada unitat citada per un problema, el panell de previsualització mostra la seva data calculada en una línia com aquesta:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

La línia indica, per ordre, l'interval d'anys, la regla que l'ha produït i la relació al llarg de la qual ha viatjat la restricció, juntament amb el node del qual procedeix. Quan els dos extrems de l'interval arriben per camins diferents, cada extrem porta la seva etiqueta (`inizio …` i `fine …`), de manera que una data mai s'atribueix a la relació equivocada. Avui, en una base de dades normal, cada unitat pren les dates del seu propi període, així que la majoria de línies diran `epoca`. El sentit de la línia no és sorprendre, sinó permetre veure **d'on ve** una data.

---

## 9. Com es llegeixen els arcs de la matriu

Algunes decisions del dibuix de la matriu poden semblar estranyes, però no són errors:

- **Una fletxa no passa mai per sota d'un node.** Quan la columna d'arribada està ocupada, la fletxa entra a la casella **pel costat**: és normal.
- **La igualtat no és una superposició.** Una relació «Uguale a» (Igual a) o «Si lega a» (Es lliga a) posa les dues unitats a la **mateixa fila**, l'una al costat de l'altra, unides per **dues línies horitzontals** (el signe igual) **sense punta de fletxa**.
- **Els arcs redundants no es dibuixen.** Si la US 1 cobreix la 2 i la 2 cobreix la 3, la fletxa d'1 a 3 no apareix, perquè no afegeix res. Dins d'un **cicle**, en canvi, tots els arcs es queden, perquè un cicle és un error que cal veure.
- **Les línies diuen quina relació són.** Grisa i contínua: la seqüència (cobreix, omple, es recolza). **Puntejada verda**: un tall (`Taglia` / `Tagliato da`), sigui quina sigui la definició estratigràfica i en qualsevol llengua. **Gruixuda i negra**: la continuïtat —un rombe petit i negre sense nom (el nom apareix en passar-hi el ratolí), a la columna de la seva unitat, així la línia és recta. **Vermella**: una fletxa que puja per les bandes, és a dir, una contradicció entre estratigrafia i cronologia; un tall que puja és vermell **i** continua puntejat.
- **Les paradades no són mai una línia contínua.** Prenen color i traç de les regles de l'Extended Matrix (`em_visual_rules.json`): bru-vermell puntejat «extret de», taronja discontinu «procedència de la dada», or discontinu «propietat», gris discontinu «connexió genèrica», vermell tomàquet discontinu «combina» (al fitxer seria continu: és l'única excepció, perquè un arc cap a un document no ha de semblar una superposició).
- **La vora bruna és una obra de maçoneria.** Les USM —WSU, MSE, UEM, USZ, ΤΣΜ en les altres llengües— tenen la mateixa casella que les US, amb la vora bruna en lloc de vermella.

---

## 10. Narrativa amb la IA

A partir de la versió **5.13.106-alpha**, el panell de la matriu dins del QGIS (§2.2, «Vedi la matrice») té dues pestanyes a la columna de la dreta: **Units** (*Unità*) —els detalls de la unitat triada, el zoom sobre la geometria i els mèdia, com abans— i **Narrative** (*Narrativa*), que és nova. La pestanya **Narrative** fa que una IA escrigui la **història del lloc**, un capítol per època, i després et permet llegir-la, fer-la validar per una persona i exportar-la a HTML, DOCX o PDF. Llegeix i escriu **el mateix em.json** que obre EMStudio, en el format de la biblioteca s3dgraphy: la narrativa que veus aquí és la que EMStudio mostra a la seva pestanya *Narrative*.

> **Cap configuració nova.** La pestanya no té cap finestra de configuració pròpia: fa servir la IA que ja has configurat en una altra part de pyArchInit (§10.2).

> **La IA escriu esborranys, no textos definitius.** Cada paràgraf escrit pel model es manté com a «AI draft» (esborrany d'IA) fins que una persona el valida (§10.6), i als documents exportats porta la marca ⚠.

Els noms de les pestanyes i dels botons de la pestanya **Narrative** existeixen en italià i en anglès: **són en italià si el QGIS és en italià, i en anglès amb qualsevol altra llengua**. Aquí es donen sempre tots dos. En canvi, les entrades de menú i les finestres de diàleg del connector (com «Vedi la matrice…» o els tres botons del §10.9) són només en italià; la traducció al català es dona entre parèntesis.

### 10.1 Obrir la pestanya Narrative

1. Obre el menú **Plugins → pyArchInit - Archaeological GIS Tools** i tria l'entrada **Extended Matrix → Vedi la matrice…** (Mostra la matriu).
2. Tria el **lloc**.
3. pyArchInit exporta el lloc de la base de dades a `<home>/pyarchinit_EM_folder/<lloc>.em.json` —`<home>` és `~/pyarchinit_5`, o la carpeta indicada per la variable d'entorn `PYARCHINIT_HOME`— i obre el panell **«Matrice — `<lloc>`»**, ancorat a la dreta de la finestra del QGIS. El nom del fitxer és el del lloc, amb els caràcters especials substituïts per «_» (per exemple, «Scavo 1» passa a ser `Scavo_1.em.json`).
4. A la columna de la dreta del panell, clica la pestanya **Narrative**.

<!-- IMMAGINE: Captura de pantalla del menú Plugins → pyArchInit - Archaeological GIS Tools amb l'entrada «Extended Matrix → Vedi la matrice…» -->
![Menú Mostra la matriu](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: L'entrada «Extended Matrix → Vedi la matrice…» al menú del connector*

<!-- IMMAGINE: Captura de pantalla del panell de la matriu ancorat a la dreta, amb les pestanyes Units i Narrative -->
![Panell amb dues pestanyes](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 2: El panell de la matriu amb les pestanyes Units i Narrative*

El fitxer és **un per lloc i resta al disc**: ja no viu en una carpeta temporal. És el fitxer que obre EMStudio i és on s'escriu la narrativa. Cada vegada que tries «Vedi la matrice…», el lloc **s'exporta de nou de la base de dades** i el fitxer es torna a escriure; la narrativa que ja hi havia es conserva (§10.8).

També pots arribar a la pestanya des de dos altres punts:

- des de l'entrada **Extended Matrix → Esporta sito in em.json…** (Exporta el lloc a em.json), que al final ofereix el botó «Narrativa con l'AI» (§10.9);
- des del botó **Vedi la matrice** de la finestra «Esporta Extended Matrix» de la fitxa US (§2.2): obre el mateix panell sobre el fitxer que acabes d'exportar, a la carpeta que has triat.

### 10.2 Quina IA es fa servir

A dalt de tot de la pestanya **Narrative**, una línia diu quina IA farà servir: **«Model: `<model>` (`<where it comes from>`)»**, seguida del recordatori sobre EMStudio. Si no en troba cap, diu **«No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”.»** (cap IA configurada: configura-la a la fitxa US → informe d'IA, o a la consulta d'IA de la base de dades) i els botons **Generate with AI** (Genera amb IA) i **Regenerate chapter** (Regenera el capítol) queden desactivats.

La pestanya llegeix la configuració d'IA **ja desada** per les altres finestres de pyArchInit, per aquest ordre, i fa servir la **primera** que té un model i —per als proveïdors en línia— la clau API:

| # | On es configura | Com l'anomena la pestanya (en / it) |
|---|-----------------|--------------------------------------|
| 1 | Fitxa US, botó «Report» → finestra «Generatore di Report» (generador d'informes), grup «Provider AI» | Report generator of the US form / Generatore di Report della scheda US |
| 2 | Fitxa US, botó «Query AI Database» | Query AI Database / Query AI Database |
| 3 | Finestra palimpsestr, botó «Report AI (analisi descrittiva)…», selector «Provider AI» | Palimpsest report / Relazione Palimpsest |
| 4 | Finestra «Generazione SQL con AI» (text a SQL: vegeu el tutorial 30) | Text to SQL / Testo in SQL |

Els proveïdors són els dels selectors «Provider AI» (proveïdor d'IA): **OpenAI** i **Anthropic (Claude)** en línia, amb la clau API que s'escriu al camp «API key» (clau API); **Ollama** i **LM Studio** al teu ordinador, sense clau. El selector desa l'elecció tan bon punt la canvies. Si vols un altre model, canvia'l a la finestra que la pestanya indica entre parèntesis (o a una que vingui abans a la llista). La pestanya torna a llegir la configuració **quan s'obre el panell**: després de canviar-la, torna a obrir la matriu.

### 10.3 La pestanya Narrative

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Show on the map]  [Export…]  [Open in EMStudio]  [Cancel]* │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* La línia de progrés i el botó «Cancel» (Cancel·la) només es veuen mentre la IA està escrivint. En aquest diagrama les files de la llista són les del lloc d'exemple.

<!-- IMMAGINE: Captura de pantalla de la pestanya Narrative amb la llista de capítols, el text del capítol triat i els set botons -->
![Pestanya Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 3: La pestanya Narrative*

De dalt a baix:

- **la línia d'estat**: el model en ús (§10.2) i el recordatori *«If EMStudio has the file open, close it first: the last writer wins.»* (si EMStudio té el fitxer obert, tanca'l abans: guanya qui escriu l'últim);
- **la llista de capítols**, una fila per capítol: *Títol — estat*. Un fitxer d'una versió anterior, dividit per sondeigs, mostra tots els grafs: cada fila va precedida del nom del graf entre claudàtors, per exemple `[Saggio A] 15th century — AI draft`;
- **el text del capítol triat**: la prosa, amb les unitats citades pel nom; els noms són **enllaços**: un clic mostra la unitat al mapa (§10.10); sota el paràgraf en què una unitat es nomena per primera vegada apareixen fins a dues fotos seves (§10.11). Si el capítol encara no té prosa, hi veus el seu marcador de posició «[to be written: …]»;
- **la línia de progrés**, només durant la generació: «Chapter 3 of 9 · 15th century»;
- **els botons**, en dues files.

El resultat de cada operació apareix a la barra de missatges del QGIS, amb el títol «Narrative».

Quan el fitxer **encara no té narrativa**, la llista és buida i un text diu: *«No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.»* (no hi ha cap narrativa al fitxer: «Prepare the chapters» crea l'esquema —N capítols entre èpoques i activitats—, «Generate with AI» l'escriu).

#### Els estats d'un capítol

| Estat (en / it) | Què vol dir |
|-----------------|-------------|
| **to be written** / da scrivere | El capítol només té el marcador de posició «[to be written: …]». |
| **AI draft** / bozza AI | Hi ha prosa escrita pel model que cap persona ha validat. N'hi ha prou amb un paràgraf: si el capítol en té tan sols un de no validat, aquest és el seu estat, encara que hi hagi altra prosa. |
| **endorsed** / convalidato | Tota la prosa de la IA ha estat validada per una persona. |
| **written** / scritto | Prosa escrita per una persona (a EMStudio). |
| **truncated** / troncato | S'afegeix a l'estat (per exemple, «AI draft, truncated»): el model s'ha aturat perquè ha arribat al límit de longitud, i el text queda tallat a la meitat. |

#### Els botons

| Botó (en) | En italià | Què fa |
|-----------|-----------|--------|
| **Generate with AI** | Genera con l'AI | Escriu, **un per un**, tots els capítols que encara són «to be written» —primer la **Presentation**, després els d'època (i d'activitat)—; els que ja estan escrits no es toquen. Si encara no hi ha narrativa, crea primer l'esquema. Mostra el progrés i el botó **Cancel**. Activat només amb un fitxer obert i una IA configurada. |
| **Regenerate chapter** | Rigenera capitolo | Reescriu **el capítol triat** a la llista: l'esborrany d'IA no validat es substitueix —però només quan el model ha respost: si la crida falla, l'esborrany d'abans es queda— i els blocs ja validats es conserven. S'activa quan tries la Presentation o un capítol d'època o d'activitat i hi ha una IA configurada; per a «Where it is» continua desactivat. |
| **Endorse…** | Convalida… | Obre un menú amb «This chapter» i «All chapters» (aquest capítol, tots els capítols) i després pregunta qui valida (§10.6). Activat quan hi ha una narrativa. |
| **Prepare the chapters** | Prepara i capitoli | Crea **només l'esquema** dels capítols, sense IA: funciona encara que no hi hagi cap IA configurada, perquè puguis escriure a mà a EMStudio. No toca la prosa ja escrita i afegeix els capítols de les èpoques noves. Resultat: «Chapters prepared: N.» |
| **Show on the map** | Mostra sulla mappa | Selecciona i enquadra al mapa, **totes alhora**, les unitats de què parla el capítol triat (§10.10): les citades a la prosa o, si el capítol encara no està escrit, totes les de la seva banda. Activat només si almenys una de les unitats de què parla el capítol triat és una fila de la fitxa US. |
| **Export…** | Esporta… | Desa la narrativa en HTML (amb el mapa interactiu del lloc, §10.7), DOCX o PDF imprimible (§10.7), amb les fotos de les unitats citades quan n'hi ha (§10.11). Activat quan hi ha una narrativa. |
| **Open in EMStudio** | Apri in EMStudio | Obre l'em.json a EMStudio. Si EMStudio no hi és, la barra de missatges indica l'entrada de menú **Extended Matrix → Installa EMStudio…** (Instal·la EMStudio). |
| **Cancel** | Annulla | Només apareix durant la generació: la IA s'atura **després del capítol en curs** i el que s'ha escrit es desa. |

Durant la generació tots els botons estan desactivats excepte **Cancel**.

### 10.4 Què escriu la IA

**Quins capítols.** L'esquema és el de la biblioteca s3dgraphy (la plantilla «site_story»):

- Des de la **5.13.110-alpha**, la **Presentation** (Presentació) és un capítol canònic que la IA escriu com els altres, a partir d'un dossier del lloc sencer (vegeu «El dossier de la Presentation» més avall); abans es quedava com a marcador de posició. **Where it is** (On es troba) és l'altre capítol canònic i es queda com a marcador de posició «[to be written: …]» per escriure a mà a EMStudio: neix de la posició del lloc i la biblioteca hi posa el mapa. Només existeix si el graf porta una posició geogràfica. La IA no el genera.
- **Un capítol per època** (període/fase) que té unitats, de la més antiga a la més recent. El títol és el nom de l'època, és a dir, la «Datazione estesa» (datació estesa) de la periodització; si falta, en surt un nom genèric com «Period 8 Phase 1»: omple-la a la fitxa Periodització per tenir títols llegibles. Una unitat apareix al capítol de l'època en què neix i als de les èpoques en què sobreviu.
- **Un capítol per activitat**, si el graf conté grups d'activitats. Un lloc exportat de la base de dades normalment no en té cap —el camp Activitat de la fitxa US viatja com a propietat de la unitat— i aleshores els capítols són els d'època.

**Què rep el model.** Per a cada capítol d'època o d'activitat, un *dossier* amb, per a cada unitat: nom, tipus i descripció; els camps emplenats de la fitxa US (definició estratigràfica i interpretativa, interpretació, període i fase, datació, activitat, estructura, sondeig, ambient, sector, àrea); les èpoques; **les relacions estratigràfiques** amb les altres unitats (cobreix, talla, omple, es recolza, igual a…) amb els seus noms; i, si n'hi ha, les fonts documentals vinculades. Les unitats s'enumeren **de la més antiga a la més recent**, seguint les relacions. Per sobre de **80 unitats** per capítol, el dossier es talla a les 80 primeres. A més, té un límit de longitud (uns 25.000 caràcters): per sobre, s'abreugen els textos llargs de les fitxes, es treuen les relacions repetides i les cadenes de proves i, si encara no n'hi ha prou, s'ometen les unitats més recents. En tots dos casos, s'informa el model de quantes unitats falten.

**Les regles.** El model rep les cinc regles de la biblioteca: escriure només el que el context sosté (cap data, material, funció ni esdeveniment inventat); mantenir la incertesa (una unitat virtual és una hipòtesi, no un fet); no citar fonts que no hi són; escriure prosa contínua, sense llistes ni títols; dir obertament quan el context és massa pobre. Demana d'un a tres paràgrafs.

**El dossier de la Presentation.** La Presentation no té unitats pròpies: el model rep un dossier del **lloc sencer**, pres del graf i no de la base de dades, amb el nom del lloc; la cadena de topònims (país → regió → província → municipi); els llocs de la fitxa US (àrees, sectors, sondeigs, ambients); les èpoques de la més antiga a la més recent, cadascuna amb quantes unitats hi són presents (una mateixa unitat pot ser en diverses èpoques, de manera que la suma pot superar el total); quantes unitats hi ha i de quin tipus, i quantes relacions estratigràfiques; els documents; les persones anomenades a les fitxes US; i els títols dels capítols de la història. Les seves instruccions són les de la Presentation, no les cinc regles de dalt: demanen de dos a quatre paràgrafs que diguin què és el lloc i on és, quines èpoques cobreix la història, com es llegeix aquesta història (un capítol per època i per activitat, amb les unitats citades pel nom i els esborranys marcats com a tals fins que una persona els validi) i en quines fonts es basa; que faci servir només el dossier, sense inventar dates ni fets, i que deixi fora una dada que sembli estranya en lloc de comentar-la. La prosa va **al principi** del capítol; les fitxes de les fonts (els documents) queden després, i els marcadors de posició «[to be written: a presentation of …]» i «[to be written: how this account is to be read…]» desapareixen.

**La llengua.** La prosa està escrita en la **llengua de la narrativa**, que es fixa quan es crea l'esquema per primera vegada: **italià si en aquell moment el QGIS és en italià, anglès amb qualsevol altra llengua** (el model rep les instruccions només en aquestes dues llengües). Una narrativa que ja existeix conserva la seva llengua encara que després canviïs la del QGIS. El mateix val per als títols dels capítols canònics i per als marcadors de posició.

**Com es desa.** En el format de la biblioteca, el mateix que llegeix EMStudio: un node de narrativa (`NarrativeNode`) que conté els capítols; cada paràgraf escrit pel model és un bloc «AI draft» atribuït a l'**autor d'IA** d'aquell model; el **prompt** utilitzat es registra com a extractor vinculat a les fonts, de manera que es pot saber què es va demanar. Les unitats citades al text són **mencions** (`[[name]]`): al fitxer continuen lligades al node de la unitat, i a la pestanya i a les exportacions apareixen amb el seu nom. Una menció que no correspon a cap unitat del graf es redueix a simples paraules, sense claudàtors.

**Costos i temps.** Es fa una crida al model **una vegada per capítol**, Presentation inclosa. Amb un proveïdor en línia cada crida té un cost i un temps d'espera (en les proves amb un model en línia, unes quantes desenes de segons per capítol: un lloc amb una desena d'èpoques triga uns quants minuts); amb Ollama o LM Studio no es paga res, però els temps depenen del teu ordinador.

### 10.5 Pas a pas

1. Obre la matriu del lloc (§10.1) i clica la pestanya **Narrative**. Comprova a dalt **quin model** farà servir.
2. **Tanca EMStudio** si té el fitxer obert: pyArchInit i EMStudio escriuen el mateix fitxer, i guanya qui escriu l'últim.
3. Opcional: **Prepare the chapters** (Prepara els capítols) per veure l'esquema, sense IA.
4. Clica **Generate with AI**. Segueix el progrés: la Presentation, si encara és «to be written», va primer («Chapter 1 of 9 · Presentation»), després els capítols d'època («Chapter 3 of 9 · …»); pots continuar fent servir el QGIS. Al final la barra de missatges diu, per exemple, *«7 chapters generated, 1 failed: Modern age — …»* (amb *«(cancelled)»* si has cancel·lat) i la llista es torna a carregar: els capítols escrits són «AI draft».
5. **Llegeix**: tria un capítol darrere l'altre i llegeix el text sota la llista. Comprova'l amb l'estratigrafia: és un esborrany construït a partir de les dades de la fitxa US. Per veure on són les unitats de què parla, clica els seus noms o fes servir **Show on the map** (Mostra al mapa; §10.10).
6. Si un capítol no et convenç, tria la seva fila i clica **Regenerate chapter**. El nou esborrany **substitueix** l'anterior no validat: si vols conservar la versió d'abans, exporta-la primer. Si un capítol és «truncated», regenera'l **abans** de validar-lo.
7. Quan un capítol està bé, clica **Endorse…** (§10.6).
8. Clica **Export…** per exportar a HTML, DOCX o PDF (§10.7), o **Open in EMStudio** per escriure a mà «Where it is» i polir la resta.
9. Més endavant pots tornar a obrir la matriu: la narrativa es conserva (§10.8).

<!-- IMMAGINE: Captura de pantalla de la generació en curs: la línia de progrés «Chapter 3 of 9 · …» i el botó Cancel -->
![Generació en curs](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 4: Generació en curs, amb la línia de progrés i el botó Cancel*

Un capítol que falla no atura els altres: el resum diu quins. Per tornar-ho a provar, només cal clicar de nou **Generate with AI**, que escriu només els capítols que encara són «to be written».

### 10.6 Validar: qui signa

Validar vol dir que una **persona** es fa responsable del text escrit pel model. No passa mai per si sol: ni en generar, ni en desar.

1. Clica **Endorse…**. S'obre un petit menú: **«This chapter»** (aquest capítol) —activat només si el capítol triat és un «AI draft»— o **«All chapters»** (tots els capítols), és a dir, tots els esborranys d'IA que encara no s'han validat, a tots els grafs del fitxer. La Presentation es valida com qualsevol altre capítol: tria-la a la llista i «This chapter» la valida ella sola.
2. Una finestra pregunta **«Who endorses? Pick an author or type a new name.»** (qui valida? Tria un autor o escriu un nom nou). La llista conté els **autors humans que ja són al graf** —les persones esmentades a la fitxa US com a compilador (*schedatore*), director US i responsable US— i pots escriure un nom nou, que passa a ser un autor nou del graf.
3. La barra de missatges diu **«N blocks endorsed by `<name>`.»** (N blocs validats per la persona triada), o «Nothing to endorse.» (no hi ha res per validar). El fitxer es desa.

<!-- IMMAGINE: Captura de pantalla del menú Endorse… («This chapter» / «All chapters») i de la finestra per triar l'autor -->
![Valida](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 5: Validar: el menú i l'elecció de l'autor*

Els blocs passen de «AI draft» a «endorsed». Al document exportat la persona apareix entre els responsables («a cura di», a cura de) i el model com a assistent («con l'assistenza di», amb l'assistència de), i els paràgrafs validats ja no porten la marca ⚠. Regenerar no esborra els blocs validats: una signatura és un acte, i no es perd en reescriure.

### 10.7 Exportar a HTML, DOCX o PDF

Clica **Export…**: s'obre la finestra de desament amb tres formats: «HTML page» (pàgina HTML; `.html`), «Word document» (document Word; `.docx`) i «Printable PDF» (PDF imprimible; `.pdf`). El nom proposat és `<lloc>_narrativa`, sense extensió, a la carpeta de l'em.json: l'extensió l'hi posa el format triat al filtre de la finestra; una extensió escrita a mà (`.html`, `.docx` o `.pdf`) preval sobre el filtre. La barra de missatges ho confirma: «Narrative exported to `<path>`» (narrativa exportada a la ruta del fitxer).

El document conté:

- el títol de la narrativa (per exemple, «Scavo archeologico — the story of the site»), els responsables («a cura di») i el model com a assistent («con l'assistenza di»);
- per a cada capítol, primer la prosa, amb les unitats citades pel seu nom, i després la llista de les unitats del capítol; per a les unitats citades que tenen fotos, una tira de fotos ocupa el lloc de la seva línia (§10.11);
- **el mapa del lloc** (des de la 5.13.115-alpha, només a l'HTML), en un requadre fix: a la dreta en les pantalles amples, a dalt al telèfon. Amb el mapa la pàgina s'eixampla (des de la 5.13.116-alpha) i el text manté una columna llegible. En repòs mostra totes les unitats del graf en gris clar; un clic al nom d'una unitat dins del text mostra **només les unitats del període d'aquell capítol** com a contorns amb el número a sobre, la unitat clicada **en color**, i enquadra el grup; un clic al títol d'un capítol fa el mateix, sense la unitat en color. La línia sota el mapa indica el període i quantes unitats; «whole site» (tot el lloc) torna a la vista completa. Les geometries provenen de les vistes US i USM de la base de dades del projecte en el moment de l'exportació (lloc del graf, unitats associades per àrea i número): una unitat citada però sense dibuix té l'enllaç i res al mapa; sense una base de dades connectada, el document no té mapa;
- al final, la secció **Fonti** (fonts): els documents en què es basa el relat i l'entrada «Prompt», que remet al prompt registrat al fitxer.

Coses que convé saber:

- **els esborranys no validats hi entren**, cadascun precedit de «⚠︎ non validato da una persona» (no validat per una persona), i la capçalera diu quants blocs hi ha en aquest estat. Per a un document sense marques, valida primer (§10.6). A l'HTML l'esborrany es llegeix com la resta del text, amb la mateixa tipografia i el mateix fons: damunt del paràgraf hi ha la línia d'avís i a l'esquerra un filet ambre. Al Word i al PDF l'avís va davant del paràgraf (al PDF, en una línia pròpia i sense el signe ⚠, §10.11);
- **hi entren tots els capítols**, fins i tot els que encara són «to be written»: el seu marcador de posició «[to be written: …]» es queda al text;
- la prosa va **al principi** del capítol, abans de la llista de les unitats; en una narrativa escrita amb una versió anterior pot ser encara al final, i es posa al seu lloc tornant a exportar el lloc (§10.8) o amb **Prepare the chapters** (Prepara els capítols);
- les figures que un autor ha previst a EMStudio (per exemple, la matriu d'una època) no les dibuixa l'exportació de pyArchInit: al document hi queda un marcador de posició;
- l'HTML és un sol fitxer, autosuficient (les fotos també hi van incorporades, i el mapa és un SVG dins del fitxer, sense biblioteques externes: s'obre també al telèfon sense xarxa); el DOCX s'obre amb Word o LibreOffice i requereix el paquet `python-docx`, i el PDF la biblioteca ReportLab (§10.11): tots dos són entre els requisits del connector.

<!-- IMMAGINE: Captura de pantalla del document HTML exportat: un capítol amb un esborrany precedit de «⚠︎ non validato da una persona» -->
![Document HTML exportat](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 6: El document HTML exportat, amb un esborrany no validat marcat*

### 10.8 Tornar a exportar el lloc: la narrativa es conserva

Tornar a exportar el lloc de la base de dades —amb **Vedi la matrice…**, amb **Esporta sito in em.json…** o amb la finestra «Esporta Extended Matrix» de la fitxa US— **conserva la narrativa** que ja hi ha al fitxer de destinació: prosa, validacions, autor d'IA i prompts. Les èpoques que han aparegut mentrestant reben un capítol «to be written». Un avís ho diu: **«Narrative kept from the previous file (N chapters).»** (narrativa conservada del fitxer anterior). El veus a la barra de missatges amb «Vedi la matrice…», al resum de la finestra «Esporta Extended Matrix» i, amb «Esporta sito in em.json…», als detalls de la finestra final.

Els **altres canvis** fets al fitxer des d'EMStudio —posicions dels nodes, descripcions reescrites— **no sobreviuen**, com abans: el fitxer es regenera a partir de la base de dades. Només es conserva la narrativa.

Abans de reescriure un fitxer que conté una narrativa, pyArchInit en fa una **còpia de seguretat** al costat: `<lloc>.em.json.bak` (cada nova exportació substitueix la còpia anterior).

Si el fitxer d'abans estava dividit per sondeigs (les versions fins a la 5.13.108-alpha podien exportar un graf per sondeig), a la primera reexportació el fitxer nou té **un sol graf** per a tot el lloc: els grafs tenen noms diferents i la narrativa **no pot passar** al fitxer nou. Un avís ho diu: *«The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …»*. El text no es perd: és a la còpia `.bak`, que, però, es substitueix en la propera exportació d'un fitxer que conté una narrativa —posa-la en lloc segur—. Si necessites la narrativa vella, obre aquesta còpia (reanomenant-la com a fitxer `.em.json` amb un altre nom); si no, torna a generar els capítols al fitxer nou (§10.5). Des de la 5.13.109-alpha el fitxer té sempre un sol graf i la narrativa passa d'una reexportació a la següent.

Si el fitxer anterior no es pot llegir (per exemple, un fitxer que ha quedat a mig escriure), l'exportació continua igualment: el fitxer il·legible es **reanomena** `<lloc>.em.json.broken` i un avís diu *«The previous file cannot be read (…): its narrative, if any, was not kept.»*

> **La narrativa no és a la base de dades de pyArchInit: viu només a l'em.json.** Una còpia de seguretat de la base de dades no la inclou. Copia de tant en tant la carpeta `pyarchinit_EM_folder`.

### 10.9 Des de l'entrada «Esporta sito in em.json…»

L'entrada **Extended Matrix → Esporta sito in em.json…** escriu el mateix fitxer `<lloc>.em.json` a `pyarchinit_EM_folder`. Al final mostra «Esportato `<path>`» (Exportat), amb els recomptes de nodes, arestes i avisos (el text dels avisos és als detalls de la finestra), i **tres botons**:

| Botó | Què fa |
|------|--------|
| **Apri in EMStudio** (Obre a EMStudio) | Obre el fitxer a EMStudio; si no està instal·lat, ofereix d'instal·lar-lo. |
| **Narrativa con l'AI** (Narrativa amb la IA) | Apareix **només si hi ha una IA configurada** (§10.2): obre el panell de la matriu ja a la pestanya **Narrative**. |
| **Chiudi** (Tanca) | Tanca la finestra. |

<!-- IMMAGINE: Captura de pantalla de la finestra final de «Esporta sito in em.json…» amb els tres botons -->
![Exporta el lloc a em.json: tres botons](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 7: La finestra final de «Esporta sito in em.json…»*

### 10.10 Les unitats al mapa

A partir de la versió **5.13.108-alpha**, la pestanya **Narrative** porta al **mapa del QGIS** les unitats de què parla un capítol, de dues maneres:

- **Una sola unitat: clica el seu nom.** Al text del capítol triat, els noms de les unitats citades són **enllaços**: un clic selecciona aquesta unitat a la capa US carregada i enquadra el mapa sobre ella, amb un parpelleig. No obre res.
- **Totes juntes: «Show on the map»** (*Mostra sulla mappa*; Mostra al mapa), a la segona fila de botons, entre «Prepare the chapters» (Prepara els capítols) i «Export…» (Exporta…). Selecciona i enquadra alhora totes les unitats de què parla el capítol triat: les citades a la prosa o, si la prosa no en cita cap (per exemple, perquè el capítol encara no està escrit), totes les unitats de la seva banda (l'època). La selecció és només una per capa —substitueix la que hi havia— i l'enquadrament abasta totes les geometries trobades, que parpellegen.

<!-- IMMAGINE: Captura de pantalla del QGIS amb les unitats del capítol seleccionades al mapa i, a dalt, la barra de missatges «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» -->
![Les unitats del capítol al mapa](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figura 8: Les unitats de què parla un capítol, seleccionades al mapa, i la barra de missatges*

Cal que una capa amb les geometries de les US ja estigui carregada al projecte, per exemple la **vista US** de pyArchInit: la pestanya la busca entre les capes carregades, com el botó «Zoom sulla geometria» (Zoom a la geometria) de la pestanya **Units** (tutorial 01), tot reconeixent les unitats pels camps `sito`, `area` i `us`. **El projecte no es modifica**: no s'afegeix cap capa, només canvien la selecció i l'enquadrament del mapa. Des de la **5.13.110-alpha**, si diverses capes porten els mateixos camps —com la vista US (polígons) i la vista de cotes (punts)—, la pestanya prova primer la geometria més plena: polígons, després línies, després punts; l'ordre de les capes a la llegenda només compta si tota la resta és igual. Val també per al botó «Zoom sulla geometria»: ja no cal posar la vista US al capdamunt de la llegenda.

La barra de missatges («Narrative») diu què s'ha trobat, per exemple «Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.» (5 de 6 unitats ressaltades a «US view», 7 geometries; no dibuixades: 1.US9). El nom entre cometes és el de la capa on s'han trobat les unitats, tal com apareix al tauler de capes del QGIS; una unitat pot tenir més d'una geometria, de manera que les geometries poden ser més que les unitats. Només es cerquen les unitats que són files de la fitxa US: un document o un node de continuïtat no té geometria i no entra al recompte. Si les unitats no dibuixades són més de cinc, els noms s'aturen a les cinc primeres, seguides de «…» i del total.

Un clic en un nom que no és una fila de la fitxa US no troba res, i la barra de missatges ho diu. Si cap capa carregada porta els camps per reconèixer les unitats, el missatge ho diu: carrega la vista US (§10.13).

### 10.11 Les fotos de les unitats i el PDF

A partir de la versió **5.13.108-alpha**, la narrativa mostra també les **fotos** de les unitats de què parla —al text de la pestanya i a les exportacions— i es pot desar a més com a **PDF imprimible**.

**Al text del capítol.** Sota el paràgraf en què una unitat es nomena per primera vegada apareixen **fins a dues miniatures** dels seus mèdia: són les mateixes de la pestanya Units, llegides de la carpeta de miniatures del projecte, i a sota, en lletra petita, hi ha el nom de la unitat i els noms dels mèdia. Si la unitat es torna a nomenar al mateix capítol, les fotos no es repeteixen.

**A les exportacions.** En els tres formats, per a cada unitat citada a la prosa que té imatges al disc, una **tira amb una o dues fotos una al costat de l'altra** ocupa el lloc de la línia de text de la unitat, amb el nom de la unitat com a peu de foto: s'usa la còpia reduïda si n'hi ha i, si no, la miniatura. Les unitats no citades a la prosa es queden com a línia de text. Les fotos van incorporades al fitxer: l'HTML i el DOCX els escriu la biblioteca s3dgraphy; el PDF, pyArchInit.

**El PDF imprimible.** És un document A4 que pyArchInit escriu amb ReportLab, amb la lletra Cambria com els altres PDF del connector (si el fitxer de la lletra no és a la carpeta `bin` de pyArchInit, fa servir Helvetica). Conté el títol, els responsables («edited by») i el model com a assistent («with the assistance of»); a dalt, si hi ha esborranys no validats, apareix també un avís amb el seu nombre; després tots els capítols, com en els altres formats, cadascun amb la seva prosa —les unitats citades escrites pel nom, i davant de cada paràgraf no validat una línia «non validato da una persona» (no validat per una persona), sense el signe ⚠— seguida de les fotos amb el seu peu i de les altres unitats en lletra petita; al final, les fonts. Al peu de pàgina hi ha «Generated by pyArchInit on …» (generat per pyArchInit el …) amb la data i el número de pàgina.

<!-- IMMAGINE: Captures de pantalla una al costat de l'altra: el text d'un capítol amb les miniatures sota la primera menció d'una unitat i una pàgina del PDF imprimible amb la tira de fotos i el peu -->
![Fotos de les unitats al text i al PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figura 9: Les fotos de les unitats al text del capítol i en una pàgina del PDF*

**Què cal.** Les fotos no són a l'em.json: es llegeixen de la base de dades i de les carpetes del projecte. Cal, doncs, la base de dades vinculada (la matriu oberta des del projecte), les rutes **Thumbnail path** i **Image resize** fixades a la configuració (tutorial 01) i els fitxers al disc; per al text n'hi ha prou amb la carpeta de miniatures. Les imatges en un magatzem remot no s'usen. Si falta alguna cosa no hi ha cap missatge: les fotos simplement no apareixen i l'exportació funciona igualment (§10.13).

### 10.12 Advertències

- **Tanca EMStudio abans de generar o validar.** Si EMStudio té el fitxer obert, guanya qui escriu l'últim.
- **Una IA escriu només a partir del que troba al graf, i es pot equivocar.** Les regles la frenen, no la fan infal·lible: llegeix cada capítol abans de validar-lo.
- **Amb un proveïdor en línia les dades surten de l'ordinador.** El dossier de cada capítol (noms, definicions, descripcions i relacions de les unitats) i el de la Presentation (nom del lloc, topònims, llocs, èpoques, documents i noms de les persones anomenades a les fitxes US) s'envien al servei triat; amb Ollama o LM Studio es queden en local.
- **El fitxer s'escriu al final.** La generació desa quan acaba, encara que l'hagis cancel·lada: no tanquis el QGIS mentre la IA està escrivint. El desament és segur: el fitxer s'escriu al costat, es torna a llegir i només aleshores substitueix el veritable; si alguna cosa va malament, **el fitxer anterior es queda tal com era**.
- **No tornis a obrir la matriu mentre la IA està escrivint.** La pestanya es queda al fitxer d'abans i avisa: *«Generation in progress: wait for it to finish, or press Cancel, before changing file.»* (generació en curs: espera que acabi, o prem Cancel, abans de canviar de fitxer).
- **El text s'edita a EMStudio**, no a pyArchInit.
- La narrativa i els nodes que la sostenen (autor d'IA, prompts) **no apareixen al dibuix de la matriu**.

### 10.13 Resolució de problemes

| Missatge (en / it) | Causa | Solució |
|--------------------|-------|---------|
| «No AI configured…» / «Nessuna AI impostata…» | Cap de les quatre finestres del §10.2 té un model (i, per a OpenAI i Anthropic, la clau API). | Configura el proveïdor i el model —i la clau— en una d'aquestes finestres i després **torna a obrir la matriu**: la pestanya només torna a llegir la configuració quan s'obre. Fins i tot sense IA pots preparar els capítols, validar, exportar i obrir EMStudio. |
| «No narrative in the file…» / «Nessuna narrativa nel file…» | El fitxer encara no té narrativa (és normal la primera vegada). | Clica **Prepare the chapters** (esquema) o **Generate with AI** (esquema i prosa). El nombre N compta els capítols d'època i d'activitat que tindrà l'esquema (una època sense unitats no en té cap); el missatge «Chapters prepared» també compta «Presentation» i, si hi és, «Where it is». «Generate with AI» escriu a més la «Presentation», que N no compta: el progrés compta un capítol més. |
| «EMStudio is not installed…» / «EMStudio non risulta installato…» | El programa no s'ha trobat a l'ordinador. | Fes servir l'entrada de menú **Extended Matrix → Installa EMStudio…** (té aquest nom amb qualsevol llengua del QGIS). |
| «truncated» / «troncato» al costat de l'estat | El model s'ha aturat al límit de longitud i el text queda tallat a la meitat. | Abans de validar, **Regenerate chapter**; si es repeteix, completa el capítol a EMStudio. |
| «N chapters generated, M failed: `<title>` — `<reason>`» / «N capitoli generati, M falliti: …» | El proveïdor ha rebutjat la petició (clau no vàlida, quota, model no disponible) o el servidor local no respon. «the model wrote nothing» vol dir que la resposta era buida. | Elimina la causa i clica de nou **Generate with AI**: escriu només els capítols que han quedat «to be written». |
| «The previous file cannot be read (…)» / «Il file precedente non si legge (…)» | En tornar a exportar, el fitxer existent no era un em.json que es pogués llegir. | L'exportació ha continuat: el fitxer il·legible s'ha conservat al costat del nou com a `….broken`, i la narrativa que contenia, si n'hi havia, no ha passat al fitxer nou. Si la necessites, recupera-la d'aquest fitxer o d'una còpia de seguretat. |
| «The previous file's narrative (graphs: …) did not travel into the new file…» / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | El fitxer d'abans estava dividit per sondeigs (versions fins a la 5.13.108-alpha): els grafs tenen noms diferents i la narrativa no pot passar. | El fitxer d'abans és a la còpia `.bak`: obre-la si necessites la narrativa vella, o torna a generar els capítols al fitxer nou. |
| «Could not write … The previous file is intact.» / «Non sono riuscito a scrivere … Il file precedente è intatto.» | El desament ha fallat (disc ple, fitxer bloquejat, permisos). | Soluciona-ho i repeteix: els capítols generats en aquella sessió no s'havien desat. |
| «DocX export needs python-docx — install the extra: …» (sempre en anglès) | El paquet `python-docx` no està instal·lat al Python del QGIS: només cal per al DOCX. | Instal·la `python-docx` (és un dels requisits del connector), o exporta a HTML, que no necessita res. |
| «None of the loaded layers has the fields to recognise the units…» / «Nessuno dei layer caricati porta i campi per riconoscere le unità…» | El projecte obert no té cap capa amb els camps `sito`, `area` i `us` de les unitats (per exemple, la vista US de pyArchInit): la pestanya només cerca entre les capes ja carregades. | **Carrega la vista US** de pyArchInit (o una capa amb els mateixos camps) al projecte i clica de nou el nom o **Show on the map** (Mostra al mapa). La pestanya no afegeix capes per si sola. Des de la 5.13.110-alpha no cal posar-la al capdamunt de la llegenda: amb els mateixos camps, la pestanya prova primer els polígons (§10.10). Carregada des de la fitxa US amb un estil triat (finestra «Style Choice», tutorial 14), la vista US porta també el número de la unitat dins d'un cercle. Des de la 5.13.111-alpha, la vista de cotes (punts), carregada des de la fitxa US, porta també la cota (dos decimals) sobre el símbol. L'estil i les etiquetes de la vista s'estableixen a la finestra «View styles» (entrada de menú «View styles…», tutorial 14); des de la 5.13.112-alpha, un estil per defecte desat allà mana en carregar. |
| Cap missatge: les fotos no apareixen al text del capítol ni a les exportacions | Les fotos es llegeixen de la base de dades del projecte i de les seves carpetes, i falta alguna cosa: la base de dades no està vinculada (la matriu s'ha obert sense), la ruta **Thumbnail path** no existeix en aquest ordinador o és un magatzem remot, els fitxers no són al disc, o la unitat no és una fila de la fitxa US o no té mèdia. | Mira la pestanya **Units**: si allà la unitat mostra les seves miniatures, les trobaràs també aquí. Si no, obre la matriu des del projecte, comprova **Thumbnail path** i **Image resize** a la configuració (tutorial 01) i que els fitxers siguin a l'ordinador: les imatges en un magatzem remot no hi entren. L'exportació funciona igualment, sense fotos. |

---

## Referències

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositori pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
