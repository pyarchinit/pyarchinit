"""Le immagini finte del database di esempio, disegnate al primo avvio.

Il database di esempio porta i **media** di tutte le schede che li
gestiscono — US, ceramica, reperti, tombe, strutture, UT — tre per record.
Le immagini però non si spediscono dentro il plugin: si **disegnano** la
prima volta, nelle due cartelle che pyArchInit usa per i media.

Perché disegnarle e non spedirle: sono 282 media, cioè 564 file (una
miniatura e una immagine ridimensionata per ciascuno). Spedirli vorrebbe
dire qualche megabyte di segnaposto dentro ogni aggiornamento del plugin,
e un nome di file sbagliato nel database renderebbe inutile metà del
pacchetto. Disegnarli costa un paio di secondi al primo avvio, e i nomi
li detta il database: `media_thumb_table.filepath` per la miniatura e
`path_resize` per l'immagine grande, esattamente come li scrive la scheda
quando l'archeologo trascina una foto.

**Le due cartelle.** pyArchInit tiene i media in due posti distinti,
configurati in `config.cfg`: `THUMB_PATH` (le miniature, 150×150, DPI
100) e `THUMB_RESIZE` (le immagini ridimensionate, DPI 300). Li legge
`Connection.thumb_path()` / `thumb_resize()`, e i nomi che il database
porta sono **nudi**: la scheda fa `thumb_path_str + filepath_thumb`, una
concatenazione — quindi il percorso configurato **deve finire col
separatore**, se no il file va a finire accanto alla cartella invece che
dentro.

Le misure sono quelle di `pyarchinit_media_utility`: 150×150 per la
miniatura, e per la grande un formato √2 come il 2008×1417 di
`Media_utility_resize`, rimpicciolito a mille pixel perché un segnaposto
non ha niente da mostrare a trecento DPI.

Niente di questo modulo tocca le immagini vere di nessuno: scrive solo i
file che il database di esempio nomina, e **salta quelli che già
esistono**.
"""
from __future__ import annotations

import os
import sqlite3
from functools import lru_cache

#: La miniatura, come la fa `Media_utility.resample_images`.
DIM_THUMB = (150, 150)
#: L'immagine ridimensionata. `Media_utility_resize` usa 2008×1417 a 300
#: DPI; per un segnaposto bastano ottocento pixel con le stesse
#: proporzioni (√2). La misura è scelta col cronometro: 606 file costano
#: 11,7 secondi a 1000×707 e 7,6 a 800×566, e la compressione non si può
#: spegnere (senza, un file passa da 15 KB a 1,3 MB).
DIM_RESIZE = (800, 566)

#: Un colore per tipo di scheda, così si vede a occhio da dove viene una
#: foto. Sono tinte spente: un segnaposto non deve sembrare una foto vera.
COLORI = {
    "US": (104, 124, 148),
    "CERAMICA": (150, 110, 94),
    "REPERTO": (126, 132, 104),
    "TOMBA": (118, 110, 130),
    "STRUTTURA": (136, 126, 102),
    "UT": (100, 130, 126),
    "DOC": (112, 116, 124),
}
#: Per un tipo che non conosciamo.
COLORE_IGNOTO = (120, 120, 120)



def media_da_disegnare(conn) -> list:
    """Le immagini che il database di esempio nomina.

    Una tupla per media: ``(nome_miniatura, nome_grande, etichetta,
    tipo)``. L'etichetta è la descrizione che la scheda mostra — è lei
    che finisce disegnata dentro l'immagine — e il tipo decide il colore.

    Si leggono da `media_thumb_table` perché è lì che stanno i **nomi dei
    file**; la descrizione e il tipo vengono da `media_table` e
    `media_to_entity_table`.
    """
    righe = conn.execute(
        "SELECT t.filepath, t.path_resize, m.descrizione, m.filename,"
        "       (SELECT e.entity_type FROM media_to_entity_table e"
        "        WHERE e.id_media = t.id_media LIMIT 1)"
        "  FROM media_thumb_table t"
        "  JOIN media_table m ON m.id_media = t.id_media"
        " ORDER BY t.id_media_thumb").fetchall()
    fuori = []
    for thumb, grande, descrizione, nome, tipo in righe:
        if not thumb or not grande:
            continue
        fuori.append((str(thumb), str(grande),
                      str(descrizione or nome or thumb),
                      str(tipo or "")))
    return fuori


