"""I file che un em.json di EMStudio cita diventano media di pyArchInit
(Enzo, 16 ottobre 2026: «dovrebbe poter importare anche i media»).

Da ogni scheda importata si seguono i legami del grafo verso i file:

* scheda —has_linked_resource→ risorsa —has_file→ file;
* scheda —has_representation_model / has_semantic_shape→ modello —
  has_linked_resource→ risorsa —has_file→ file;
* l'``url`` della risorsa o del documento, se è un file e non un indirizzo web.

I file che esistono (il percorso è relativo alla cartella dell'em.json, o
il solo nome del file in quella cartella) diventano media collegati alla
scheda, copiati nella cartella dei media con le miniature: la filiera è
quella dell'importazione da QField (``qfield_importer``). Quelli che
mancano si elencano. I PDF restano nel campo «documentazione» della
scheda del documento: la scheda media del plugin non li apre.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

#: Le estensioni che la scheda media del plugin sa mostrare, col tipo.
MEDIA_TYPES = {
    "jpg": "image", "jpeg": "image", "png": "image", "tif": "image",
    "tiff": "image", "bmp": "image", "gif": "image", "webp": "image",
    "mp4": "video", "avi": "video", "mov": "video", "mkv": "video",
    "flv": "video",
    "obj": "3d_model", "glb": "3d_model", "gltf": "3d_model", "ply": "3d_model",
    "stl": "3d_model", "fbx": "3d_model", "3ds": "3d_model",
}

#: I legami che portano da una scheda ai suoi file.
_VERSO_I_FILE = frozenset({
    "has_linked_resource", "has_file", "has_representation_model",
    "has_semantic_shape",
})


@dataclass
class EmMediaResult:
    inserted: int = 0
    linked: int = 0
    already_present: int = 0
    thumbnails: int = 0
    #: i file citati che non ci sono accanto all'em.json
    missing: List[str] = field(default_factory=list)
    #: i file citati che la scheda media non apre (pdf, mtl, …), per estensione
    skipped_types: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parti = ["%d media nuovi, %d collegamenti, %d già presenti"
                 % (self.inserted, self.linked, self.already_present)]
        if self.thumbnails:
            parti.append("%d miniature" % self.thumbnails)
        if self.missing:
            esempi = ", ".join(os.path.basename(p) for p in self.missing[:3])
            parti.append("%d file citati ma non trovati accanto all'em.json (%s%s)"
                         % (len(self.missing), esempi, "…" if len(self.missing) > 3 else ""))
        if self.skipped_types:
            parti.append("non sono media: " + ", ".join(
                "%s %d" % (k, v) for k, v in sorted(self.skipped_types.items())))
        return "; ".join(parti) + "."


def _url_di_file(node) -> Optional[str]:
    """L'url di un nodo se è un file, non un indirizzo web."""
    for valore in (getattr(node, "url", None), (getattr(node, "data", None) or {}).get("url")
                   if isinstance(getattr(node, "data", None), dict) else None,
                   (getattr(node, "attributes", None) or {}).get("url")):
        if valore and isinstance(valore, str):
            v = valore.strip()
            if v and "://" not in v and not v.lower().startswith(("www.", "mailto:")):
                return v
    return None


def collect_files(graph, rows: Dict[str, Tuple[Any, str]]) -> Dict[str, List[str]]:
    """``{id della scheda: [url dei file]}``: i file raggiungibili da ogni
    scheda attraverso risorse e modelli (al massimo tre passi)."""
    per_id = {str(n.node_id): n for n in getattr(graph, "nodes", None) or []}
    uscite: Dict[str, List[str]] = {}
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) in _VERSO_I_FILE:
            uscite.setdefault(str(e.edge_source), []).append(str(e.edge_target))
    out: Dict[str, List[str]] = {}
    for nid, (nodo, _ut) in rows.items():
        trovati: List[str] = []
        proprio = _url_di_file(nodo)
        if proprio:
            trovati.append(proprio)
        visti = {nid}
        frontiera = [nid]
        for _passo in range(3):
            prossimi = []
            for corrente in frontiera:
                for dopo in uscite.get(corrente, []):
                    if dopo in visti or dopo in rows:
                        continue
                    visti.add(dopo)
                    prossimi.append(dopo)
                    url = _url_di_file(per_id.get(dopo))
                    if url and type(per_id.get(dopo)).__name__ in ("ResourceFileNode", "ResourceNode"):
                        trovati.append(url)
            frontiera = prossimi
        if trovati:
            out[nid] = list(dict.fromkeys(trovati))
    return out


def resolve_file(url: str, base_dir: str) -> Optional[str]:
    """Il file sul disco: il percorso relativo alla cartella dell'em.json,
    o il solo nome del file in quella cartella."""
    for candidato in (Path(base_dir) / url, Path(base_dir) / os.path.basename(url)):
        try:
            if candidato.is_file():
                return str(candidato.resolve())
        except OSError:
            continue
    return None


