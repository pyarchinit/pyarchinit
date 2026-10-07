"""yE-D Group A: L0 unit tests for yed_rapporti_policy module.

7 tests cover:
1. analyze_edges() against em_demo_02_mini fixture (real graphml).
2. SKIP policy drops folder-touching edges.
3. FAN_OUT explodes a folder->folder edge to N x M leaf pairs.
4. REPRESENTATIVE uses first member of each folder as proxy.
5. SYNTHETIC creates one VA row per unique folder + rewires edges.
6. SYNTHETIC handles folder->folder edges (2 VA rows + 1 rapporto).
7. Folder self-loops are filtered for ALL 4 policies.
"""
from __future__ import annotations

from pathlib import Path

from s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    ClassifiedNode,
    classify_leaves,
)
from s3dgraphy.sync.yed_group_walker import (
    FolderCandidate,
    walk_folders,
)
from s3dgraphy.sync.yed_rapporti_policy import (
    ExpandedRapporti,
    FolderEdge,
    FolderEdgePolicy,
    FolderEdgeReport,
    analyze_edges,
    apply_policy,
)


FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _leaf(yed_id: str, label: str = "") -> ClassifiedNode:
    return ClassifiedNode(
        yed_id=yed_id,
        label=label or yed_id,
        auto_kind=ClassificationKind.US_REAL,
        user_kind=ClassificationKind.US_REAL,
    )


def _folder(
    yed_id: str,
    label: str,
    *,
    members: list[str] | None = None,
    nested: list[str] | None = None,
    auto_dim: str | None = "attivita",
) -> FolderCandidate:
    return FolderCandidate(
        yed_id=yed_id,
        full_label=label,
        auto_dimension=auto_dim,
        user_dimension=auto_dim,
        auto_value=label.split("-")[0],
        user_value=label.split("-")[0],
        member_yed_ids=list(members or []),
        nested_folder_ids=list(nested or []),
        parent_folder_id=None,
    )


# ---------------------------------------------------------------------------
# Test 1 — analyze_edges against the real fixture
# ---------------------------------------------------------------------------

def test_analyze_edges_em_demo_02_mini_counts() -> None:
    """Mini fixture yields the known partition:
       5 edges total, 2 leaf-to-leaf, 3 folder-touching, 0 self-loops."""
    classified = classify_leaves(FIXTURE_PATH)
    folders = walk_folders(FIXTURE_PATH)

    report = analyze_edges(FIXTURE_PATH, classified, folders)

    assert report.total_edges == 5
    assert len(report.leaf_to_leaf) == 2
    assert len(report.folder_touching) == 3
    assert len(report.folder_self_loops) == 0

    # The two leaf-to-leaf edges are US01->US02 and USV101->US01.
    pairs = {(src, tgt) for src, tgt, _ in report.leaf_to_leaf}
    assert ("n0::n0::n0", "n0::n0::n1") in pairs
    assert ("n0::n0::n2", "n0::n0::n0") in pairs

    # One folder->folder edge exists.
    f2f = [
        fe for fe in report.folder_touching
        if fe.source_is_folder and fe.target_is_folder
    ]
    assert len(f2f) == 1
    assert f2f[0].source_id == "n0::n0"
    assert f2f[0].target_id == "n0::n1"


# ---------------------------------------------------------------------------
# Test 2 — SKIP drops folder-touching edges
# ---------------------------------------------------------------------------

def test_apply_skip_policy_drops_folder_edges() -> None:
    """SKIP keeps leaf-to-leaf only; folder-touching edges discarded."""
    leaf_to_leaf = [
        ("L1", "L2", None),
        ("L3", "L4", None),
    ]
    folder_touching = [
        FolderEdge("F1", "L1", True, False, None),
        FolderEdge("L4", "F2", False, True, None),
        FolderEdge("F1", "F2", True, True, None),
    ]
    report = FolderEdgeReport(
        total_edges=5,
        leaf_to_leaf=leaf_to_leaf,
        folder_touching=folder_touching,
    )

    result = apply_policy(
        report,
        FolderEdgePolicy.SKIP,
        all_folders=[
            _folder("F1", "VA01-a", members=["L1"]),
            _folder("F2", "AR01-b", members=["L4"]),
        ],
        classified=[_leaf("L1"), _leaf("L2"), _leaf("L3"), _leaf("L4")],
    )

    assert result.policy == FolderEdgePolicy.SKIP
    assert result.rapporti == leaf_to_leaf
    assert result.synthetic_us_rows == []


