import argparse
import copy
import dataclasses
import enum


class LoopError(Exception):
    ...

class Direction(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'

    @classmethod
    def horizontals(cls):
        return {cls.LEFT, cls.RIGHT}

    @classmethod
    def verticals(cls):
        return {cls.UP, cls.DOWN}


@dataclasses.dataclass
class Position:
    row: int
    column: int
    visited_directions: set[Direction] = dataclasses.field(default_factory=set)
    obstructed: bool = False
    test: bool = False

    @property
    def visited(self):
        return bool(self.visited_directions)

    def __str__(self):
        if (
            self.visited_directions.intersection(Direction.verticals())
            and self.visited_directions.intersection(Direction.horizontals())
        ):
            c = '+'
        elif self.visited_directions.intersection(Direction.verticals()):
            c = '|'
        elif self.visited_directions.intersection(Direction.horizontals()):
            c = '-'
        elif self.obstructed and self.test:
            c = 'O'
        elif self.obstructed:
            c = '#'
        else:
            c = '.'
        return c


@dataclasses.dataclass
class Guard:
    row: int
    column: int
    facing: Direction

    def __str__(self):
        match self.facing:
            case Direction.UP:
                c = '^'
            case Direction.RIGHT:
                c = '>'
            case Direction.DOWN:
                c = 'v'
            case Direction.LEFT:
                c = '<'
        return c

    def turn_right(self):
        match self.facing:
            case Direction.UP:
                self.facing = Direction.RIGHT
            case Direction.RIGHT:
                self.facing = Direction.DOWN
            case Direction.DOWN:
                self.facing = Direction.LEFT
            case Direction.LEFT:
                self.facing = Direction.UP


class Map:
    grid: list[list[Position]]
    guard: Guard

    def __init__(self, raw_grid: str):
        self.grid = []
        self.guard = None
        self.reset(raw_grid)

    def reset(self, raw_grid: str):
        self.grid = []
        for row_index, raw_row in enumerate(raw_grid.split()):
            row = []
            for column_index, raw_position in enumerate(raw_row):
                if is_guard := (raw_position.lower() in ('^', '>', '<', 'v')):
                    match raw_position:
                        case '^':
                            direction = Direction.UP
                        case '>':
                            direction = Direction.RIGHT
                        case 'v':
                            direction = Direction.DOWN
                        case '<':
                            direction = Direction.LEFT
                    self.guard = Guard(
                        row=row_index,
                        column=column_index,
                        facing=direction,
                    )
                position = Position(
                    row=row_index,
                    column=column_index,
                    visited_directions={self.guard.facing} if is_guard else set(),
                    obstructed=raw_position == '#'
                )
                row.append(position)
            self.grid.append(row)

    def __getitem__(self, key):
        return self.grid.__getitem__(key)

    def __str__(self):
        rendered_rows = []
        for row in self.grid:
            rendered_row = [str(position) for position in row]
            rendered_rows.append(rendered_row)

        if self.guard:
            rendered_rows[self.guard.row][self.guard.column] = str(self.guard)

        return '\n'.join(''.join(row) for row in rendered_rows)

    def play(self):
        while self.step():
            pass

    def step(self) -> bool:
        if not self.guard:
            return False

        next_position = self.get_guard_next_position()
        if next_position is None:
            self.guard = None
        elif next_position.obstructed:
            self.guard.turn_right()
            self.grid[self.guard.row][self.guard.column].visited_directions.add(self.guard.facing)
        else:
            self.guard.row = next_position.row
            self.guard.column = next_position.column
            if self.guard.facing in next_position.visited_directions:
                raise LoopError()
            next_position.visited_directions.add(self.guard.facing)

        return True

    def get_guard_next_position(self):
        if not self.guard:
            return None

        row_delta = 0
        column_delta = 0
        match self.guard.facing:
            case Direction.UP:
                row_delta = -1
            case Direction.RIGHT:
                column_delta = 1
            case Direction.DOWN:
                row_delta = 1
            case Direction.LEFT:
                column_delta = -1

        next_row = self.guard.row + row_delta
        next_column = self.guard.column + column_delta
        if (
            next_row < 0
            or next_row >= len(self.grid)
            or next_column < 0
            or next_column >= len(self.grid[next_row])
        ):
            next_position = None
        else:
            next_position = self.grid[self.guard.row + row_delta][self.guard.column + column_delta]
        return next_position


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw_grid = f.read()
    return raw_grid


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    raw_map = _parse_file(args.filename)
    map_ = Map(raw_map)
    map_.play()

    visited_positions = len(
        [
            position
            for row in map_.grid
            for position in row
            if position.visited
        ]
    )
    print(f'Number of visited positions: {visited_positions}')

    map_.reset(raw_map)
    obstructions_causing_loops = []
    changed = True
    step = 0
    while changed:
        if args.verbose:
            print(f"Step {step}/{visited_positions-1}")
        trial_map = copy.deepcopy(map_)

        if not (next_position := trial_map.get_guard_next_position()):
            break
        elif not (next_position.obstructed or next_position.visited):
            next_position.obstructed = True
            next_position.test = True
            try:
                trial_map.play()
            except LoopError:
                obstructions_causing_loops.append(next_position)

        changed = map_.step()
        step += 1

    print(f'Number of potential loop-causing obstructions: {len(obstructions_causing_loops)}')
