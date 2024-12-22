import argparse
import functools
import itertools
import typing

Position: typing.TypeAlias = tuple[int, int]


def _parse_file(filename: str) -> list[str]:
    with open(filename, "r") as f:
        raw = f.read().strip()

    return raw.split('\n')


def _prepopulate_paths(rows: list[str]):
    def _get_coordinates(button: str) -> Position:
        for i, row in enumerate(rows):
            if button in row:
                return (i, row.index(button))
        raise ValueError(f"Button {button} not present on keypad")

    def _get_path(start: Position, end: Position, blank: Position) -> str:
        row_diff = end[0] - start[0]
        row_direction = 'v' if row_diff > 0 else '^'
        row_moves = [row_direction] * abs(row_diff)

        column_diff = end[1] - start[1]
        column_direction = '>' if column_diff > 0 else '<'
        column_moves = [column_direction] * abs(column_diff)

        # If the blank space is in the way, avoid it. Otherwise, prioritze
        # directions furthest from A (ie. "<"), performing only a single turn.
        if blank[0] == start[0] and blank[1] == end[1]:
            directions = row_moves + column_moves
        elif blank[0] == end[0] and blank[1] == start[1]:
            directions = column_moves + row_moves
        else:
            if column_direction == "<":
                directions = column_moves + row_moves
            else:
                directions = row_moves + column_moves

        directions.append("A")
        return ''.join(directions)

    blank = _get_coordinates(' ')
    buttons = itertools.chain.from_iterable(rows)
    pairs = itertools.product(buttons, repeat=2)
    return {
        (start, end): _get_path(_get_coordinates(start), _get_coordinates(end), blank)
        for start, end in pairs
    }


NUMPAD_PATHS = _prepopulate_paths(['789', '456', '123', ' 0A'])
DIRPAD_PATHS = _prepopulate_paths([' ^A', '<v>'])


@functools.cache
def _press_keypad(code: str, depth: int, is_numpad_starter: bool = False) -> int:
    if depth == 0:
        return len(code)

    count = 0
    for start, end in itertools.pairwise('A' + code):
        paths = NUMPAD_PATHS if is_numpad_starter else DIRPAD_PATHS
        next_directions = paths[(start, end)]
        count += _press_keypad(next_directions, depth - 1)

    return count


def _calculate_complexity(code: str, directions_count: str) -> int:
    return directions_count * int(code.rstrip('A'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    codes = _parse_file(args.filename)
    direction_counts = {
        code: _press_keypad(code, depth=3, is_numpad_starter=True) for code in codes
    }
    complexities = sum(
        _calculate_complexity(code, count) for code, count in direction_counts.items()
    )
    print(f"Sum of code complexities with 3 keypads: {complexities}")

    direction_counts = {
        code: _press_keypad(code, depth=26, is_numpad_starter=True) for code in codes
    }
    complexities = sum(
        _calculate_complexity(code, count) for code, count in direction_counts.items()
    )
    print(f"Sum of code complexities with 26 keypads: {complexities}")
