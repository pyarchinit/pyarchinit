"""I media che illustrano la narrativa (17 ottobre 2026).

Enzo: «l'AI in modo deterministico possa scegliere i media, 3D, da
incorporare nella narrativa seguendo il filo logico della narrativa, mentre
le fonti devono esserci sempre». Le fonti le mette :mod:`em_narrative_html`;
qui si scelgono le immagini, i video e i modelli 3D da mettere **dentro** il
capitolo, dopo il paragrafo che ne parla.

* **i candidati** di un capitolo sono i media delle unità di cui parla
  (:func:`em_narrative_html.chapter_units`) e quelli della loro catena di
  prova — l'immagine dell'estrattore, la tavola del documento —, presi dal
  database come li mostra la scheda; i PDF e gli altri documenti no: sono
  fonti;
* **la scelta** la fa l'AI con temperatura zero (il chiamante), fra quei
  candidati e soltanto fra loro, con il paragrafo dopo cui metterli e una
  didascalia nella lingua della prosa; senza AI, o se la risposta non si
  legge, la scelta è automatica: i media delle unità nell'ordine in cui il
  testo le nomina;
* **la scelta resta nel file**, nei dati della narrativa
  (``data["pyarchinit_media"]``, per capitolo): l'esportazione la rilegge,
  sempre uguale, finché non si sceglie di nuovo.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence

#: dove sta la scelta, nei dati della narrativa
DATA_KEY = "pyarchinit_media"
#: quanti media al massimo in un capitolo
MAX_PER_CHAPTER = 4
#: quanti candidati si mostrano al modello
MAX_CANDIDATES = 40
MAX_CAPTION = 200

_TRE_D = ("glb", "gltf", "obj", "ply", "stl", "fbx", "3ds", "dae", "las", "laz", "e57")
_IMMAGINI = ("jpg", "jpeg", "png", "gif", "webp", "bmp", "tif", "tiff")
_VIDEO = ("mp4", "mov", "avi", "mkv", "webm", "m4v")

_LINGUE = {"it": "italiano", "en": "English", "de": "German", "fr": "French", "es": "Spanish",
           "ca": "Catalan", "pt": "Portuguese", "ro": "Romanian", "el": "Greek", "ar": "Arabic"}


@dataclass
class MediaCandidate:
    """Un media che il capitolo potrebbe mostrare. ``key`` lo ritrova a
    ogni esportazione: l'id del nodo e il nome del file."""
    key: str
    unit_id: str
    unit_name: str
    filename: str
    kind: str
    description: str = ""
    reading: str = ""
    id_media: Optional[int] = None
    thumb_path: str = ""
    file_path: str = ""


@dataclass
class MediaReport:
    chapters: int = 0
    chosen: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)


def media_kind(filename: str) -> Optional[str]:
    est = os.path.splitext(str(filename or ""))[1].lstrip(".").lower()
    if est in _TRE_D:
        return "3d"
    if est in _IMMAGINI:
        return "image"
    if est in _VIDEO:
        return "video"
    return None


def chapter_key(chapter) -> str:
    """L'àncora e il titolo del capitolo. L'àncora da sola non basta: in
    TempluMare «Virtual Activity 2» e «3» sono ancorati alla stessa attività,
    e la scelta di uno prendeva il posto di quella dell'altro."""
    return "%s#%s" % (getattr(chapter, "anchor", None) or "", getattr(chapter, "title", "") or "")


def stored_choices(narrative, chapter) -> List[dict]:
    tutte = (getattr(narrative, "data", None) or {}).get(DATA_KEY) or {}
    return list(tutte.get(chapter_key(chapter)) or [])


def store_choices(narrative, chapter, choices: Sequence[dict]) -> None:
    tutte = dict((narrative.data or {}).get(DATA_KEY) or {})
    if choices:
        tutte[chapter_key(chapter)] = [dict(c) for c in choices]
    else:
        tutte.pop(chapter_key(chapter), None)
    if tutte:
        narrative.data[DATA_KEY] = tutte
    else:
        narrative.data.pop(DATA_KEY, None)