def _engine(db):
    from sqlalchemy import create_engine
    if hasattr(db, "engine"):
        return db.engine
    if isinstance(db, Path) or (isinstance(db, str) and "://" not in db):
        return create_engine("sqlite:///%s" % db)
    if isinstance(db, str):
        return create_engine(db)
    return db


def import_emjson_media(db, graph, sito: str, emjson_path: str, *,
                        media_dest: Optional[str] = None,
                        thumb_path: Optional[str] = None,
                        thumb_resize: Optional[str] = None,
                        make_thumbs: bool = True, log=None) -> EmMediaResult:
    """Registra come media i file citati dall'em.json per le schede del
    sito appena importate. Da chiamare DOPO l'importazione delle schede
    (servono i loro ``id_us``). Una seconda chiamata non duplica niente."""
    from sqlalchemy import MetaData, text
    from ...utility import qfield_importer as qf
    from ...s3dgraphy.sync import em_native_import as emn
    from .graph_ingestor import _NON_STRAT_TYPES, _PARADATA_ROW_TYPES, _is_synthetic_node

    scrivi = log or (lambda _m: None)
    esito = EmMediaResult()
    rows = emn.row_nodes(graph, _NON_STRAT_TYPES - _PARADATA_ROW_TYPES, _is_synthetic_node)
    names = emn.row_names(rows, getattr(graph, "edges", None) or [])
    base_dir = os.path.dirname(os.path.abspath(str(emjson_path)))
    da_importare: List[Tuple[str, str, str, str]] = []      # (id scheda, file, estensione, tipo)
    for nid, urls in collect_files(graph, rows).items():
        for url in urls:
            estensione = os.path.splitext(url)[1].lstrip(".").lower()
            tipo = MEDIA_TYPES.get(estensione)
            if tipo is None:
                esito.skipped_types[estensione or "?"] = esito.skipped_types.get(estensione or "?", 0) + 1
                continue
            percorso = resolve_file(url, base_dir)
            if percorso is None:
                if url not in esito.missing:
                    esito.missing.append(url)
                continue
            da_importare.append((nid, percorso, estensione, tipo))
    if not da_importare:
        return esito

    engine = _engine(db)
    risultato = qf.QFieldImportResult()
    risultato.dry_run = False
    qf._wire_spatialite(engine, risultato.warnings)
    copia = bool(media_dest)
    metadata = MetaData()
    inseriti: List[Dict[str, Any]] = []
    us_id_map: Dict[str, Any] = {}
    with engine.connect() as conn:
        transazione = conn.begin()
        try:
            for k, (nid, percorso, estensione, tipo) in enumerate(da_importare):
                nodo, unita_tipo = rows[nid]
                if nid not in us_id_map:
                    riga = conn.execute(
                        text("SELECT id_us FROM us_table WHERE sito = :s AND us = :u AND unita_tipo = :t"),
                        {"s": sito, "u": names[nid], "t": unita_tipo}).fetchone()
                    if riga is None:
                        esito.warnings.append("Scheda %s %s non trovata: media saltato"
                                              % (unita_tipo, names[nid]))
                        continue
                    us_id_map[nid] = riga[0]
                nome = os.path.splitext(os.path.basename(percorso))[0]
                # import_media legge la sorgente come cartella + percorso: ogni
                # file ha la sua cartella, quindi una chiamata per file.
                media = {"_fid": str(k), "filename": nome, "filetype": estensione,
                         "mediatype": tipo, "descrizione": str(getattr(nodo, "name", "") or ""),
                         "filepath": os.path.basename(percorso) if copia else percorso}
                legame = {"id_entity": nid, "id_media": str(k), "entity_type": "US",
                          "table_name": "us_table", "media_name": nome}
                saltati = risultato.media.skipped
                inseriti += qf.import_media(
                    conn, metadata, engine, [media], [legame], us_id_map,
                    os.path.dirname(percorso) if copia else "", media_dest,
                    risultato, False, scrivi, copy_media=copia)
                if risultato.media.skipped > saltati:
                    esito.already_present += 1
            transazione.commit()
        except Exception:
            transazione.rollback()
            raise
    if copia:
        qf.copy_media_files(risultato, scrivi)
    esito.inserted = risultato.media.inserted
    esito.linked = risultato.links.inserted
    immagini = [m for m in inseriti if m.get("mediatype") == "image"]
    if make_thumbs and immagini and thumb_path and thumb_resize:
        prima = risultato.thumbs.inserted
        qf.make_thumbnails(engine, immagini, thumb_path, thumb_resize, risultato, scrivi)
        esito.thumbnails = risultato.thumbs.inserted - prima
    esito.warnings.extend(risultato.warnings)
    esito.warnings.extend(risultato.media_upload_failures)
    return esito
