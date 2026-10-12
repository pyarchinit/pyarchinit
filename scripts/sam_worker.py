#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Worker di segmentazione per pyArchInit: gira nel Python di `sam_venv`, non in QGIS.

Legge un PNG, segmenta, scrive un JSON di poligoni **in pixel** (riga/colonna
con origine in alto a sinistra, al centro del pixel). La georeferenza non
entra qui: ci pensa QGIS, che ha la geotrasformazione dell'immagine.

    python sam_worker.py --image in.png --output out.json --backend sam2 \\
        --weights sam2.1_t.pt --mode auto|points|boxes [--prompts prompts.json]
    python sam_worker.py ... --backend yoloe --weights yoloe-26s-seg.pt --classes "building,road"
    python sam_worker.py ... --backend replicate --api-key ...           (SAM 2 in cloud, automatico)
    python sam_worker.py ... --backend roboflow --api-key ... --classes "stones"   (SAM 3, a testo)

Backend:
- sam2     Meta SAM 2.1 via ultralytics: tutto automatico, punti, riquadri.
- yoloe    YOLOE-26 via ultralytics: classi a testo libero («building, road,
           river, field»), con MobileCLIP2 come codificatore (file .ts nella
           cartella di lavoro, scaricato da pyArchInit).
- replicate  API Replicate `meta/sam-2` (maschere automatiche).
- roboflow   API Roboflow SAM 3 `concept_segment` (prompt testuali).

Uscita: {"backend", "model", "image": {"width","height"}, "polygons":
[{"ring": [[c, r], ...], "holes": [...], "score", "label", "area_px"}], "warnings": []}
Le righe che iniziano con «[sam]» su stdout sono messaggi di avanzamento.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time

MASK_THRESHOLD = 127


def say(msg):
    print(f"[sam] {msg}", flush=True)


# ----------------------------------------------------------------------
# Poligoni dalle maschere (numpy + OpenCV)
# ----------------------------------------------------------------------
def parse_classes(text):
    """«building, road ,river» -> ['building', 'road', 'river'] (vuoti e doppioni via)."""
    out = []
    for part in (text or "").replace(";", ",").split(","):
        name = part.strip()
        if name and name.lower() not in [o.lower() for o in out]:
            out.append(name)
    return out


def _simplify(contour, tolerance):
    import cv2
    if tolerance and tolerance > 0:
        contour = cv2.approxPolyDP(contour, float(tolerance), True)
    pts = contour.reshape(-1, 2).astype(float)
    return [[float(x) + 0.5, float(y) + 0.5] for x, y in pts]      # centro del pixel


def masks_to_polygons(masks, scores=None, labels=None, min_area=20.0, simplify=1.0):
    """Maschere (N, H, W) -> poligoni con anelli esterni e buchi, in pixel."""
    import cv2
    import numpy as np

    polygons = []
    for i, mask in enumerate(masks):
        m8 = (np.asarray(mask) > 0).astype(np.uint8)
        if not m8.any():
            continue
        contours, hierarchy = cv2.findContours(m8, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            continue
        hierarchy = hierarchy[0]
        for ci, contour in enumerate(contours):
            if hierarchy[ci][3] != -1:          # e' un buco: lo prende il genitore
                continue
            area = float(cv2.contourArea(contour))
            if area < min_area:
                continue
            ring = _simplify(contour, simplify)
            if len(ring) < 3:
                continue
            holes = []
            child = hierarchy[ci][2]
            while child != -1:
                hole = contours[child]
                if cv2.contourArea(hole) >= min_area:
                    hr = _simplify(hole, simplify)
                    if len(hr) >= 3:
                        holes.append(hr)
                child = hierarchy[child][0]
            polygons.append({
                "ring": ring, "holes": holes, "area_px": area,
                "score": None if scores is None else float(scores[i]),
                "label": None if labels is None else labels[i],
            })
    return polygons


def rings_to_polygons(rings, scores=None, labels=None, min_area=20.0):
    """Anelli gia' poligonali (API cloud) -> stesso formato, con l'area di Gauss."""
    polygons = []
    for i, ring in enumerate(rings):
        pts = [[float(x), float(y)] for x, y in ring]
        if len(pts) < 3:
            continue
        area = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            area += x1 * y2 - x2 * y1
        area = abs(area) / 2.0
        if area < min_area:
            continue
        polygons.append({"ring": pts, "holes": [], "area_px": area,
                         "score": None if scores is None else float(scores[i]),
                         "label": None if labels is None else labels[i]})
    return polygons


def load_image(path):
    import cv2
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"non leggo l'immagine {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def pick_device(requested):
    if requested and requested != "auto":
        return requested
    try:
        import torch
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:       # noqa: BLE001
        pass
    return "cpu"


def _masks_array(result):
    """Le maschere di un Results di ultralytics come array (N, H, W) uint8 alla
    dimensione dell'immagine originale."""
    import numpy as np
    if result.masks is None:
        return np.zeros((0,) + tuple(result.orig_shape), dtype=np.uint8)
    data = result.masks.data
    try:
        data = data.cpu().numpy()
    except AttributeError:
        data = np.asarray(data)
    data = (data > 0.5).astype(np.uint8)
    h, w = result.orig_shape[:2]
    if data.shape[1:] != (h, w):
        import cv2
        data = np.stack([cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST) for m in data]) \
            if len(data) else np.zeros((0, h, w), dtype=np.uint8)
    return data