@lru_cache(maxsize=8)
def _font_grande(dimensione: int):
    """Un font leggibile, o ``None`` se non ce n'è nessuno.

    `ImageFont.load_default()` c'è sempre ma è una bitmap minuscola, e
    `truetype` ha bisogno di un file che su Windows, Linux e macOS sta in
    posti diversi. Si provano i soliti; se non se ne trova nessuno,
    l'etichetta la disegna :func:`_scritta_ingrandita`.

    In cache: caricare il truetype a ogni immagine era il grosso dei
    dodici secondi del primo avvio (milleduecento caricamenti per
    seicento immagini).
    """
    from PIL import ImageFont
    candidati = (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    )
    for percorso in candidati:
        try:
            return ImageFont.truetype(percorso, dimensione)
        except Exception:
            continue
    return None


def _scritta_ingrandita(immagine, testo, colore, alto, fattore):
    """Scrive `testo` ingrandendo la bitmap del font di sistema.

    Serve dove non c'è nessun truetype: si disegna la scritta piccola su
    una tela sua e poi la si allarga. Sgranata, ma leggibile e identica
    su tutti i sistemi.
    """
    from PIL import Image, ImageDraw, ImageFont

    base = ImageFont.load_default()
    tela = Image.new("RGBA", (max(len(testo) * 7, 10), 14), (0, 0, 0, 0))
    ImageDraw.Draw(tela).text((0, 0), testo, font=base, fill=colore)
    tela = tela.resize((tela.width * fattore, tela.height * fattore),
                       Image.NEAREST)
    immagine.paste(tela, (6 if immagine.width < 400 else 18, alto), tela)


