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