def chapter_paragraphs(chapter, graph=None) -> List[str]:
    """I paragrafi della prosa del capitolo, nell'ordine in cui la pagina li
    mostra (i blocchi divisi alle righe vuote), con i titoli «###» esclusi:
    è su questi che si conta «dopo il paragrafo n». Le unità citate col loro
    nome, come le legge chi legge (e il modello)."""
    from s3dgraphy.nodes.narrative_node import plain_mentions
    nomi = {n.node_id: str(getattr(n, "name", "") or n.node_id)
            for n in (getattr(graph, "nodes", None) or [])}
    out: List[str] = []
    for b in getattr(chapter, "blocks", None) or []:
        if getattr(b, "block_type", "") != "prose":
            continue
        try:
            testo = plain_mentions(getattr(b, "text", "") or "", lambda ref: nomi.get(ref, ref))
        except Exception:                                    # noqa: BLE001
            testo = str(getattr(b, "text", "") or "")
        for paragrafo in re.split(r"\n\s*\n", testo):
            paragrafo = paragrafo.strip()
            if paragrafo and not re.match(r"^#{2,4}\s", paragrafo):
                out.append(paragrafo)
    return out


# ---------------------------------------------------------------- candidati

def chapter_media_candidates(graph, chapter, connection, thumb_base: str = "",
                             resize_base: str = "") -> List[MediaCandidate]:
    """I media delle unità di cui il capitolo parla e della loro catena di
    prova (proprietà → estrattore → documento), dal database: immagini,
    video e modelli 3D. Senza database, nessuno."""
    if connection is None or graph is None:
        return []
    from ..utility.em_matrix_links import media_for_unit
    from . import em_narrative_html as nh
    nodi = {n.node_id: n for n in getattr(graph, "nodes", None) or []}
    candidati: List[MediaCandidate] = []
    visti = set()

    def aggiungi(nodo, unita, lettura=""):
        try:
            refs = media_for_unit(connection, nodo, limit=6)
        except Exception:                                    # noqa: BLE001
            refs = []
        for ref in refs:
            nome = os.path.basename(str(ref.original_file or "")) or str(ref.name or "")
            tipo = media_kind(nome)
            chiave = "%s::%s" % (nodo.node_id, nome)
            if tipo is None or chiave in visti:
                continue
            visti.add(chiave)
            candidati.append(MediaCandidate(
                key=chiave, unit_id=unita.node_id, unit_name=str(getattr(unita, "name", "") or ""),
                filename=nome, kind=tipo,
                description=str(getattr(unita, "description", "") or "")[:200], reading=lettura,
                id_media=ref.id_media,
                thumb_path=os.path.join(thumb_base, ref.thumb_file) if thumb_base and ref.thumb_file else "",
                file_path=str(ref.original_file or "")))

    unita_ids = nh.chapter_units(graph, chapter)
    for uid in unita_ids:
        unita = nodi.get(uid)
        if unita is not None:
            aggiungi(unita, unita)
    uscite = nh._uscite(graph)
    for uid in unita_ids:
        unita = nodi.get(uid)
        if unita is None:
            continue
        for pid in uscite[uid]["has_property"]:
            proprieta = nodi.get(pid)
            for prov in uscite[pid]["has_data_provenance"]:
                nodo = nodi.get(prov)
                estrattori = (uscite[prov]["combines"] if getattr(nodo, "node_type", "") == "combiner"
                              else [prov])
                for xid in estrattori:
                    estrattore = nodi.get(xid)
                    if estrattore is None:
                        continue
                    lettura = "%s — %s" % (getattr(proprieta, "name", "") or "",
                                           getattr(estrattore, "name", "") or "")
                    aggiungi(estrattore, unita, lettura)
                    for did in uscite[xid]["extracted_from"]:
                        if did in nodi:
                            aggiungi(nodi[did], unita, lettura)
        if len(candidati) >= MAX_CANDIDATES:
            break
    return candidati[:MAX_CANDIDATES]


# ---------------------------------------------------------------- la scelta

def media_messages(title: str, paragraphs: Sequence[str], candidates: Sequence[MediaCandidate],
                   lang: Optional[str]) -> List[Dict[str, str]]:
    """Le istruzioni per il modello: scegliere fra i candidati quelli che
    illustrano il filo del capitolo, dove metterli, con che didascalia."""
    lingua = _LINGUE.get(str(lang or "en")[:2].lower(), "English")
    sistema = (
        "You choose the illustrations of one chapter of an archaeological narrative. "
        "You are given the chapter's paragraphs, numbered, and a list of media (3D models, "
        "images, videos) that belong to the units the chapter talks about. Choose at most %d "
        "media that follow the logical thread of the text: the ones a reader needs where the "
        "text discusses that unit or that evidence. Use only keys from the list. For each, say "
        "after which paragraph it goes (0 = before the first) and write a one-sentence caption "
        "in %s that states only what the text and the list say: invent nothing. If nothing "
        "fits, choose nothing. Reply with JSON only: "
        '{"choices": [{"key": "...", "after": 1, "caption": "..."}]}.'
        % (MAX_PER_CHAPTER, lingua))
    righe = ["Chapter: %s" % title, "", "Paragraphs:"]
    for i, p in enumerate(paragraphs, 1):
        righe.append("[%d] %s" % (i, str(p)[:1200]))
    righe += ["", "Media:"]
    for c in candidates:
        righe.append(json.dumps({"key": c.key, "kind": c.kind, "unit": c.unit_name, "file": c.filename,
                                 "unit_description": c.description, "reading": c.reading},
                                ensure_ascii=False))
    return [{"role": "system", "content": sistema}, {"role": "user", "content": "\n".join(righe)}]


