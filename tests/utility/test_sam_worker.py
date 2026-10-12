"""SAM: il worker esterno, nelle parti che non vogliono torch — 2026-10-12.

`scripts/sam_worker.py` gira nel venv; qui si provano con numpy e OpenCV di
QGIS le funzioni pure: classi dal testo, maschere -> poligoni con i buchi,
anelli dalle API cloud, e che lo script si importi senza ultralytics.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
cv2 = pytest.importorskip("cv2")

_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = _ROOT / "scripts" / "sam_worker.py"


@pytest.fixture(scope="module")
def worker():
    spec = importlib.util.spec_from_file_location("sam_worker", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)        # importabile senza ultralytics/torch
    return module


def test_parse_classes_pulisce_e_deduplica(worker):
    assert worker.parse_classes("building, road ,river;Road,, ") == ["building", "road", "river"]
    assert worker.parse_classes("") == []


def test_un_quadrato_con_un_buco_da_un_anello_e_un_buco(worker):
    mask = np.zeros((60, 80), dtype=np.uint8)
    mask[10:50, 10:70] = 1          # quadrato 60x40
    mask[25:35, 30:50] = 0          # buco 20x10
    polys = worker.masks_to_polygons([mask], scores=[0.9], labels=["building"], min_area=20, simplify=0.0)
    assert len(polys) == 1
    p = polys[0]
    assert p["label"] == "building" and p["score"] == 0.9
    assert len(p["holes"]) == 1
    xs = [pt[0] for pt in p["ring"]]
    ys = [pt[1] for pt in p["ring"]]
    # i vertici stanno al centro del pixel: 10.5 .. 69.5 in x, 10.5 .. 49.5 in y
    assert min(xs) == pytest.approx(10.5) and max(xs) == pytest.approx(69.5)
    assert min(ys) == pytest.approx(10.5) and max(ys) == pytest.approx(49.5)
    assert 2300 < p["area_px"] < 2400     # 59*39 - buco (OpenCV conta i bordi)


def test_le_maschere_piccole_e_vuote_sono_scartate(worker):
    empty = np.zeros((20, 20), dtype=np.uint8)
    tiny = np.zeros((20, 20), dtype=np.uint8)
    tiny[5:7, 5:7] = 1
    assert worker.masks_to_polygons([empty, tiny], min_area=20) == []


def test_due_pezzi_separati_sono_due_poligoni(worker):
    mask = np.zeros((30, 30), dtype=np.uint8)
    mask[2:12, 2:12] = 1
    mask[18:28, 18:28] = 1
    polys = worker.masks_to_polygons([mask], scores=[0.5], min_area=10)
    assert len(polys) == 2 and all(p["score"] == 0.5 for p in polys)


def test_la_semplificazione_riduce_i_vertici_di_un_cerchio(worker):
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (50, 50), 30, 1, -1)
    raw = worker.masks_to_polygons([mask], simplify=0.0)[0]
    simple = worker.masks_to_polygons([mask], simplify=2.0)[0]
    assert len(simple["ring"]) < len(raw["ring"]) / 2
    assert abs(simple["area_px"] - np.pi * 30 ** 2) / (np.pi * 30 ** 2) < 0.05


def test_gli_anelli_delle_api_cloud_tengono_etichetta_e_punteggio(worker):
    rings = [[[0, 0], [10, 0], [10, 10], [0, 10]], [[0, 0], [1, 0], [1, 1]]]
    polys = worker.rings_to_polygons(rings, scores=[0.8, 0.9], labels=["road", "road"], min_area=5)
    assert len(polys) == 1 and polys[0]["area_px"] == 100 and polys[0]["label"] == "road"


def test_main_senza_pesi_esce_con_errore_chiaro(worker, tmp_path):
    img = tmp_path / "a.png"
    cv2.imwrite(str(img), np.zeros((8, 8, 3), dtype=np.uint8))
    with pytest.raises(SystemExit) as e:
        worker.main(["--image", str(img), "--output", str(tmp_path / "o.json"), "--backend", "sam2",
                     "--weights", str(tmp_path / "nope.pt")])
    assert "pesi mancanti" in str(e.value)


def test_main_cloud_senza_chiave_esce_con_errore_chiaro(worker, tmp_path):
    img = tmp_path / "a.png"
    cv2.imwrite(str(img), np.zeros((8, 8, 3), dtype=np.uint8))
    with pytest.raises(SystemExit) as e:
        worker.main(["--image", str(img), "--output", str(tmp_path / "o.json"), "--backend", "roboflow",
                     "--classes", "stones"])
    assert "chiave API" in str(e.value)


def test_roboflow_legge_la_risposta_concept_segment(worker, tmp_path, monkeypatch):
    """La risposta documentata di `sam3/concept_segment` diventa poligoni etichettati."""
    img = tmp_path / "a.png"
    cv2.imwrite(str(img), np.zeros((8, 8, 3), dtype=np.uint8))
    risposta = {"prompt_results": [
        {"prompt_index": 0, "echo": {"type": "text", "text": "building"},
         "predictions": [{"format": "polygon", "confidence": 0.92,
                          "masks": [[[0, 0], [20, 0], [20, 20], [0, 20]]]}]},
        {"prompt_index": 1, "echo": {"type": "text", "text": "road"}, "predictions": []}]}
    visto = {}

    class Resp:
        status_code = 200
        text = ""

        def json(self):
            return risposta

    class Requests:
        @staticmethod
        def post(url, headers=None, json=None, timeout=None):
            visto.update(url=url, headers=headers, payload=json)
            return Resp()
    monkeypatch.setitem(sys.modules, "requests", Requests)
    polys = worker.run_roboflow(str(img), "KEY", ["building", "road"], 0.4, 10)
    assert visto["url"].endswith("/sam3/concept_segment")
    assert visto["headers"]["Authorization"] == "Bearer KEY"
    assert [p["type"] for p in visto["payload"]["prompts"]] == ["text", "text"]
    assert visto["payload"]["image"]["type"] == "base64" and visto["payload"]["format"] == "polygon"
    assert len(polys) == 1 and polys[0]["label"] == "building" and polys[0]["score"] == 0.92


def test_il_worker_tiene_sam2_a_1024_e_arrotonda_yoloe(worker):
    assert worker.SAM2_IMGSZ == 1024
    src = SCRIPT.read_text(encoding="utf-8")
    assert "imgsz=SAM2_IMGSZ" in src, "SAM 2 non deve ricevere l'imgsz dalla riga di comando"
    assert worker.yoloe_imgsz(1000, 800) == 1024 and worker.yoloe_imgsz(4000, 3000) == 1280
    assert worker.yoloe_imgsz(30, 20) == 64 and worker.yoloe_imgsz(1000, 800, max_side=640) == 640


def test_i_messaggi_del_worker_seguono_la_lingua(worker):
    assert worker.T("done", 3, 1.5) == "3 poligoni in 1.5 s"
    worker.LANG = "en"
    try:
        assert worker.T("done", 3, 1.5) == "3 polygons in 1.5 s"
        assert worker.T("load", "sam2.1_t.pt", "mps") == "loading sam2.1_t.pt on mps"
    finally:
        worker.LANG = "it"


def test_lang_dalla_riga_di_comando(worker, tmp_path):
    img = tmp_path / "a.png"
    cv2.imwrite(str(img), np.zeros((8, 8, 3), dtype=np.uint8))
    with pytest.raises(SystemExit) as e:
        worker.main(["--image", str(img), "--output", str(tmp_path / "o.json"), "--backend", "sam2",
                     "--weights", str(tmp_path / "nope.pt"), "--lang", "en"])
    assert "missing weights" in str(e.value)
    worker.LANG = "it"
