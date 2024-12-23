import argparse
import collections
import itertools


def _parse_file(filename: str) -> dict[str, list[str]]:
    with open(filename, "r") as f:
        raw = f.read()
    return _build_edges(raw.strip())


def _build_edges(raw_edges: str) -> dict[str, set[str]]:
    edges = collections.defaultdict(set)
    for edge in raw_edges.split('\n'):
        value_1, value_2 = edge.split('-')
        edges[value_1].add(value_2)
        edges[value_2].add(value_1)
    return edges


def _get_cliques(edges: dict[str, list[str]]) -> list[list[str]]:
    sets_of_3 = []
    for node, neighbors in edges.items():
        for neighbor_1, neighbor_2 in itertools.combinations(edges[node], 2):
            if neighbor_1 in edges[neighbor_2]:
                clique = sorted([node, neighbor_1, neighbor_2])
                if clique not in sets_of_3:
                    sets_of_3.append(clique)
    return sets_of_3


def _get_connected_components(edges: dict[str, list[str]]) -> list[set[str]]:
    components = []
    visited_nodes = set()
    for node, neighbors in edges.items():
        if node in visited_nodes:
            continue

        component = set([node])
        next_nodes = set(neighbors)
        while next_nodes:
            next_node = next_nodes.pop()
            next_neighbors = edges.get(next_node, [])
            for next_neighbor in next_neighbors:
                if component.issubset(edges[next_neighbor]):
                    component.add(next_neighbor)
                    next_nodes.update(edges[next_neighbor])

        visited_nodes.update(component)
        components.append(component)

    return components


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    edges = _parse_file(args.filename)
    cliques_3 = _get_cliques(edges)
    cliques_3_with_t = [
        clique for clique in cliques_3 if any(node.startswith('t') for node in clique)
    ]
    print(f"Sets of 3 with a 't' node: {len(cliques_3_with_t)}")

    components = _get_connected_components(edges)
    lan_party = max(components, key=len)
    password = ','.join(sorted(list(lan_party)))
    print(f"Password to LAN party: {password}")