def parse_choices(text: str, candidates: Sequence[MediaCandidate], n_paragrafi: int,
                  massimo: int = MAX_PER_CHAPTER) -> List[dict]:
    """La risposta del modello, controllata: solo chiavi dei candidati, una
    volta sola, il paragrafo dentro il capitolo, la didascalia corta."""
    m = re.search(r"\{.*\}", str(text or ""), re.S)
    if not m:
        raise ValueError("risposta senza JSON")
    dati = json.loads(m.group(0))
    validi = {c.key for c in candidates}
    scelte: List[dict] = []
    for voce in dati.get("choices") or []:
        chiave = str(voce.get("key") or "")
        if chiave not in validi or any(s["key"] == chiave for s in scelte):
            continue
        try:
            dopo = int(voce.get("after") or 0)
        except (TypeError, ValueError):
            dopo = n_paragrafi
        scelte.append({"key": chiave, "after": max(0, min(dopo, n_paragrafi)),
                       "caption": str(voce.get("caption") or "").strip()[:MAX_CAPTION]})
        if len(scelte) >= massimo:
            break
    return scelte


def auto_choices(paragraphs: Sequence[str], candidates: Sequence[MediaCandidate],
                 massimo: int = 3) -> List[dict]:
    """Senza AI: i media delle unità nell'ordine in cui il testo le nomina,
    uno per unità, dopo il paragrafo che la nomina per primo."""
    def primo(nome):
        for i, p in enumerate(paragraphs, 1):
            if nome and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(nome), p):
                return i
        return None

    ordinati = []
    for c in candidates:
        dove = primo(c.unit_name)
        if dove is not None:
            ordinati.append((dove, c))
    ordinati.sort(key=lambda x: x[0])
    scelte, unita = [], set()
    for dove, c in ordinati:
        if c.unit_id in unita:
            continue
        unita.add(c.unit_id)
        scelte.append({"key": c.key, "after": dove, "caption": "", "by": "auto"})
        if len(scelte) >= massimo:
            break
    return scelte


def choose_media(graph, narrative, *, chat: Optional[Callable], model: str = "",
                 lang: Optional[str] = None, connection=None, media_base=("", ""),
                 progress=None, cancelled=None) -> MediaReport:
    """Per ogni capitolo con dei candidati: la scelta dell'AI (``chat``
    riceve i messaggi e restituisce il testo; la temperatura zero la mette
    chi chiama il modello), o quella automatica senza ``chat`` o se l'AI
    non risponde bene; salvata nella narrativa."""
    miniature, ridotte = media_base or ("", "")
    esito = MediaReport()
    capitoli = list(getattr(narrative, "chapters", None) or [])
    for i, cap in enumerate(capitoli, 1):
        if cancelled is not None and cancelled():
            break
        candidati = chapter_media_candidates(graph, cap, connection, miniature, ridotte)
        if not candidati:
            continue
        esito.chapters += 1
        if progress is not None:
            progress(i, len(capitoli), str(getattr(cap, "title", "") or ""))
        paragrafi = chapter_paragraphs(cap, graph)
        scelte = None
        if chat is not None:
            try:
                risposta = chat(media_messages(str(cap.title), paragrafi, candidati, lang))
                testo = risposta[0] if isinstance(risposta, tuple) else risposta
                scelte = parse_choices(testo, candidati, len(paragrafi))
                quando = datetime.now().isoformat(timespec="seconds")
                for s in scelte:
                    s.update({"by": "ai", "model": str(model), "date": quando})
            except Exception as e:                           # noqa: BLE001
                esito.failed += 1
                esito.errors.append("%s: %s" % (cap.title, e))
                scelte = None
        if scelte is None:
            scelte = auto_choices(paragrafi, candidati)
        store_choices(narrative, cap, scelte)
        esito.chosen += len(scelte)
    return esito


# ---------------------------------------------------------------- nella pagina

#: un modello o un video entra nella pagina fino a questa misura
MAX_MEDIA_FILE = 15 * 1024 * 1024
#: e tutti insieme fino a questa
MAX_MEDIA_FILES = 60 * 1024 * 1024
_LATO_FIGURA = 1400