# ---------------------------------------------------------------------------
# Test 3 — FAN_OUT explodes N x M
# ---------------------------------------------------------------------------

def test_apply_fan_out_explodes_n_x_m() -> None:
    """FAN_OUT: F1(2 members) -> F2(3 members) yields 6 leaf pairs."""
    folder_touching = [
        FolderEdge("F1", "F2", True, True, None),
    ]
    report = FolderEdgeReport(
        total_edges=1,
        leaf_to_leaf=[],
        folder_touching=folder_touching,
    )

    f1 = _folder("F1", "VA01-x", members=["a1", "a2"])
    f2 = _folder("F2", "AR01-y", members=["b1", "b2", "b3"])

    result = apply_policy(
        report,
        FolderEdgePolicy.FAN_OUT,
        all_folders=[f1, f2],
        classified=[
            _leaf("a1"), _leaf("a2"),
            _leaf("b1"), _leaf("b2"), _leaf("b3"),
        ],
    )

    assert result.policy == FolderEdgePolicy.FAN_OUT
    assert len(result.rapporti) == 6
    pairs = {(s, t) for s, t, _ in result.rapporti}
    expected = {
        ("a1", "b1"), ("a1", "b2"), ("a1", "b3"),
        ("a2", "b1"), ("a2", "b2"), ("a2", "b3"),
    }
    assert pairs == expected
    assert result.synthetic_us_rows == []


# ---------------------------------------------------------------------------
# Test 4 — REPRESENTATIVE uses first member
# ---------------------------------------------------------------------------

def test_apply_representative_uses_first_member() -> None:
    """REPRESENTATIVE: folder endpoint resolves to its first member."""
    folder_touching = [
        # F1 -> L99 should become a1 -> L99
        FolderEdge("F1", "L99", True, False, None),
        # L88 -> F2 should become L88 -> b1
        FolderEdge("L88", "F2", False, True, None),
    ]
    report = FolderEdgeReport(
        total_edges=2,
        leaf_to_leaf=[],
        folder_touching=folder_touching,
    )

    f1 = _folder("F1", "VA01-x", members=["a1", "a2"])
    f2 = _folder("F2", "AR01-y", members=["b1", "b2"])

    result = apply_policy(
        report,
        FolderEdgePolicy.REPRESENTATIVE,
        all_folders=[f1, f2],
        classified=[
            _leaf("a1"), _leaf("a2"),
            _leaf("b1"), _leaf("b2"),
            _leaf("L88"), _leaf("L99"),
        ],
    )

    assert result.policy == FolderEdgePolicy.REPRESENTATIVE
    assert ("a1", "L99", None) in result.rapporti
    assert ("L88", "b1", None) in result.rapporti
    assert len(result.rapporti) == 2
    assert result.synthetic_us_rows == []


# ---------------------------------------------------------------------------
# Test 5 — SYNTHETIC creates VA rows for folder->leaf
# ---------------------------------------------------------------------------

