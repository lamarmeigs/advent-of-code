import argparse
import dataclasses
import itertools
import typing

Position: typing.TypeAlias = tuple[int, int]


def _parse_file(filename: str) -> list[str]:
    with open(filename, "r") as f:
        raw = f.read().strip()

    return raw.split('\n')


@dataclasses.dataclass
class KeypadRobot:
    rows: list[str]
    position: Position
    next_robot: 'KeypadRobot' = None

    def _get_coordinates(self, button: str) -> Position:
        for i, row in enumerate(self.rows):
            if button in row:
                return (i, row.index(button))
        raise ValueError(f"Button {button} not present on keypad")

    def press(self, button: str) -> list[str]:
        if self.next_robot:
            buttons = self.next_robot.press(button)
            directions = []
            for button in buttons:
                directions.extend(self._press(button))
        else:
            directions = self._press(button)
        return ''.join(directions)

    def _press(self, button: str) -> list[str]:
        target = self._get_coordinates(button)
        blank = self._get_coordinates(' ')

        row_diff = target[0] - self.position[0]
        row_direction = 'v' if row_diff > 0 else '^'
        row_moves = [row_direction] * abs(row_diff)

        column_diff = target[1] - self.position[1]
        column_direction = '>' if column_diff > 0 else '<'
        column_moves = [column_direction] * abs(column_diff)

        # If the blank space is in the way, avoid it. Otherwise, prioritze
        # directions furthest from A (ie. "<"), performing only a single turn.
        if blank[0] == self.position[0] and blank[1] == target[1]:
            directions = row_moves + column_moves
        elif blank[0] == target[0] and blank[1] == self.position[1]:
            directions = column_moves + row_moves
        else:
            if column_direction == "<":
                directions = column_moves + row_moves
            else:
                directions = row_moves + column_moves
        directions.append("A")

        self.position = target
        return directions


@dataclasses.dataclass
class NumericKeypadRobot(KeypadRobot):
    rows: list[str] = dataclasses.field(default_factory=lambda: ['789', '456', '123', ' 0A'])
    position: Position = (3, 2)


@dataclasses.dataclass
class DirectionalKeypadRobot(KeypadRobot):
    rows: list[str] = dataclasses.field(default_factory=lambda: [' ^A', '<v>'])
    position: Position = (0, 2)


def _calculate_complexity(code: str, directions: str) -> int:
    return len(directions) * int(code.rstrip('A'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    robot_1 = NumericKeypadRobot()
    robot_2 = DirectionalKeypadRobot(next_robot=robot_1)
    robot_3 = DirectionalKeypadRobot(next_robot=robot_2)

    codes = _parse_file(args.filename)
    directions = {
        code: ''.join(itertools.chain.from_iterable(robot_3.press(button) for button in code))
        for code in codes
    }
    complexities = sum(
        _calculate_complexity(code, directions) for code, directions in directions.items()
    )
    print(f"Sum of code complexities: {complexities}")
