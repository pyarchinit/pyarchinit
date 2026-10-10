# Verifica cronologia dentro «Verifica rapporti» — design

> Brainstorming con Enzo, 2026-10-10. Nasce da: «mi piacerebbe importare in
> pyArchInit la questione delle correzioni cronologiche di cui parla Ema,
> presente in EMStudio».

## Che cosa si vuole ottenere

Che i problemi di cronologia di un sito si vedano **e si correggano** dentro
pyArchInit, senza passare da EMStudio — nella finestra dove l'archeologo già
controlla i rapporti.

Deciso con Enzo, in ordine:

1. **Direzione**: leggere **e correggere** le cronologie. La narrativa di
   EMStudio resta fuori da questa spec (sola lettura, spec separata).
2. **Chi decide la correzione**: automatica dove non c'è scelta, **proposta con
   anteprima** dove la scelta è dell'archeologo. È la stessa forma del dialogo
   «Verifica rapporti», quindi l'abitudine è già presa.
3. **Dove**: tutto **dentro «Verifica rapporti»**. Gli avvisi cronologici
   diventano altre categorie nell'albero che c'è già; la data calcolata compare
   nell'anteprima. Una finestra sola, nessuna scheda nuova.

Riuscito quando: sul sito di Enzo la verifica elenca le sovrapposizioni fra
fasi e le datazioni disallineate, le correzioni obbligate si applicano da sé,
quelle ambigue si propongono, e una seconda verifica non le ripresenta.

## Che cosa c'è oggi, misurato

Tutto quello che segue è misurato sul database di Enzo
(`~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite`, sito «Scavo
archeologico», 51 US), non dedotto.

**La periodizzazione ha davvero sovrapposizioni.** Due coppie di fasi portano
intervalli **identici**, e per giunta incrociati rispetto ai nomi:

| periodo.fase | anni | `datazione_estesa` |
|---|---|---|
| 2.2 | 1500–1549 | Prima metà del XVI secolo |
| **3.1** | **1500–1549** | Prima metà' del XV **secolo rec** |
| 2.3 | 1451–1499 | XV secolo |
| **2.2.1** | **1451–1499** | XV sec **rec** |

Sono gli stessi che EMStudio segnala come «*Prima metà del XVI secolo overlaps
Prima metà' del XV secolo rec by 49 years (1500–1549)*».

**`us_table.datazione` è una copia di `periodizzazione_table.datazione_estesa`
e ha derivato.** Su 51 US: **38 combaciano, 9 no, 4 vuote**. I 9 sono di tre
specie diverse:

| US | periodo.fase | nella scheda | attesa dalla periodizzazione | che cos'è |
|---|---|---|---|---|
| 31 | 3.1 | `Inizi XV seoclo` | `Inizi XV secolo` | refuso battuto a mano |
| 35 | 3.3 | `Seconda metà del XIV secolo` | `Seconda metà' del XIV secolo` | apostrofo che balla |
| 12 | 2.3 | `Prima metà del XV secolo` | `XV secolo` | scarto vero |

**Gli avvisi di EMStudio NON vengono dalla libreria.**
`graph.chronology(warnings=…)` sul sito emette **0 avvisi**. Quel controllo è
di EMStudio. In pyArchInit va **scritto**, non richiamato.

**La cronologia calcolata funziona ma oggi ripete la periodizzazione.**
`graph.chronology()` dà gli estremi a **45 nodi su 76**, e **tutti con regola
`epoch`**: `US 4 → 1500..1549, start=epoch(epoch_2_2 via has_first_epoch)`. Le
regole `tpq`/`taq`/`contained` non entrano mai in gioco perché scattano quando
un'unità **non** ha un periodo, e **le US senza periodo sono zero**. La regola
`written` non scatta perché nessuna US porta date assolute.

**Quello che c'è già e si riusa:**