_CSS_MEDIA = """
/* pyArchInit: i media scelti per la narrativa */
figure.pya-media { margin: 1.2rem 0 1.4rem; }
figure.pya-media a.pya-fonte { display: block; border: 0; position: relative; }
figure.pya-media img { display: block; max-width: 100%; height: auto; margin: 0 auto;
  border-radius: 6px; border: 1px solid rgba(128,128,128,.25); }
figure.pya-media figcaption { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: .85rem; color: #555; margin-top: .35rem; text-align: center; }
.pya-media-3d { position: absolute; right: .6rem; bottom: .6rem; background: rgba(0,0,0,.65);
  color: #fff; font: 12px/1.2 -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: .3rem .55rem; border-radius: 999px; }
.pya-media-vuoto { display: block; padding: 2rem; text-align: center; border: 1px dashed #aaa; }
model-viewer.pya-vista { width: 100%; height: 70vh; background: #f4f4f2; }
@media (prefers-color-scheme: dark) { figure.pya-media figcaption { color: #9aa3ae; } }
"""

_PAROLE_MEDIA = {"it": "Apri il modello 3D", "en": "Open the 3D model"}


def add_media(pagina: str, per_capitolo: List[List[dict]], registro: Dict[str, dict],
              lang: Optional[str] = None) -> str:
    """Le figure dei media scelti, dentro i capitoli: ognuna dopo il
    paragrafo di prosa indicato (0 = prima del primo; i sottotitoli «###»
    non contano), oltre l'ultimo in fondo al capitolo. Ogni figura è un
    hotspot come le fonti: la scheda al passaggio, il pannello al clic —
    per un modello 3D il visore, per un video il lettore."""
    import html as _html
    from . import em_narrative_html as nh
    if not registro or not any(per_capitolo):
        return pagina
    parola_3d = _PAROLE_MEDIA.get(str(lang or "it")[:2].lower(), _PAROLE_MEDIA["en"])
    fine = nh._fine_dei_capitoli(pagina)
    inizi = [m.start() for m in re.finditer(r"<h2[\s>]", pagina[:fine])]
    messi = 0
    for k in range(len(inizi) - 1, -1, -1):
        scelte = [s for s in (per_capitolo[k] if k < len(per_capitolo) else [])
                  if s.get("key") in registro]
        if not scelte:
            continue
        a, b = inizi[k], (inizi[k + 1] if k + 1 < len(inizi) else fine)
        segmento = pagina[a:b]
        dopo_titolo = segmento.index("</h2>") + len("</h2>") if "</h2>" in segmento else 0
        fine_paragrafi = [m.end() for m in re.finditer(r"<p>(?!#{2,4}\s)(?:(?!</p>).)*</p>", segmento, re.S)]
        posti: Dict[int, List[str]] = {}
        for s in scelte:
            voce = registro[s["key"]]
            n = int(s.get("after") or 0)
            posto = dopo_titolo if n <= 0 else (fine_paragrafi[n - 1] if n - 1 < len(fine_paragrafi)
                                                else len(segmento))
            didascalia = str(s.get("caption") or "")
            titolo = str(voce.get("title") or "")
            immagine = ('<img src="%s" alt="%s" loading="lazy">' % (voce["preview"], _html.escape(didascalia or titolo, quote=True))
                        if voce.get("preview") else '<span class="pya-media-vuoto">%s</span>' % _html.escape(titolo))
            segno = '<span class="pya-media-3d">%s</span>' % _html.escape(parola_3d) if voce.get("model") else ""
            chi = " · ".join(x for x in (str(voce.get("unit") or ""), titolo) if x)
            figura = ('\n<figure class="pya-media"><a class="pya-fonte" href="#pya-f-%s" role="button" data-src="%s">%s%s</a>'
                      '<figcaption>%s<span class="pya-desc">%s</span></figcaption></figure>\n'
                      % (_html.escape(s["key"], quote=True), _html.escape(s["key"], quote=True), immagine, segno,
                         (_html.escape(didascalia) + " ") if didascalia else "", _html.escape(chi)))
            posti.setdefault(posto, []).append(figura)
            messi += 1
        for posto in sorted(posti, reverse=True):
            segmento = segmento[:posto] + "".join(posti[posto]) + segmento[posto:]
        pagina = pagina[:a] + segmento + pagina[b:]
    if not messi:
        return pagina
    return pagina.replace("</style>", _CSS_MEDIA + "</style>", 1)


