# Narrativa: la scena 3D dei proxy — disegno

Data: 2026-10-17 · ramo `Stratigraph_00001` · plugin 5.13.131-alpha → 5.13.132-alpha · s3dgraphy dev57.

## Da dove viene

Enzo, 17 ottobre 2026: «assemblare insieme tutti i 3D come ad esempio per la mappa e quando nel capitolo si fa riferimento a quello se ci clicco sopra come le us ad esempio si evidenzia il proxy interessato e gli altri sono in trasparenza».

Oggi l'HTML della narrativa ha la mappa (i disegni delle viste US e USM, `em_narrative_map`: un clic sul nome di un'unità la evidenzia e mostra solo le unità del periodo del capitolo) e apre i modelli 3D uno alla volta, nel pannello delle fonti e dei media (`<model-viewer>`). Una scena che metta insieme le unità in 3D non c'è. E dove non ci sono disegni — TempluMare, importato da un em.json — non c'è la mappa, e i nomi delle unità nel testo non sono nemmeno link.

Misure su TempluMare v3.2 (le 65 copie dei proxy del database, solo lettura):

- 65 proxy GLB (Khronos glTF Blender I/O 5.2), 2,4 MB in tutto;
- ogni GLB ha un nodo con traslazione e rotazione nel sistema locale della scena (Y in alto, metri): messi insieme si incastrano, in un ingombro di 43,3 × 14,3 × 52,4 m;
- i materiali hanno i colori EM: US (0,33 · 0,03 · 0,03), USVn (0,03 · 0,19 · 0,03), USVs (0,02 · 0,28 · 0,80, α 0,4, BLEND), SF (0,69 · 0,51 · 0,03, α 0,4), VSF (0,44 · 0,35 · 0,12), un NEUTRO bianco; 31 proxy hanno lo stesso materiale «USVn».

## Obiettivo

Nel pannello fisso dell'HTML della narrativa, accanto alla mappa, una scheda **3D** con tutti i proxy delle unità messi insieme. Una sola selezione vale per le due viste: il clic sul nome di un'unità nel testo evidenzia il suo proxy, rende trasparenti quelli del suo periodo e quasi invisibili gli altri, e inquadra; il clic sul titolo di un capitolo mostra il suo periodo; «tutto il sito» torna a tutto. Funziona offline: la libreria 3D è dentro la pagina.

## Non obiettivi

- Word e PDF: restano come sono.
- I modelli di rappresentazione delle epoche (`rm_instances`), il rilievo di `RB/`, le forme fatte solo di inviluppi o sfere senza file.
- Ricavare geometrie 2D dai 3D (Enzo: «No non ricavare le geometrie dai 3D»).
- Il visore del singolo modello nel pannello delle fonti e dei media (`<model-viewer>`): resta com'è.
- Trovare i proxy senza database (accanto a un em.json): dopo.
- Modificare qualcosa dalla scena: si guarda soltanto.

## Decisioni

