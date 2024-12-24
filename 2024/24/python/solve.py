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
    operand: typing.Literal["AND", "OR", "XOR"]
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

        match gate.operand:
            case 'AND':
                result = input1.value & input2.value
            case 'OR':
                result = input1.value | input2.value
            case 'XOR':
                result = input1.value ^ input2.value

        wire.value = result

    for wire in wires.values():
        _evaluate_wire(wire)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    wires = _parse_file(args.filename)
    _run_circuit(wires)
    z_wire_values = [
        wires[key].value for key in sorted(key for key in wires if key.startswith("z"))
    ]
    circuit_output = int(''.join(str(d) for d in z_wire_values[::-1]), 2)
    print(f"Circuit output: {circuit_output}")
