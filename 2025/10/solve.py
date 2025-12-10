import argparse
import dataclasses


@dataclasses.dataclass
class Schematic:
    lights: list[bool]
    buttons: list[tuple[int]]
    joltages: list[int]

    def __init__(self, raw_line: str):
        self.buttons = []
        for data in raw_line.split():
            if data.startswith("["):
                self.lights = [light == "#" for light in data.strip("[]")]
            elif data.startswith("("):
                light_indexes = tuple([int(i) for i in data.strip("()").split(",")])
                self.buttons.append(light_indexes)
            elif data.startswith("{"):
                self.joltages = [int(j) for j in data.strip("{}").split(",")]

    def get_minimal_init(self) -> list[list[int]]:
        def _toggle_lights(lights: list[bool], indexes: list[int]) -> list[bool]:
            toggled = lights[:]
            for index in indexes:
                toggled[index] = not lights[index]
            return toggled

        # Create initial sequences
        sequences = []
        initial_lights = [False for _ in range(len(self.lights))]
        for button in self.buttons:
            lights = _toggle_lights(initial_lights, button)
            if lights == self.lights:
                return [button]
            sequence = ([button], lights)
            sequences.append(sequence)

        # Continue until a solution is found
        while True:
            current_sequence, current_lights = sequences.pop(0)
            for button in self.buttons:
                if button == current_sequence[-1]:
                    continue
                new_sequence = current_sequence + [button]
                lights = _toggle_lights(current_lights, button)
                if lights == self.lights:
                    return new_sequence
                sequences.append((new_sequence, lights))


def _parse_file(filename: str):
    with open(filename) as f:
        lines = f.readlines()
    return [Schematic(line) for line in lines]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    schematics = _parse_file(args.filename)
    result = sum(len(schematic.get_minimal_init()) for schematic in schematics)
    print(f"Fewest button presses to initialize all machines: {result}")