1. **I proxy dalla libreria.** `s3dgraphy.paradata_view.proxy_instances(graph)`, la regola del datamodel che usa EMStudio (`threed_instances` di `em_visual_rules.json`): unità → `has_property` → proprietà `geometry` → `has_semantic_shape` → forma → `has_linked_resource` → risorsa `proxy_model`. Una proprietà ereditata (la USV che completa una US) si disegna una volta sola, dal proprietario originale (`ownership.original_owner`). Le istanze senza file si saltano.
2. **Unità ↔ proxy.** Il proprietario ha i suoi proxy (uno o più file); un'unità che ha la stessa proprietà `geometry` senza esserne la proprietaria punta al proxy del proprietario: il clic su di lei evidenzia quello.
3. **I file dal database**, con la regola dell'export del progetto EM (`em_project`): l'originale di `media_table` (prima quello il cui percorso finisce come il locator, poi quello col nome giusto), altrimenti la copia della cartella delle ridotte solo se ha la stessa estensione. Le due funzioni di `em_project` che lo fanno diventano pubbliche: `media_index(connection_url, resize_base)` e `media_file_for(locator, index)`.
4. **Limiti.** 15 MB per proxy, 40 MB in tutto; quelli che restano fuori si contano nella didascalia e si elencano nel suo suggerimento.
5. **Nomi ed epoche** come la mappa: `em_narrative_map.units_meta(graph)` per le unità che sono righe della scheda; per i proprietari di un proxy che non lo sono, il nome del nodo e le epoche di `epochs_of(graph)`. Così «per periodo» vuol dire la stessa cosa nelle due viste.
6. **I link anche senza mappa.** Le menzioni (`a.em-mention.pya-u` con `data-u` e `data-e`) e i titoli dei capitoli (`h2.pya-cap` con `data-e` e `data-units`) si fanno quando c'è almeno una delle due viste, non più solo con la mappa: la parte di `inject_map` che li fa si separa da quella del pannello della mappa.
7. **Un pannello, a schede.** Resta `<aside class="pya-map" id="pya-map">` (altri pezzi trovano lì la fine dei capitoli: `em_narrative_html._fine_dei_capitoli`). Con le due viste, in cima le schede **Mappa** e **3D**; con una sola, niente schede. La mappa si vede per prima quando ci sono tutte e due, e la scena 3D si crea la prima volta che si apre la sua scheda; quando c'è solo il 3D, la scena si crea all'apertura della pagina.
8. **Una selezione sola.** Un piccolo script comune tiene la selezione (epoca, unità) e la passa a ogni vista registrata: lo chiamano il clic su una menzione, sul titolo di un capitolo, su «tutto il sito» e sul proxy nella scena. La vista 3D, creata dopo, parte dalla selezione corrente. Un capitolo senza epoca (ancorato a un'attività, come i capitoli di TempluMare) seleziona come gruppo le unità del capitolo (`data-units`): la selezione è `(epoca, unità, gruppo)` (aggiunto con il piano, 17 ottobre 2026).
9. **Come si disegna.**
   - A riposo: tutti i proxy con i loro materiali, inquadrati tutti.
   - Un'unità: il suo proxy con il suo materiale, opaco, e un contorno arancione (#f5b942, lo stesso dell'evidenziazione della mappa) disegnato sopra; quelli dello stesso periodo con opacità 0,25; gli altri con opacità 0,04. Inquadratura sull'ingombro del proxy allargato tre volte, per avere intorno il contesto.
   - Un capitolo: i proxy del suo periodo con i loro materiali, opachi; gli altri a 0,04; inquadratura sul gruppo.
   - Un capitolo senza epoca: le sue unità con i loro materiali, opache; le altre a 0,04; inquadratura sul gruppo. La mappa, che lavora per epoca, torna a tutto il sito.
   - I materiali si clonano per proxy (31 proxy di TempluMare ne condividono uno), così ognuno ha la sua opacità; i trasparenti non scrivono la profondità.
   - Il passaggio da un'inquadratura all'altra dura 0,6 secondi.