# ----------------------------------------------------------------------
# Backend locali (ultralytics)
# ----------------------------------------------------------------------
def run_sam2(image, weights, mode, prompts, conf, imgsz, device, min_area, simplify):
    from ultralytics import SAM
    import numpy as np

    say(f"carico {os.path.basename(weights)} su {device}")
    model = SAM(weights)
    kwargs = dict(conf=conf, imgsz=imgsz, device=device, verbose=False)

    def predict(**extra):
        try:
            return model(image, **kwargs, **extra)
        except Exception as e:          # noqa: BLE001 - MPS a volte non regge: si ricade su CPU
            if device != "cpu":
                say(f"{device} ha fallito ({str(e)[:80]}), riprovo su CPU")
                kwargs["device"] = "cpu"
                return model(image, **kwargs, **extra)
            raise

    say("segmento")
    if mode == "points":
        pts = prompts.get("points") or []
        lbl = prompts.get("labels") or [1] * len(pts)
        if not pts:
            raise SystemExit("modo punti senza punti")
        masks, scores = [], []
        for p, l in zip(pts, lbl):          # un oggetto per punto
            res = predict(points=[[float(p[0]), float(p[1])]], labels=[int(l)])
            arr = _masks_array(res[0])
            for k, m in enumerate(arr):
                masks.append(m)
                scores.append(_score(res[0], k))
        masks = np.stack(masks) if masks else np.zeros((0,) + image.shape[:2], dtype=np.uint8)
        return masks_to_polygons(masks, scores, None, min_area, simplify)
    if mode == "boxes":
        boxes = prompts.get("boxes") or []
        if not boxes:
            raise SystemExit("modo riquadri senza riquadri")
        res = predict(bboxes=[[float(v) for v in b] for b in boxes])
        arr = _masks_array(res[0])
        scores = [_score(res[0], k) for k in range(len(arr))]
        return masks_to_polygons(arr, scores, None, min_area, simplify)
    res = predict()
    arr = _masks_array(res[0])
    scores = [_score(res[0], k) for k in range(len(arr))]
    return masks_to_polygons(arr, scores, None, min_area, simplify)


def _score(result, k):
    try:
        return float(result.boxes.conf[k])
    except Exception:       # noqa: BLE001
        return None


def run_yoloe(image, weights, classes, conf, imgsz, device, min_area, simplify):
    from ultralytics import YOLOE

    if not classes:
        raise SystemExit("YOLOE vuole almeno una classe (--classes)")
    say(f"carico {os.path.basename(weights)} su {device}; classi: {', '.join(classes)}")
    model = YOLOE(weights)
    try:
        model.set_classes(classes, model.get_text_pe(classes))
    except TypeError:
        model.set_classes(classes)
    say("segmento")
    try:
        res = model.predict(image, conf=conf, imgsz=imgsz, device=device, retina_masks=True, verbose=False)
    except Exception as e:              # noqa: BLE001
        if device == "cpu":
            raise
        say(f"{device} ha fallito ({str(e)[:80]}), riprovo su CPU")
        res = model.predict(image, conf=conf, imgsz=imgsz, device="cpu", retina_masks=True, verbose=False)
    r = res[0]
    arr = _masks_array(r)
    names = r.names if isinstance(r.names, dict) else dict(enumerate(r.names))
    labels, scores = [], []
    for k in range(len(arr)):
        try:
            cls = int(r.boxes.cls[k])
            labels.append(names.get(cls, classes[cls] if cls < len(classes) else str(cls)))
            scores.append(float(r.boxes.conf[k]))
        except Exception:   # noqa: BLE001
            labels.append(None)
            scores.append(None)
    return masks_to_polygons(arr, scores, labels, min_area, simplify)