def test_apply_synthetic_creates_va_rows() -> None:
    """SYNTHETIC on folder->leaf creates 1 VA anchor + rewires edge."""
    folder_touching = [
        FolderEdge("F1", "L99", True, False, None),
    ]
    report = FolderEdgeReport(
        total_edges=1,
        leaf_to_leaf=[],
        folder_touching=folder_touching,
    )

    f1 = _folder("F1", "VA01-foundation", members=["a1", "a2"])
    classified = [_leaf("a1"), _leaf("a2"), _leaf("L99")]

    result = apply_policy(
        report,
        FolderEdgePolicy.SYNTHETIC,
        all_folders=[f1],
        classified=classified,
    )

    assert result.policy == FolderEdgePolicy.SYNTHETIC
    assert len(result.synthetic_us_rows) == 1

    row = result.synthetic_us_rows[0]
    assert row["unita_tipo"] == "VA"
    assert row["us"] == "VA01-foundation"
    assert "node_uuid" in row
    assert row["_yed_folder_id"] == "F1"
    assert len(row["node_uuid"]) == 32  # hex form of uuid4

    # The folder F1 rapporto is rewired through the synthetic node_uuid.
    assert len(result.rapporti) == 1
    src, tgt, _et = result.rapporti[0]
    assert src == row["node_uuid"]
    assert tgt == "L99"


# ---------------------------------------------------------------------------
# Test 6 — SYNTHETIC with folder->folder edge: 2 VA rows + 1 rapporto
# ---------------------------------------------------------------------------

def test_apply_synthetic_with_folder_to_folder_edge() -> None:
    """SYNTHETIC on F1->F2 yields 2 VA rows + 1 rewired rapporto."""
    folder_touching = [
        FolderEdge("F1", "F2", True, True, None),
    ]
    report = FolderEdgeReport(
        total_edges=1,
        leaf_to_leaf=[],
        folder_touching=folder_touching,
    )

    f1 = _folder("F1", "VA01-x", members=["a1"])
    f2 = _folder("F2", "AR01-y", members=["b1"])

    result = apply_policy(
        report,
        FolderEdgePolicy.SYNTHETIC,
        all_folders=[f1, f2],
        classified=[_leaf("a1"), _leaf("b1")],
    )

    assert result.policy == FolderEdgePolicy.SYNTHETIC
    assert len(result.synthetic_us_rows) == 2

    by_folder = {
        r["_yed_folder_id"]: r for r in result.synthetic_us_rows
    }
    assert set(by_folder.keys()) == {"F1", "F2"}
    assert all(r["unita_tipo"] == "VA" for r in result.synthetic_us_rows)

    # Exactly one rapporto, connecting the two synthetic anchors.
    assert len(result.rapporti) == 1
    src, tgt, _ = result.rapporti[0]
    assert src == by_folder["F1"]["node_uuid"]
    assert tgt == by_folder["F2"]["node_uuid"]


# ---------------------------------------------------------------------------
# Test 7 — folder self-loops filtered for ALL 4 policies
# ---------------------------------------------------------------------------

def test_self_loop_folder_skipped_in_all_policies() -> None:
    """A FolderEdge with source==target on a folder yields zero rapporti
    under each of the 4 policies. Single test that loops all policies
    so pytest counts it once (matches spec § 5 line 198-206 budget)."""
    self_loop = FolderEdge("F1", "F1", True, True, None)
    # Report constructed by analyze_edges puts self-loops in their own
    # field. Here we test defensive handling: if a caller injects a
    # self-loop into folder_touching directly, apply_policy still drops
    # it under every policy.
    report = FolderEdgeReport(
        total_edges=1,
        leaf_to_leaf=[],
        folder_touching=[self_loop],
    )

    f1 = _folder("F1", "VA01-x", members=["a1", "a2"])
    classified = [_leaf("a1"), _leaf("a2")]

    for policy in (
        FolderEdgePolicy.SKIP,
        FolderEdgePolicy.FAN_OUT,
        FolderEdgePolicy.REPRESENTATIVE,
        FolderEdgePolicy.SYNTHETIC,
    ):
        result = apply_policy(
            report,
            policy,
            all_folders=[f1],
            classified=classified,
        )
        assert result.rapporti == [], (
            f"{policy.value}: expected empty rapporti, got {result.rapporti}"
        )
        # SYNTHETIC: our filter drops the self-loop before unique-folder
        # enumeration, so no VA row should be created either.
        assert result.synthetic_us_rows == [], (
            f"{policy.value}: expected no synthetic_us_rows"
        )
