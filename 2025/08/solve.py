import argparse
import collections
import itertools
import math

JunctionBox = collections.namedtuple("JunctionBox", ["x", "y", "z"])


def _parse_file(filename: str) -> str:
    with open(filename) as f:
        lines = f.readlines()
    boxes = []
    for line in lines:
        x, y, z = line.split(",")
        box = JunctionBox(int(x), int(y), int(z))
        boxes.append(box)
    return boxes


def _get_distance(box_1: JunctionBox, box_2: JunctionBox) -> float:
    return math.sqrt(
        math.pow(box_1.x - box_2.x, 2)
        + math.pow(box_1.y - box_2.y, 2)
        + math.pow(box_1.z - box_2.z, 2)
    )


def _join_n_circuits(
    distances: dict[float, tuple[JunctionBox, JunctionBox]],
    count: int,
) -> list[set[JunctionBox]]:
    def _find_circuit(box: JunctionBox, circuits: list[set[JunctionBox]]) -> set[JunctionBox]:
        for circuit in circuits:
            if box in circuit:
                return circuit
        return None

    circuits = []
    nearest_distances = sorted(distances.keys())[:count]
    for distance in nearest_distances:
        box_1, box_2 = distances[distance]

        box_1_circuit = _find_circuit(box_1, circuits)
        box_2_circuit = _find_circuit(box_2, circuits)

        if not box_1_circuit and not box_2_circuit:
            circuits.append(set([box_1, box_2]))
        elif box_1_circuit and not box_2_circuit:
            box_1_circuit.add(box_2)
        elif not box_1_circuit and box_2_circuit:
            box_2_circuit.add(box_1)
        else:
            if box_1_circuit == box_2_circuit:
                continue
            box_1_circuit |= box_2_circuit
            circuits.remove(box_2_circuit)

    return circuits


def _join_all_boxes(
    distances: dict[float, tuple[JunctionBox, JunctionBox]],
    box_count: int,
) -> list[set[JunctionBox]]:
    def _find_circuit(box: JunctionBox, circuits: list[set[JunctionBox]]) -> set[JunctionBox]:
        for circuit in circuits:
            if box in circuit:
                return circuit
        return None

    circuits = []
    nearest_distances = sorted(distances.keys())
    for distance in nearest_distances:
        box_1, box_2 = distances[distance]

        box_1_circuit = _find_circuit(box_1, circuits)
        box_2_circuit = _find_circuit(box_2, circuits)

        if not box_1_circuit and not box_2_circuit:
            circuits.append(set([box_1, box_2]))
        elif box_1_circuit and not box_2_circuit:
            box_1_circuit.add(box_2)
        elif not box_1_circuit and box_2_circuit:
            box_2_circuit.add(box_1)
        else:
            if box_1_circuit == box_2_circuit:
                continue
            box_1_circuit |= box_2_circuit
            circuits.remove(box_2_circuit)

        if len(circuits) == 1 and len(circuits[0]) == box_count:
            break

    return box_1, box_2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    junction_boxes = _parse_file(args.filename)
    pairs = itertools.permutations(junction_boxes, 2)
    distances = {_get_distance(*pair): pair for pair in pairs}

    circuits = _join_n_circuits(distances, 1000)
    circuits.sort(key=len, reverse=True)
    result = len(circuits[0]) * len(circuits[1]) * len(circuits[2])
    print(f"Product of 3 largest circuits: {result}")

    box_1, box_2 = _join_all_boxes(distances, len(junction_boxes))
    print(f"Product of final connected boxes: {box_1.x * box_2.x}")