# ----------------------------------------------------------------------
# Backend cloud
# ----------------------------------------------------------------------
def _image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def run_replicate(image_path, api_key, conf, min_area, simplify, points_per_side=32):
    """Replicate `meta/sam-2`: maschere automatiche come PNG da scaricare."""
    import requests
    import numpy as np
    import cv2

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Prefer": "wait=60"}
    payload = {"input": {"image": "data:image/png;base64," + _image_b64(image_path),
                         "points_per_side": int(points_per_side),
                         "pred_iou_thresh": 0.88, "stability_score_thresh": 0.95, "use_m2m": True}}
    say("invio a Replicate (meta/sam-2)")
    r = requests.post("https://api.replicate.com/v1/models/meta/sam-2/predictions",
                      headers=headers, json=payload, timeout=120)
    if r.status_code >= 400:
        raise SystemExit(f"Replicate: HTTP {r.status_code} {r.text[:300]}")
    pred = r.json()
    poll = (pred.get("urls") or {}).get("get")
    deadline = time.time() + 900
    while pred.get("status") not in ("succeeded", "failed", "canceled"):
        if not poll or time.time() > deadline:
            raise SystemExit("Replicate: tempo scaduto")
        time.sleep(3)
        pred = requests.get(poll, headers=headers, timeout=60).json()
        say(f"Replicate: {pred.get('status')}")
    if pred.get("status") != "succeeded":
        raise SystemExit(f"Replicate: {pred.get('status')} {pred.get('error') or ''}")
    out = pred.get("output") or {}
    if isinstance(out, dict):
        urls = out.get("individual_masks") or ([out["combined_mask"]] if out.get("combined_mask") else [])
    elif isinstance(out, list):
        urls = out
    else:
        urls = [out]
    say(f"scarico {len(urls)} maschere")
    masks = []
    for u in urls:
        data = requests.get(u, timeout=120).content
        arr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
        if arr is not None:
            masks.append((arr > MASK_THRESHOLD).astype(np.uint8))
    return masks_to_polygons(masks, None, None, min_area, simplify)


def run_roboflow(image_path, api_key, classes, conf, min_area):
    """Roboflow SAM 3 `concept_segment`: prompt testuali, poligoni in risposta."""
    import requests

    if not classes:
        raise SystemExit("SAM 3 vuole almeno una classe (--classes)")
    payload = {"image": {"type": "base64", "value": _image_b64(image_path)},
               "prompts": [{"type": "text", "text": c} for c in classes[:16]],
               "output_prob_thresh": float(conf), "format": "polygon"}
    say(f"invio a Roboflow SAM 3: {', '.join(classes[:16])}")
    r = requests.post("https://serverless.roboflow.com/sam3/concept_segment",
                      headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=300)
    if r.status_code >= 400:
        raise SystemExit(f"Roboflow: HTTP {r.status_code} {r.text[:300]}")
    data = r.json()
    rings, scores, labels = [], [], []
    for pr in data.get("prompt_results") or []:
        label = (pr.get("echo") or {}).get("text")
        for p in pr.get("predictions") or []:
            for ring in p.get("masks") or []:
                rings.append(ring)
                scores.append(p.get("confidence"))
                labels.append(label)
    return rings_to_polygons(rings, scores, labels, min_area)


# ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--image", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--backend", required=True, choices=("sam2", "yoloe", "replicate", "roboflow"))
    ap.add_argument("--weights", default=None)
    ap.add_argument("--mode", default="auto", choices=("auto", "points", "boxes"))
    ap.add_argument("--prompts", default=None, help="file JSON con points/labels/boxes (pixel)")
    ap.add_argument("--classes", default="", help="classi a testo, separate da virgola")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--imgsz", type=int, default=1024)
    ap.add_argument("--min-area", type=float, default=20.0, help="area minima in pixel")
    ap.add_argument("--simplify", type=float, default=1.0, help="tolleranza Douglas-Peucker in pixel")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--api-key", default=None)
    args = ap.parse_args(argv)

    prompts = {}
    if args.prompts:
        with open(args.prompts, encoding="utf-8") as f:
            prompts = json.load(f)
    classes = parse_classes(args.classes)
    warnings = []
    t0 = time.time()

    if args.backend in ("sam2", "yoloe"):
        if not args.weights or not os.path.isfile(args.weights):
            raise SystemExit(f"pesi mancanti: {args.weights}")
        image = load_image(args.image)
        device = pick_device(args.device)
        if args.backend == "sam2":
            polygons = run_sam2(image, args.weights, args.mode, prompts, args.conf, args.imgsz, device,
                                args.min_area, args.simplify)
        else:
            polygons = run_yoloe(image, args.weights, classes, args.conf, args.imgsz, device,
                                 args.min_area, args.simplify)
        h, w = image.shape[:2]
        model = os.path.basename(args.weights)
    else:
        if not args.api_key:
            raise SystemExit("serve la chiave API (--api-key)")
        import cv2
        img = cv2.imread(args.image)
        if img is None:
            raise SystemExit(f"non leggo l'immagine {args.image}")
        h, w = img.shape[:2]
        if args.backend == "replicate":
            if args.mode != "auto":
                warnings.append("Replicate SAM-2: solo il modo automatico; punti e riquadri ignorati")
            polygons = run_replicate(args.image, args.api_key, args.conf, args.min_area, args.simplify)
            model = "replicate:meta/sam-2"
        else:
            polygons = run_roboflow(args.image, args.api_key, classes, args.conf, args.min_area)
            model = "roboflow:sam3"

    result = {"backend": args.backend, "model": model, "image": {"path": args.image, "width": w, "height": h},
              "classes": classes, "polygons": polygons, "warnings": warnings,
              "seconds": round(time.time() - t0, 2)}
    tmp = args.output + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f)
    os.replace(tmp, args.output)
    say(f"{len(polygons)} poligoni in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
