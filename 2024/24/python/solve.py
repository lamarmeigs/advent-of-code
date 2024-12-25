import argparse
import dataclasses
import re
import typing


@dataclasses.dataclass
class Wire:
    value: int = None
    source: "Gate" = None


@dataclasses.dataclass
class Gate:
    operator: typing.Literal["AND", "OR", "XOR"]
    input1: str
    input2: str
    output: str


def _parse_file(filename: str) -> dict[str, list[str]]:
    with open(filename, "r") as f:
        raw = f.read().strip()
    return _build_circuit(*raw.split('\n\n'))


def _build_circuit(raw_wires: str, raw_gates: str) -> dict[str, Wire]:
    wires = {}
    wire_pattern = r"(?P<id>[\S\d]{3}): (?P<value>\d)"
    for raw_wire in raw_wires.split('\n'):
        if match := re.search(wire_pattern, raw_wire):
            wires[match.group("id")] = Wire(int(match.group("value")), None)

    gate_pattern = (
        r"(?P<input1>[\S\d]{3}) (?P<op>(AND|OR|XOR)) (?P<input2>[\S\d]{3}) "
        r"-> (?P<output>[\S\d]{3})"
    )
    for raw_gate in raw_gates.split("\n"):
        if match := re.search(gate_pattern, raw_gate):
            gate = Gate(
                match.group("op"),
                match.group("input1"),
                match.group("input2"),
                match.group("output"),
            )
            wire = wires.get(gate.output, Wire(None, gate))
            wire.source = gate
            wires[gate.output] = wire
    return wires


def _run_circuit(wires: dict[str, Wire]):
    def _evaluate_wire(wire: Wire):
        if wire.value is not None:
            return

        gate = wire.source
        if (input1 := wires[gate.input1]).value is None:
            _evaluate_wire(input1)
        if (input2 := wires[gate.input2]).value is None:
            _evaluate_wire(input2)

        match gate.operator:
            case 'AND':
                result = input1.value & input2.value
            case 'OR':
                result = input1.value | input2.value
            case 'XOR':
                result = input1.value ^ input2.value

        wire.value = result

    for wire in wires.values():
        _evaluate_wire(wire)


def _extract_labelled(wires: dict[str, Wire], label: str) -> str:
    labelled_wires = sorted((key for key in wires if key.startswith(label)), reverse=True)
    return ''.join(str(wires[key].value) for key in labelled_wires)


def _find_incorrect_wires(wires: dict[str, Wire]):
    gates = {}
    for wire_id, wire in wires.items():
        if gate := wire.source:
            gates[wire_id] = (gate.input1, gate.operator, gate.input2)

    problem_wires = set()
    for output, (input1, operator, input2) in gates.items():
        if output.startswith("z") and not output.endswith(("z00", "z45")) and operator != "XOR":
            problem_wires.add(output)

        elif (
            operator == "XOR"
            and not input1.startswith(("x", "y", "z"))
            and not input2.startswith(("x", "y", "z"))
            and not output.startswith(("x", "y", "z"))
        ):
            problem_wires.add(output)

        elif (
            operator == "AND"
            and "x00" not in (input1, input2)
            and any(
                output in (sub_input1, sub_input2) and sub_operator != "OR"
                for sub_input1, sub_operator, sub_input2 in gates.values()
            )
        ):
            problem_wires.add(output)

        elif operator == "XOR" and any(
            output in (sub_input1, sub_input2) and sub_operator == "OR"
            for sub_input1, sub_operator, sub_input2 in gates.values()
        ):
            problem_wires.add(output)

    return problem_wires


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    wires = _parse_file(args.filename)
    _run_circuit(wires)
    circuit_output = _extract_labelled(wires, "z")
    print(f"Circuit output: {int(circuit_output, 2)}")

    bad_wires = _find_incorrect_wires(wires)
    print(f"Swapped output wires: {','.join(sorted(list(bad_wires)))}")
