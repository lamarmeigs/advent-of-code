import argparse
import dataclasses
import itertools

import z3


@dataclasses.dataclass
class Schematic:
    lights: list[bool]
    buttons: list[tuple[int]]
    joltage: list[int]

    @classmethod
    def from_raw(cls, raw_line: str):
        buttons = []
        for data in raw_line.split():
            if data.startswith("["):
                lights = [light == "#" for light in data.strip("[]")]
            elif data.startswith("("):
                light_indexes = tuple([int(i) for i in data.strip("()").split(",")])
                buttons.append(light_indexes)
            elif data.startswith("{"):
                joltage = [int(j) for j in data.strip("{}").split(",")]
        return cls(lights, buttons, joltage)

    def get_minimal_light_init(self) -> list[tuple[int]]:
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

    def get_minimal_joltage_init(self):
        solver = z3.Optimize()

        button_presses = z3.IntVector("button_presses", len(self.buttons))
        for button_index in range(len(self.buttons)):
            solver.add(button_presses[button_index] >= 0)

        for joltage_index, joltage in enumerate(self.joltage):
            buttons = [
                button_index
                for button_index, button in enumerate(self.buttons)
                if joltage_index in button
            ]
            solver.add(sum(button_presses[button] for button in buttons) == joltage)

        presses = z3.Sum(button_presses)
        solver.minimize(presses)
        solver.check()
        return solver.model().eval(presses).as_long()

    def get_minimal_joltage_init_with_matrices(self):
        """DOES NOT WORK"""
        matrix = self.as_matrix()

        # No free variables: press each button enough to obtain a whole joltage
        if not (free_variables := matrix.free_variables):
            presses = 0
            for pivot in matrix.pivots:
                joltage_per_press = matrix.results[pivot[0]]
                if joltage_per_press != 0:
                    presses += int(joltage_per_press * (1 / joltage_per_press))
            return presses

        free_variable_guesses = []
        for free_variable in free_variables:
            button = self.buttons[free_variable]
            max_presses = min(self.joltage[joltage_index] for joltage_index in button)
            free_variable_guesses.append(range(0, max_presses + 1))

        fewest_presses = float('inf')
        for guesses in itertools.product(*free_variable_guesses):
            sum_ = sum(guesses)
            is_valid = True
            for _, equation in matrix.equations:
                button_presses = eval(equation)
                if button_presses < 0 or round(button_presses) != button_presses:
                    is_valid = False
                    break
                else:
                    sum_ += button_presses
            if is_valid:
                fewest_presses = min(fewest_presses, sum_)
        return fewest_presses

    def as_matrix(self):
        columns = []
        for button in self.buttons:
            column = [1 if i in button else 0 for i in range(len(self.joltage))]
            columns.append(column)
        return EnhancedMatrix(
            [list(row) for row in zip(*columns)],
            self.joltage[:],
        )