10. **Nella scena.** Si gira col tasto sinistro o un dito, si ingrandisce con la rotella o due dita, si sposta col tasto destro o due dita (`OrbitControls`); passando sopra un proxy compare il nome della sua unità; un clic (non un trascinamento) su un proxy seleziona la sua unità, nell'epoca già selezionata se l'unità vi appartiene, altrimenti nella sua prima epoca.
11. **La didascalia** sotto la scena, come quella della mappa: «II A.D. · 23 proxy · SU004», oppure «Tutto il sito · 65 proxy»; per un'unità senza proxy «SU005: senza proxy 3D»; i proxy rimasti fuori o non caricati si contano. Accanto, il link «tutto il sito».
12. **three.js dentro la pagina.** Un solo file `resources/js/pya_three_scene.min.js`: three (la versione stabile più recente al momento della costruzione, fissata e scritta in testa al file e in `THREE_LICENSE.txt`; licenza MIT) con `GLTFLoader` e `OrbitControls`, impacchettato con esbuild in uno script classico che espone un oggetto globale; accanto `resources/js/THREE_LICENSE.txt`. Lo rifà `scripts/build_three_bundle.sh` (npm ed esbuild in una cartella temporanea, solo per chi sviluppa). La pagina lo porta una volta sola, e solo se ha una scena 3D. Il codice della scena — selezione, materiali, inquadrature, didascalia — è JavaScript scritto nel modulo Python, non nel pacchetto.
13. **I proxy nella pagina** in un blocco JSON (`<script type="application/json" id="pya-scena-3d-data">`; gli id della scena cominciano con `pya-scena-3d` perché `pya-3d` è del visore del singolo modello nel pannello delle fonti) con, per ogni proxy, l'unità e il GLB in base64; nel browser si decodificano e si leggono con `GLTFLoader.parse`.
14. **Lingua**: italiano e inglese, come la mappa.
15. **Correzione della 5.13.130.** Le regole CSS del blocco «Unità del capitolo» su `.pya-u` valgono solo dentro `.pya-unita`: oggi danno un bordo e un margine anche ai nomi delle unità nel testo, che sono link `a.pya-u` della mappa.

## Che cosa vede chi legge

A destra, sopra il pannello, le schede «Mappa» e «3D» (o solo una delle due). La scheda 3D mostra la scena con tutti i proxy nei colori EM e, sotto, «Tutto il sito · 65 proxy». Clic su «SU004» nel testo: la scena va su SU004, opaco e col contorno arancione, con intorno le unità dello stesso periodo trasparenti e le altre appena accennate; la didascalia dice «II A.D. · 23 proxy · SU004». Clic sul titolo del capitolo: le unità del periodo piene. Passando sopra un proxy se ne legge il nome; cliccandolo si seleziona, e la mappa, se c'è, lo segue. Sul telefono il pannello sta in alto, come la mappa.

## Errori e casi limite

- Nessun proxy o nessun database: niente scheda 3D; senza mappa e senza proxy la pagina è quella di oggi.
- Il browser non ha WebGL: nella scheda 3D la frase «Questo browser non mostra il 3D (WebGL).».
- Un GLB che non si legge: si salta; la didascalia conta i proxy non caricati.
- Un'unità citata che non ha proxy: la scena mostra il suo periodo e la didascalia dice «senza proxy 3D».
- Un proxy la cui unità non è citata da nessuna parte: c'è nella scena, si vede a riposo e nel suo periodo.
- Oltre i limiti: restano fuori i proxy più grandi; la didascalia lo dice.
- Pagina riaperta più volte: lo stato non si salva da nessuna parte; ogni apertura parte da «tutto il sito».

## Verifica

- **Test Python** (senza browser): i dati della scena da un grafo piccolo — proprietario, unità che eredita, forma senza file, file dal database e dalla copia delle ridotte, limiti; la pagina — solo mappa, solo 3D, tutte e due (schede), link senza mappa, dati JSON, il pacchetto three.js una volta sola, la correzione del CSS; i test della mappa di oggi passano senza cambiare.
- **Nel browser**: Chrome senza schermo (WebGL software) sull'HTML di TempluMare, con schermate a riposo, dopo il clic su un'unità e dopo il clic su un capitolo; i clic li fa una copia della pagina con uno script di prova, che non entra nel plugin.
- Suite completa verde.
- Tutorial 36 §10.7 in dieci lingue, changelog bilingue, 5.13.132-alpha.

## Fuori da questa release, da decidere dopo

- I modelli di rappresentazione delle epoche e il rilievo come contesto della scena.
- Le forme senza file (inviluppi, sfere).
- I proxy trovati senza database, partendo dal progetto dell'em.json.
- Un collegamento diretto a un'unità (`#…` nell'indirizzo).
- Usare la stessa scena three.js anche per il singolo modello, al posto di `<model-viewer>`.