def media_registry(graph, narrative, connection, media_base=("", ""), *,
                   max_file: int = MAX_MEDIA_FILE, budget: int = MAX_MEDIA_FILES,
                   render_3d: bool = True):
    """Le scelte salvate, capitolo per capitolo (nell'ordine dei capitoli
    della narrativa), e le voci della pagina per i media scelti: la vista
    grande (l'immagine ridotta, il modello reso fuori da QGIS, il primo
    fotogramma del video), il file dentro la pagina quando è un GLB o un
    video non troppo grandi, il percorso dell'originale. Chiavi «m::…», per
    non confonderle con le fonti."""
    import base64
    from pathlib import Path
    from . import em_narrative_html as nh
    miniature, ridotte = media_base or ("", "")
    per_capitolo: List[List[dict]] = []
    registro: Dict[str, dict] = {}
    da_disegnare = []
    speso = 0
    for cap in getattr(narrative, "chapters", None) or []:
        scelte = stored_choices(narrative, cap)
        if not scelte:
            per_capitolo.append([])
            continue
        candidati = {c.key: c for c in chapter_media_candidates(graph, cap, connection, miniature, ridotte)}
        lista = []
        for s in scelte:
            c = candidati.get(s.get("key"))
            if c is None:
                continue
            chiave = "m::" + c.key
            lista.append({"key": chiave, "after": s.get("after", 0), "caption": s.get("caption", "")})
            if chiave in registro:
                continue
            est = os.path.splitext(c.filename)[1].lstrip(".").lower()
            file = c.file_path if c.file_path and os.path.isfile(c.file_path) else ""
            voce = {"title": c.filename, "description": s.get("caption") or c.description, "unit": c.unit_name,
                    "kind": "3D" if c.kind == "3d" else est.upper(), "model": c.kind == "3d",
                    "uses": [[c.unit_name, c.reading, ""]] if c.reading else [],
                    "preview": "", "file": "", "mime": "", "path": c.file_path,
                    "link": Path(os.path.abspath(file)).as_uri() if file else ""}
            if c.kind == "image" and file:
                voce["preview"] = nh._anteprima_di(file, est, lato=_LATO_FIGURA)
            elif c.kind == "video" and file:
                voce["preview"] = _fotogramma_uri(file)
                voce["mime"] = "video/mp4" if est in ("mp4", "m4v") else ""
            elif c.kind == "3d":
                voce["mime"] = "model/gltf-binary" if est == "glb" else ""
                if file and render_3d:
                    da_disegnare.append((chiave, file))
            if not voce["preview"] and c.thumb_path and os.path.isfile(c.thumb_path):
                with open(c.thumb_path, "rb") as fh:
                    voce["preview"] = nh._data_uri(fh.read(), "image/png")
            if file and voce["mime"] and voce["mime"] != "image/jpeg":
                misura = os.path.getsize(file)
                if misura <= max_file and speso + misura <= budget:
                    with open(file, "rb") as fh:
                        voce["file"] = base64.b64encode(fh.read()).decode("ascii")
                    speso += misura
            registro[chiave] = voce
        per_capitolo.append(lista)
    if da_disegnare:
        _viste_3d(da_disegnare, registro)
    return per_capitolo, registro


def _viste_3d(lavori, registro) -> None:
    """Le viste grandi dei modelli scelti, disegnate tutte insieme fuori da
    QGIS (``render_models_png``); un modello che non si disegna tiene la
    miniatura dell'importazione."""
    import tempfile
    import shutil
    from ..utility import media_preview
    from . import em_narrative_html as nh
    cartella = tempfile.mkdtemp(prefix="pyarchinit_vista_3d_")
    try:
        jobs = [(file, os.path.join(cartella, "%d.png" % i)) for i, (_k, file) in enumerate(lavori)]
        esiti = media_preview.render_models_png(jobs, (960, 720))
        for (chiave, _file), (_src, out) in zip(lavori, jobs):
            if esiti.get(out) is None and os.path.isfile(out):
                with open(out, "rb") as fh:
                    registro[chiave]["preview"] = nh._data_uri(fh.read(), "image/png")
    finally:
        shutil.rmtree(cartella, ignore_errors=True)


def _fotogramma_uri(file: str) -> str:
    try:
        import cv2
        from . import em_narrative_html as nh
        video = cv2.VideoCapture(file)
        try:
            ok, frame = video.read()
        finally:
            video.release()
        if not ok:
            return ""
        ok, png = cv2.imencode(".jpg", frame)
        return nh._data_uri(png.tobytes(), "image/jpeg") if ok else ""
    except Exception:                                        # noqa: BLE001
        return ""