@dataclasses.dataclass
class EnhancedMatrix:
    coefficients: list[list[int]]
    results: list[int]
    equations: list[tuple[int, str]] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.to_rref()
        self._derive_equations()

    @property
    def pivots(self) -> tuple[int, int]:
        """Return the coordinates for the leading number in each row."""
        pivots = []
        for i, row in enumerate(self.coefficients):
            j = 0
            try:
                while row[j] == 0:
                    j += 1
            except IndexError:
                break
            pivots.append((i, j))
        return pivots

    @property
    def free_variables(self) -> list[int]:
        """Return the indices of columns without a pivot value."""
        pivot_columns = set(pivot[1] for pivot in self.pivots)
        return set(range(len(self.coefficients[0]))) - pivot_columns

    def to_rref(self):
        """Transform matrix into Reduced Row-Echelon Form."""
        # Ensure non-zero values exist along the (rough) diagonal by swapping
        # subsequent rows. These will be the pivots.
        min_pivot = 0
        row_index = 0
        while row_index < len(self.coefficients) and min_pivot < len(self.coefficients[0]):
            while (
                min_pivot < len(self.coefficients[0])
                and self.coefficients[row_index][min_pivot] == 0
            ):
                candidates = [
                    later_row_index
                    for later_row_index in range(row_index + 1, len(self.coefficients))
                    if self.coefficients[later_row_index][min_pivot] != 0
                ]
                if candidates:
                    self._swap_rows(row_index, candidates[0])
                else:
                    min_pivot += 1

            if min_pivot >= len(self.coefficients[0]):
                break

            # Reduce the pivot to 1
            if self.coefficients[row_index][min_pivot] != 1:
                self._multiply_row(
                    row_index,
                    1 / self.coefficients[row_index][min_pivot],
                )

            # Eliminate non-zero values beneath the new pivot by subtracting rows.
            for later_row_index in range(row_index + 1, len(self.coefficients)):
                number_below_pivot = self.coefficients[later_row_index][min_pivot]
                if number_below_pivot != 0:
                    self._add_by_row(
                        later_row_index,
                        row_index,
                        -(number_below_pivot / self.coefficients[row_index][min_pivot]),
                    )
            min_pivot += 1
            row_index += 1

        # Eliminate non-zero values above each pivot by subtracting rows.
        for pivot in sorted(self.pivots, reverse=True):
            row_index = pivot[0]
            for earlier_row_index in range(row_index - 1, -1, -1):
                number_above_pivot = self.coefficients[earlier_row_index][pivot[1]]
                if number_above_pivot != 0:
                    self._add_by_row(
                        earlier_row_index,
                        row_index,
                        -(number_above_pivot / self.coefficients[pivot[0]][pivot[1]]),
                    )

    def _swap_rows(self, row_1: int, row_2: int):
        tmp = self.coefficients[row_1]
        self.coefficients[row_1] = self.coefficients[row_2]
        self.coefficients[row_2] = tmp

        tmp = self.results[row_1]
        self.results[row_1] = self.results[row_2]
        self.results[row_2] = tmp

    def _add_by_row(self, row_1: int, row_2: int, scalar: int | float):
        for i in range(len(self.coefficients[row_1])):
            self.coefficients[row_1][i] += self.coefficients[row_2][i] * scalar
            self.coefficients[row_1][i] += round(self.coefficients[row_1][i], 6)
        self.results[row_1] += self.results[row_2] * scalar
        self.results[row_1] = round(self.results[row_1], 6)

    def _multiply_row(self, row: int, scalar: int | float):
        for i in range(len(self.coefficients[row])):
            self.coefficients[row][i] *= scalar
            self.coefficients[row][i] = round(self.coefficients[row][i], 6)
        self.results[row] *= scalar
        self.results[row] = round(self.results[row], 6)

    def _derive_equations(self):
        """Format arithmetic necessary to solve for dependent variables."""
        pivots = self.pivots
        free_variables = self.free_variables
        for pivot in pivots:
            equation = f"{self.results[pivot[0]]}"
            for i, free_variable in enumerate(free_variables):
                coefficient = self.coefficients[pivot[0]][free_variable]
                equation += f" - ({coefficient} * guesses[{i}])"
            self.equations.append((pivot[1], equation))

    def __str__(self):
        rows = []
        for row, result in zip(self.coefficients, self.results):
            coefficients = "".join(f"{str(c):5s}" for c in row)
            rows.append(f"{coefficients} | {result}")
        return "\n".join(rows)


def _parse_file(filename: str):
    with open(filename) as f:
        lines = f.readlines()
    return [Schematic.from_raw(line) for line in lines]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    schematics = _parse_file(args.filename)
    result = sum(len(schematic.get_minimal_light_init()) for schematic in schematics)
    print(f"Fewest button presses to initialize all machine lights: {result}")

    result = sum(schematic.get_minimal_joltage_init() for schematic in schematics)
    print(f"Fewest button presses to initialize all joltages: {result}")
