from modules.utility.rapporti_check import regenerate_node_uuids


class _N:
    def __init__(self, nid, uuid):
        self.node_id = nid
        self.attributes = {"node_uuid": uuid}


class _G:
    def __init__(self, nodes):
        self.nodes = nodes


def test_regenerate_node_uuids_replaces_all_and_is_unique():
    g = _G([_N("a", "old-1"), _N("b", "old-2"), _N("c", None)])
    regenerate_node_uuids(g)
    uuids = [n.attributes.get("node_uuid") for n in g.nodes]
    assert all(u and not u.startswith("old-") for u in uuids)
    assert len(set(uuids)) == 3