- `modules/utility/rapporti_check.py` — `Issue(kind, us_path, auto, summary,
  edits)`, `Edit(us, add, remove, set_fields)`, `RapportiReport`,
  `kind_title(kind, lang)`, `apply_edits(edits, handle, sito=…)`,
  `rollback(token, handle)`. Le correzioni scrivono **solo** in `us_table`,
  colonne nella whitelist `_PERIOD_COL_WHITELIST`
  (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`).
- `modules/utility/temporal_check.py` — `build_chronology(handle, sito)` e
  `load_unit_periods(handle, sito)`, già chiamate dal dialogo.
- `gui/rapporti_check_dialog.py` — albero per categoria, spunte sulle
  automatiche, anteprima, applica, annulla, riverifica dopo l'applicazione.
- Le voci localizzate stanno in `_L`, con **sei lingue**: it, en, de, es, fr, pt.

## Fuori da questa spec, e perché

**Le date assolute su una US** (far scattare `written`/`tpq`/`taq`). Richiede
una correzione nel projector: oggi una riga `unita_tipo='property'` diventa
`PropertyNode(name='1.property800', value=None)` — il **nome** è l'etichetta e
il **valore non arriva**, quindi la regola `written` non potrebbe mai scattare.
Accantonata perché **non avrebbe niente da fare**: zero US con una data propria,
**una sola** riga `property` in tutto il sito, `elem_datanti` vuoto su 51 schede
su 51. E non costa niente riprenderla dopo, perché questa spec **non tocca il
projector**.

**La narrativa di EMStudio.** Sottosistema indipendente (`s3dgraphy.narrative`:
template, baking, citazioni, bozze AI con avallo umano). Spec separata.

## A — Gli avvisi cronologici

### Il modulo

Nuovo `modules/utility/chronology_check.py`, **puro**: niente QGIS, niente
widget. Prende le righe della periodizzazione e delle US e restituisce una
lista di `Issue` nella **stessa forma** di `rapporti_check`, così l'albero,
l'anteprima, l'applica e l'annulla non cambiano.

```python
def check_chronology(periods, units, *, sito, lang="it") -> list[Issue]
```

- `periods`: `[{periodo, fase, cron_iniziale, cron_finale, datazione_estesa}]`
- `units`: `[{us, periodo_iniziale, fase_iniziale, datazione, area,
  unita_tipo}]` — le ultime due non servono al giudizio ma a nominare la
  riga da correggere (vedi «Dove atterrano le correzioni»)

Entrambe lette dal chiamante con una funzione sola,
`load_chronology_rows(handle, sito)`, nello stesso modulo. Separare la lettura
dal giudizio è quello che rende il giudizio provabile senza database.

### Le quattro categorie

| kind | che cosa trova | auto | la correzione | istanze oggi |
|---|---|---|---|---|
| `epoch_overlap` | due fasi i cui intervalli si intersecano | no | **proposta**: restringe la più recente fino all'anno prima dell'altra | **2 per sito**, 20 in tutto |
| `datazione_mismatch` | `us_table.datazione` ≠ `datazione_estesa` della sua fase | **sì** | riscrive `datazione` dalla periodizzazione | **13** su «Scavo archeologico», 51 su ciascuno degli altri |
| `epoch_reversed` | `cron_iniziale > cron_finale` | no | **proposta**: riscrive i due anni **negativi** (date a.C. senza il segno meno) | **0** nel database di esempio, **non** nel Ventena |
| `epoch_no_dates` | fase senza anni | no | nessuna: si segnala | **0** — è una guardia |

**Perché `epoch_overlap` non è automatica.** Davanti a «1500–1549» due volte
non esiste una risposta giusta: chi si sposta lo sa solo chi ha scavato. La
proposta si mostra nell'anteprima e si applica solo se spuntata.

**Perché `epoch_reversed` non è automatica** (corretto il 2026-10-10,
dopo la revisione). La prima stesura la dava automatica e con lo scambio
dei due anni, sul presupposto «0 istanze, è una guardia» — misurato sul
**solo** database di esempio, e falso sul Ventena.
`modules/utility/periodization_checks.py` esiste dal 2026-08-27, ha lo
stesso predicato e dice l'opposto: `1650 → 1450` è «quasi sempre un
periodo a.C. battuto senza il segno meno», e il rimedio è **scrivere gli
anni negativi**. Scambiarli trasformerebbe l'Età del Bronzo Medio nel
1450–1650 d.C. — e renderebbe `inizio > fine` falso, zittendo l'avviso
del projector che gira nello stesso clic: la corruzione diventerebbe
invisibile. Quindi: `auto=False`, **una** proposta sola (i due anni
negati), e lo scambio nominato nel testo come la cosa da fare a mano
nella scheda Periodizzazione. Una proposta sola e non due perché il
dialogo applica la issue **intera**: due `Edit` nella stessa issue si
scriverebbero insieme, e una negazione mescolata a uno scambio non è
nessuna delle due. Quando un anno è già negativo il segno non manca, e
negare porterebbe il periodo nell'era sbagliata: lì la proposta è lo
scambio.

**Perché `datazione_mismatch` è automatica.** La periodizzazione è la fonte e
la scheda la copia: Enzo lo ha confermato («in US c'è il campo datazione che
legge dalla table periodizzazione a seconda del periodo e fase»). Riscrivere la
copia dalla fonte non ha alternative. Una US **senza** periodo non entra in
questa categoria: non c'è fonte da cui copiare.

**Ma la scala va guardata.** Sui nove siti tradotti del database di esempio la
periodizzazione è tradotta e la `datazione` nella scheda è rimasta in italiano:

```
US 4  p2 f2   scheda='Prima metà del XVI secolo'
              periodizzazione='First half of the 16th century'
```

Il disallineamento è vero e la correzione è giusta, ma sono **51 righe per
sito** (47 con un testo diverso più 4 con la `datazione` vuota, che è lo
stesso caso: la fonte c'è e la copia manca). Due conseguenze per il disegno:
il `summary` deve mostrare **tutti e due** i testi, perché l'anteprima è
l'unico punto in cui si vede cosa si sta per riscrivere; e la verifica resta
**per sito**, com'è oggi, così non si riscrivono mai dieci siti in un colpo.
La conferma con il conteggio («Applicare N correzioni?») e l'annulla restano
quelli di adesso.

**`epoch_no_dates` non è automatica, e non per prudenza**: in
`periodizzazione_table` **non esistono righe di solo periodo** — la `fase` non è
mai vuota, misurato su tutti i siti — quindi non c'è nessuna riga da cui
ereditare gli anni. Ereditarli dalle fasi sorelle sarebbe un'invenzione. Si
segnala e basta.

### Dove atterrano le correzioni

`epoch_reversed`, `epoch_no_dates` ed `epoch_overlap` scrivono in
**`periodizzazione_table`** (`cron_iniziale`, `cron_finale`), che la macchina
di oggi non tocca. `datazione_mismatch` scrive in `us_table.datazione`, che
oggi non è in whitelist.

La chiave di una riga di `us_table` è di **quattro** colonne —
`UniqueConstraint('sito', 'area', 'us', 'unita_tipo')` in
`modules/db/structures/US_table.py` — quindi `datazione_mismatch` porta
`target=("us_table", {"us": …, "area": …, "unita_tipo": …})`: con la sola
`us`, su uno scavo a più aree una correzione ne riscriverebbe tutte le
righe con quel numero (corretto il 2026-10-10, dopo la revisione). E
`apply_edits` **rifiuta** quando la clausola individua più di una riga,
per qualunque produttore di correzioni.

Dal 2026-10-10 lo fanno **tutti** i produttori, non solo
`datazione_mismatch`: la reciprocità, il self-loop e le due correzioni di
periodo dei paradossi temporali. Finché non lo facevano, su uno scavo a più
aree il rifiuto le colpiva tutte — «Apply fallito», e tutte le spunte dello
stesso clic perdute, perché il `raise` sta dentro `engine.begin()`.

`Issue` guadagna un campo facoltativo, `rows`: le chiavi di riga delle US di
`us_path`, allineate posizione per posizione, `None` dove la riga non si sa
nominare e **lista vuota** per chi non nomina righe — gli avvisi sulle fasi
di questa verifica, che non riguardano righe di `us_table`. Vuota vuol dire
«come prima»: la correzione tiene la chiave `us` e nient'altro.

**Il cambio di semantica, voluto.** Due righe numerate 1 in due aree erano
un'unità sola per la verifica dei rapporti, che indicizzava le schede per
numero di US; adesso sono due. «US 1 copre 9» scritto nell'area 1 cerca il
reciproco sulla US 9 **dell'area che il rapporto nomina**, non su una
qualunque riga numerata 9 — ed è quello che la tupla `[rapporto, us, area,
sito]` dice. Sullo scavo a due aree misurato il 2026-10-10 il
comportamento di prima era: il reciproco scritto nell'area 2 zittiva
l'avviso dell'area 1, e i rapporti dell'area 1 risultavano mancanti perché
a risponderne era la scheda dell'altra area.

La **forma corta** `['Coperto da', '1']` l'area non la dice, e vale quella
della scheda che l'ha scritta: è quello che il plugin stesso ci scrive
quando la espande (`US_USM.update_rapporti_col` gira area per area e appende
l'area in lavorazione). Ma la preferenza entra in gioco **solo** quando il
numero di US da solo nomina più di una riga: con un candidato solo la
lettura è quella di sempre, e questo è il caso di tutte e 510 le righe del
database di esempio — un'area, zero numeri ripetuti, e 1870 voci di
rapporti tutte in forma corta. Se l'area dichiarata non nomina nessuna riga
decide il numero: è un dato denormalizzato che il plugin riscrive da sé
(Ctrl+U) e può essere vecchio, e andare in silenzio sarebbe peggio che
leggerlo come un suggerimento. Se restano più righe — una US 9 e una USM 9
nella stessa area, che il vincolo permette e che una voce di `rapporti` non
sa distinguere, perché il tipo di unità non lo scrive mai — si segnala e non
si propone niente.

`Edit` guadagna un campo **con un valore di ripiego che conserva il
comportamento di adesso**:

```python
@dataclass(frozen=True)
class Edit:
    us: str
    add: tuple = ()
    remove: tuple = ()
    set_fields: tuple = ()
    target: tuple = ()      # ("us_table", {"us": "12"}) se vuoto
```

`target` dice **in quale tabella** e **con quale chiave**: per la
periodizzazione `("periodizzazione_table", {"periodo": "2", "fase": "2.2"})`.
Quando è vuoto vale `us_table` con la chiave `us`, cioè esattamente quello che
`apply_edits` fa oggi — nessuna chiamata esistente cambia.

`apply_edits` raggruppa per `(tabella, chiave)` invece che per `us`, e la
whitelist diventa **per tabella**:

```python
_WRITABLE = {
    "us_table": {"periodo_iniziale", "fase_iniziale", "periodo_finale",
                 "fase_finale", "datazione"},
    "periodizzazione_table": {"cron_iniziale", "cron_finale"},
}
```

Lo snapshot per l'annulla tiene già `(riga, valori originali)`: diventa
`((tabella, chiave), valori originali)` e `rollback` lo segue. **Nessuna
colonna nuova in nessuna tabella.**

### Dove si innesta nel dialogo

In `_run`, dopo `check_rapporti`, si aggiungono le issue di
`check_chronology`. L'albero le raggruppa da sé perché raggruppa per `kind`;
servono le quattro voci `t_epoch_reversed`, `t_epoch_no_dates`,
`t_epoch_overlap`, `t_datazione_mismatch` in `_L` per le **sei** lingue che il
dizionario già copre.

## B — La data calcolata, nell'anteprima

Quando si seleziona un problema, sotto il testo compare una riga per ogni US
nominata:

```
US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2
```

cioè gli estremi, **la regola** che li ha prodotti e **la provenienza** (l'arco
percorso e il nodo da cui il vincolo è arrivato), presi da
`graph.chronology()`. Niente colonne nuove, **niente scritture**: si ricalcola
a ogni verifica, e costa poco perché il grafo si sta già proiettando per
`check_rapporti`.

Una funzione pura in `chronology_check.py` formatta la riga:

```python
def explain_bounds(entry, *, lang="it") -> str
```

Così il testo è provabile senza grafo e senza finestra.

**Onestà su quello che dice oggi**: finché nessuna US porta date assolute,
tutte le righe diranno `epoca`, cioè ripeteranno la periodizzazione. Serve a
rendere visibile **da dove viene** una data — e quando diranno tutte la stessa
cosa, si vedrà da sé che manca la parte accantonata.

## Errori e casi limite

- **Periodizzazione assente o vuota** per il sito: nessuna issue, non è un
  errore. La verifica dei rapporti continua.
- **`epoch_reversed` ed `epoch_no_dates` non hanno istanze nel database di
  esempio** (zero righe con inizio > fine, zero righe senza anni, su tutti i
  siti), ma `epoch_reversed` ne ha nel **Ventena** — è il caso per cui
  `periodization_checks` è nato. I loro test nascono da righe costruite a
  mano, non dal database di esempio.
- **`fase` non numerica** (nei dati di Enzo ci sono `2.1`, `3.1`): la chiave è
  sempre **testo**, mai convertita a numero. Confrontare `2.1` come float
  perderebbe `2.10`.
- **Anni non interi o testo** in `cron_iniziale`: la riga si salta e si segnala
  come `epoch_no_dates`, non si solleva.
- **Due fasi con la stessa coppia (periodo, fase)**: non è compito di questa
  verifica — `periodizzazione_table` ha già un vincolo di unicità.
- **La correzione non trova la riga** (qualcuno l'ha cancellata nel frattempo):
  `apply_edits` aggiorna zero righe; la riverifica che segue ripresenta il
  problema, che è il comportamento giusto.
- Ogni correzione passa dallo stesso **annulla** di oggi.

## Prove

Il modulo è puro, quindi quasi tutto si prova senza QGIS e senza database.

**Rilevazione** (`tests/utility/test_chronology_check.py`), con righe
costruite a mano:
- due fasi con intervallo identico → un `epoch_overlap`, non due;
- intervalli che si sfiorano senza toccarsi (1499/1500) → nessuna issue;
- `cron_iniziale > cron_finale` → `epoch_reversed`, **non** automatica, la
  proposta dei due anni negativi (e lo scambio quando un anno è già
  negativo);
- fase senza anni → `epoch_no_dates`, segnalata e **non** automatica;
- `datazione` diversa → `datazione_mismatch` automatica con il valore atteso;
- `datazione` uguale, o US senza periodo → nessuna issue;
- `fase` `2.1` e `2.10` restano distinte.

**Scrittura** (`tests/utility/test_chronology_apply.py`), su SQLite di prova:
- una `Edit` con `target` sulla periodizzazione scrive lì e **non** in us_table;
- una `Edit` senza `target` scrive in `us_table` come prima (nessuna
  regressione sui rapporti);
- una colonna fuori whitelist non viene scritta;
- l'annulla riporta entrambe le tabelle allo stato di prima.

**Sul database vero** (`tests/utility/test_chronology_live.py`, sul database di
esempio): la verifica trova **2** sovrapposizioni e **13** datazioni
disallineate su «Scavo archeologico», e **51** su un sito tradotto, ognuna
con i due testi nel `summary`; applicando le automatiche, una seconda
verifica non le ripresenta. I numeri sono 13 e 51 e non 9 e 47 — che è
quanto diceva la prima stesura di questa spec — perché la categoria conta
anche le **4 schede per sito con la `datazione` vuota**: la fonte c'è e la
copia manca, che è lo stesso disallineamento (misurato il 2026-10-10; la
spec diceva 9 e 47 contando solo le righe con un testo diverso).

**L'anteprima**: `explain_bounds` su una voce di `chronology()` dà la riga
attesa, e su una voce senza estremi non solleva.

## Come si spedisce

Due tappe, ognuna utile da sola:

1. **A** — modulo, quattro categorie, `target` su `Edit`, whitelist per
   tabella, voci localizzate, innesto nel dialogo. Risolve i problemi che il
   sito ha oggi.
2. **B** — la riga nell'anteprima. Poche righe, dipende solo da A per il posto
   dove scriverla.