def disegna(etichetta: str, tipo: str, dimensione=DIM_RESIZE):
    """Un segnaposto per quella scheda: fondo in tinta, cornice, scala.

    Non assomiglia a una fotografia di scavo di proposito: c'è scritto
    sopra che è un esempio, così nessuno la confonde con documentazione
    vera.
    """
    from PIL import Image, ImageDraw

    larghezza, altezza = dimensione
    fondo = COLORI.get(tipo.upper(), COLORE_IGNOTO)
    immagine = Image.new("RGB", (larghezza, altezza), fondo)
    disegno = ImageDraw.Draw(immagine)

    chiaro = tuple(min(255, c + 46) for c in fondo)
    scuro = tuple(max(0, c - 40) for c in fondo)

    # La cornice e una banda in alto, dove va l'etichetta.
    bordo = max(2, larghezza // 120)
    disegno.rectangle([0, 0, larghezza - 1, altezza - 1], outline=scuro,
                      width=bordo)
    banda = max(28, altezza // 7)
    disegno.rectangle([bordo, bordo, larghezza - bordo - 1, banda],
                      fill=scuro)

    # Una griglia leggera: fa capire la scala senza fingere un contenuto.
    passo = max(20, larghezza // 12)
    for x in range(passo, larghezza, passo):
        disegno.line([(x, banda), (x, altezza - bordo)], fill=chiaro, width=1)
    for y in range(banda + passo, altezza, passo):
        disegno.line([(bordo, y), (larghezza - bordo, y)], fill=chiaro,
                     width=1)

    # Una scaletta metrica in basso a destra, con la sua tacca.
    scala = max(40, larghezza // 5)
    x1 = larghezza - bordo - 14 - scala
    y1 = altezza - bordo - 22
    disegno.rectangle([x1, y1, x1 + scala, y1 + 7], fill=(250, 250, 250),
                      outline=(20, 20, 20))
    disegno.rectangle([x1, y1, x1 + scala // 2, y1 + 7], fill=(20, 20, 20))

    # Il nord, in alto a destra: un triangolo e la sua asta.
    cx = larghezza - bordo - 22
    cy = banda + 26
    disegno.line([(cx, cy), (cx, cy + 26)], fill=(250, 250, 250), width=2)
    disegno.polygon([(cx, cy - 12), (cx - 7, cy + 2), (cx + 7, cy + 2)],
                    fill=(250, 250, 250))

    grande = larghezza >= 400
    font = _font_grande(max(13, altezza // 26)) if grande else None
    if font is not None:
        disegno.text((16, bordo + 6), etichetta, font=font,
                     fill=(252, 252, 252))
        piccolo = _font_grande(max(11, altezza // 40))
        disegno.text((16, altezza - bordo - 26),
                     "immagine di esempio \u2014 pyArchInit",
                     font=piccolo or font, fill=(250, 250, 250))
    elif grande:
        _scritta_ingrandita(immagine, etichetta[:46], (252, 252, 252),
                            bordo + 8, 3)
        _scritta_ingrandita(immagine, "immagine di esempio",
                            (250, 250, 250), altezza - bordo - 34, 2)
    else:
        # Sulla miniatura ci sta il numero della scheda, non il tipo: tre
        # miniature uguali per ogni record non si distinguerebbero da
        # quelle del record accanto. È il primo pezzo dell'etichetta
        # («US 1 · Scavo archeologico · …» → «US 1»), ingrandito perché
        # il font di sistema a 150 pixel è illeggibile.
        corto = etichetta.split("\u00b7")[0].strip() or (tipo or "?")
        _scritta_ingrandita(immagine, corto[:12], (252, 252, 252), 4, 2)
    return immagine


#: Il foglio dei documenti dei nodi DOC: A4 a 150 DPI.
DIM_DOCUMENTO = (1240, 1754)


def documenti_da_disegnare(conn) -> list:
    """I documenti che i nodi DOC del database di esempio nominano.

    Una tupla per documento: ``(nome_file, titolo, testo)``. Il percorso
    sta in `us_table.doc_usv` nella forma `DosCo\\nome.pdf` — la scheda US
    lo scrive così (`setDoc_ref`), con la barra rovescia anche fuori da
    Windows — e il titolo è la definizione interpretativa del nodo.
    """
    righe = conn.execute(
        "SELECT doc_usv, d_interpretativa, sito, us FROM us_table"
        " WHERE unita_tipo = 'DOC'"
        "   AND trim(coalesce(doc_usv, '')) <> ''").fetchall()
    fuori, visti = [], set()
    for percorso, titolo, sito, us in righe:
        nome = str(percorso).replace("\\", "/").split("/")[-1]
        if not nome.lower().endswith(".pdf") or nome in visti:
            continue
        visti.add(nome)
        fuori.append((nome, str(titolo or nome),
                      "Documento del nodo DOC %s \u00b7 %s" % (us, sito)))
    return fuori


def disegna_documento(titolo: str, testo: str):
    """Una pagina A4 con il titolo, due righe di testo e una figura.

    «Nei nodi DOC associ immagini e testi come PDF» (Enzo): qui la pagina
    porta tutte e due — il testo in alto, un disegno in mezzo — e dice
    che è un esempio.
    """
    from PIL import Image, ImageDraw

    larghezza, altezza = DIM_DOCUMENTO
    pagina = Image.new("RGB", (larghezza, altezza), (252, 251, 248))
    disegno = ImageDraw.Draw(pagina)
    inchiostro = (38, 42, 50)

    margine = 90
    disegno.rectangle([margine, margine, larghezza - margine,
                       altezza - margine], outline=(200, 198, 192), width=2)
    disegno.line([(margine, margine + 110), (larghezza - margine,
                                             margine + 110)],
                 fill=inchiostro, width=3)

    font = _font_grande(40)
    piccolo = _font_grande(24)
    if font is not None:
        disegno.text((margine + 20, margine + 42), titolo[:52], font=font,
                     fill=inchiostro)
        disegno.text((margine + 20, margine + 140), testo[:78],
                     font=piccolo or font, fill=(80, 84, 92))
        disegno.text((margine + 20, altezza - margine - 44),
                     "documento di esempio \u2014 pyArchInit",
                     font=piccolo or font, fill=(120, 124, 132))
    else:
        _scritta_ingrandita(pagina, titolo[:46], inchiostro, margine + 48, 4)
        _scritta_ingrandita(pagina, testo[:60], (80, 84, 92), margine + 150, 2)

    # La figura: lo stesso segnaposto delle foto, incollato nel foglio.
    figura = disegna(titolo, "DOC", (larghezza - 2 * margine - 40,
                                     int((larghezza - 2 * margine - 40) * 0.7)))
    pagina.paste(figura, (margine + 20, margine + 210))

    # E il testo sotto: «immagini **e testi**», ha chiesto Enzo. Righe
    # inventate ma di un diario vero: quote, unità, materiali.
    righe = (
        "Settimana 1 — Rimozione dello strato superficiale di macerie",
        "   (US 1) fino alla quota di 488,62 m s.l.m. Recuperati",
        "   frammenti di maiolica arcaica e laterizi di reimpiego.",
        "",
        "Settimana 2 — Messa in luce della muratura perimetrale (USM 6)",
        "   e del piano d'uso addossato (US 20). Documentazione",
        "   fotogrammetrica del prospetto sud, scala 1:20.",
        "",
        "Settimana 3 — Scavo dei riempimenti delle fosse (US 14, 16, 23)",
        "   e campionatura dei carboni per la datazione radiometrica.",
        "",
        "Settimana 4 — Raggiunta la quota di 488,15 m s.l.m. nel settore",
        "   profondo. Chiusura del saggio e rilievo di fase.",
    )
    alto = margine + 210 + figura.height + 50
    corpo = _font_grande(26)
    for riga in righe:
        if alto > altezza - margine - 80:
            break
        if corpo is not None:
            disegno.text((margine + 20, alto), riga, font=corpo,
                         fill=(60, 64, 72))
        elif riga:
            _scritta_ingrandita(pagina, riga[:60], (60, 64, 72), alto, 2)
        alto += 38
    return pagina


def genera_documenti(db, cartella_dosco) -> tuple:
    """Disegna i PDF dei nodi DOC dentro **DosCo**.

    `(scritti, saltati)`. Come le immagini: salta quelli che ci sono già,
    e non alza mai — un documento che non si disegna lascia il database
    aperto lo stesso.
    """
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        return (0, 0)
    if not os.path.isfile(str(db)):
        return (0, 0)
    try:
        os.makedirs(str(cartella_dosco), exist_ok=True)
    except Exception:
        return (0, 0)

    conn = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try:
        elenco = documenti_da_disegnare(conn)
    except sqlite3.Error:
        return (0, 0)
    finally:
        conn.close()

    scritti = saltati = 0
    for nome, titolo, testo in elenco:
        percorso = os.path.join(str(cartella_dosco), nome)
        if os.path.exists(percorso):
            saltati += 1
            continue
        try:
            pagina = disegna_documento(titolo, testo)
            pagina.save(percorso, "PDF", resolution=150.0)
            scritti += 1
        except Exception:
            continue
    return (scritti, saltati)


def genera(db, cartella_thumb, cartella_resize) -> tuple:
    """Disegna le immagini che il database di esempio nomina.

    Ritorna ``(scritte, saltate)``: salta i file che esistono già, così
    chiamarla due volte non ridisegna niente e **non tocca** un'immagine
    che l'utente ha messo lì lui.

    Non alza: se PIL non c'è o una cartella non si scrive, ritorna
    ``(0, 0)`` — il database di esempio si apre comunque, le schede
    mostreranno i media senza anteprima.
    """
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        return (0, 0)
    if not os.path.isfile(str(db)):
        return (0, 0)
    try:
        os.makedirs(str(cartella_thumb), exist_ok=True)
        os.makedirs(str(cartella_resize), exist_ok=True)
    except Exception:
        return (0, 0)

    conn = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try:
        elenco = media_da_disegnare(conn)
    except sqlite3.Error:
        return (0, 0)
    finally:
        conn.close()

    scritte = saltate = 0
    for nome_thumb, nome_grande, etichetta, tipo in elenco:
        for nome, dimensione, cartella in (
                (nome_thumb, DIM_THUMB, cartella_thumb),
                (nome_grande, DIM_RESIZE, cartella_resize)):
            percorso = os.path.join(str(cartella), nome)
            if os.path.exists(percorso):
                saltate += 1
                continue
            try:
                immagine = disegna(etichetta, tipo, dimensione)
                # `compress_level=1` e niente `optimize`: la
                # compressione massima costa il doppio e non serve a un
                # segnaposto a tinte piatte. Spegnerla del tutto non si
                # può: un file passerebbe da 15 KB a 1,3 MB. E la
                # conversione in palette, che pure fa file più piccoli,
                # costa più di quanto risparmia (misurato: +4 secondi su
                # 606 immagini).
                immagine.save(percorso, optimize=False, compress_level=1,
                              dpi=(100, 100) if dimensione == DIM_THUMB
                              else (300, 300))
                scritte += 1
            except Exception:
                # Un nome di file impossibile su questo sistema non deve
                # fermare le altre duecentottanta immagini.
                continue
    return (scritte, saltate)
