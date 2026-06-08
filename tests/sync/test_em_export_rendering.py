import sys, xml.etree.ElementTree as ET
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TESTDB = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_test_em.sqlite"
N = "{http://graphml.graphdrawing.org/xmlns}"


def _export(tmp_path):
    if not Path(TESTDB).exists():
        pytest.skip("EM test DB absent")
    out = str(tmp_path / "em.graphml")
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(TESTDB, "pyarchinit_us_mapping", out,
                   site_filter="Sito_Test_EM")
    return ET.parse(out).getroot()


def _node_labels(root):
    labels = set()
    for n in root.iter(N + "node"):
        for tx in n.iter():
            if tx.tag.endswith("}NodeLabel") and tx.text and tx.text.strip():
                labels.add(tx.text.strip())
                break
    return labels


def test_paradata_labels_are_us_values(tmp_path):
    labels = _node_labels(_export(tmp_path))
    # paradata labelled by us code, NOT by description
    assert "D.1" in labels, labels
    assert "D.1.1" in labels, labels      # extractor
    assert "C.1" in labels, labels        # combiner
    assert not any(l in ("Documento", "Combiner", "Extractor", "Proprieta")
                   for l in labels), labels


def _edges(root):
    return [(e.get("source"), e.get("target")) for e in root.iter(N + "edge")]


def _node_degrees(root):
    import collections
    deg = collections.Counter()
    for s, t in _edges(root):
        deg[s] += 1
        deg[t] += 1
    # map id -> label
    id2lab = {}
    for nd in root.iter(N + "node"):
        for tx in nd.iter():
            if tx.tag.endswith("}NodeLabel") and tx.text and tx.text.strip():
                id2lab[nd.get("id")] = tx.text.strip()
                break
    return {id2lab.get(k, k): v for k, v in deg.items()}


def test_paradata_nodes_are_connected(tmp_path):
    deg = _node_degrees(_export(tmp_path))
    # combiner / extractor / a document must have at least one edge
    assert deg.get("C.1", 0) >= 1, deg
    assert deg.get("D.1.1", 0) >= 1, deg     # extractor
    assert deg.get("D.1", 0) >= 1, deg       # document
