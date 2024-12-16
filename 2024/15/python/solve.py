import argparse
import dataclasses


@dataclasses.dataclass
class Map:
    robot: tuple[int, int] = None
    grid: list[list[str]] = dataclasses.field(default_factory=list)

    def __init__(self, raw_map: str):
        self.grid = []
        for row_index, raw_row in enumerate(raw_map.split("\n")):
            row = list(raw_row)
            self.grid.append(row)
            if "@" in row:
                self.robot = (row_index, row.index("@"))

    def __str__(self):
        return "\n".join("".join(row) for row in self.grid)

    @property
    def height(self):
        return len(self.grid)

    @property
    def width(self):
        try:
            return len(self.grid[0])
        except IndexError:
            return 0

    def get_box_coordinates(self):
        for row_index, row in enumerate(self.grid):
            for column_index, position in enumerate(row):
                if position == "O":
                    yield 100 * row_index + column_index

    def move_robot(self, direction: str):
        self.robot = self._move_object(self.robot[0], self.robot[1], direction, prev=".")

    def _move_object(
        self,
        row: int,
        column: int,
        direction: str,
        prev: str,
    ) -> tuple[int, int]:
        match direction:
            case "<":
                neighbor_row = row
                neighbor_column = column - 1
            case "^":
                neighbor_row = row - 1
                neighbor_column = column
            case ">":
                neighbor_row = row
                neighbor_column = column + 1
            case "v":
                neighbor_row = row + 1
                neighbor_column = column

        if not (0 <= neighbor_row < self.height and 0 <= neighbor_column < self.width):
            return row, column

        neighbor = self.grid[neighbor_row][neighbor_column]
        if neighbor == "#":
            return row, column
        elif neighbor == "O":
            new_neighbor_position = self._move_object(
                neighbor_row,
                neighbor_column,
                direction,
                self.grid[row][column],
            )
            if new_neighbor_position != (neighbor_row, neighbor_column):
                self.grid[neighbor_row][neighbor_column] = self.grid[row][column]
                self.grid[row][column] = prev
                new_position = neighbor_row, neighbor_column
            else:
                new_position = row, column
            return new_position
        else:
            self.grid[neighbor_row][neighbor_column] = self.grid[row][column]
            self.grid[row][column] = prev
            return neighbor_row, neighbor_column


@dataclasses.dataclass
class WideMap(Map):
    robot: tuple[int, int] = None
    grid: list[list[str]] = dataclasses.field(default_factory=list)

    def __init__(self, raw_map: str):
        self.grid = []
        for row_index, raw_row in enumerate(raw_map.split("\n")):
            row = []
            for column_index, position in enumerate(raw_row):
                match position:
                    case "#":
                        row.extend(["#", "#"])
                    case "O":
                        row.extend(["[", "]"])
                    case ".":
                        row.extend([".", "."])
                    case "@":
                        row.extend(["@", "."])
                        self.robot = (row_index, row.index("@"))
            self.grid.append(row)

    def get_box_coordinates(self):
        for row_index, row in enumerate(self.grid):
            for column_index, position in enumerate(row):
                if position == "[":
                    yield 100 * row_index + column_index

    def move_robot(self, direction: str):
        if self._can_move(self.robot[0], self.robot[1], direction):
            self._move_object(self.robot[0], self.robot[1], direction, prev=".")
            match direction:
                case "<":
                    self.robot = self.robot[0], self.robot[1] - 1
                case "^":
                    self.robot = self.robot[0] - 1, self.robot[1]
                case ">":
                    self.robot = self.robot[0], self.robot[1] + 1
                case "v":
                    self.robot = self.robot[0] + 1, self.robot[1]

    def _can_move(self, row: int, column: int, direction: str) -> bool:
        match direction:
            case "<":
                if self.grid[row][column] == "]":
                    next_positions = [(row, column - 2)]
                else:
                    next_positions = [(row, column - 1)]
            case "^":
                next_positions = [(row - 1, column)]
                if self.grid[row - 1][column] == "]":
                    next_positions.append((row - 1, column - 1))
                elif self.grid[row - 1][column] == "[":
                    next_positions.append((row - 1, column + 1))
            case ">":
                if self.grid[row][column] == "[":
                    next_positions = [(row, column + 2)]
                else:
                    next_positions = [(row, column + 1)]
            case "v":
                next_positions = [(row + 1, column)]
                if self.grid[row + 1][column] == "]":
                    next_positions.append((row + 1, column - 1))
                elif self.grid[row + 1][column] == "[":
                    next_positions.append((row + 1, column + 1))

        can_move = True
        for next_position in next_positions:
            if self.grid[next_position[0]][next_position[1]] == "#":
                can_move = False
                break
            elif self.grid[next_position[0]][next_position[1]] in ("[", "]"):
                can_move = self._can_move(next_position[0], next_position[1], direction)
                if not can_move:
                    break
        return can_move

    def _move_object(
        self,
        row: int,
        column: int,
        direction: str,
        prev: str,
    ):
        match direction:
            case "<":
                neighbors = [(row, column - 1, self.grid[row][column])]
            case "^":
                neighbors = [(row - 1, column, self.grid[row][column])]
                if self.grid[row - 1][column] == "]":
                    neighbors.append((row - 1, column - 1, "."))
                elif self.grid[row - 1][column] == "[":
                    neighbors.append((row - 1, column + 1, "."))
            case ">":
                neighbors = [(row, column + 1, self.grid[row][column])]
            case "v":
                neighbors = [(row + 1, column, self.grid[row][column])]
                if self.grid[row + 1][column] == "]":
                    neighbors.append((row + 1, column - 1, "."))
                elif self.grid[row + 1][column] == "[":
                    neighbors.append((row + 1, column + 1, "."))

        for neighbor in neighbors:
            neighbor_row, neighbor_column, neighbor_prev = neighbor
            if self.grid[neighbor_row][neighbor_column] == ".":
                self.grid[neighbor_row][neighbor_column] = neighbor_prev
                self.grid[row][column] = prev
            else:
                self._move_object(neighbor_row, neighbor_column, direction, neighbor_prev)
                self.grid[neighbor_row][neighbor_column] = neighbor_prev
                self.grid[row][column] = prev


def _parse_file(filename: str) -> tuple[str, str]:
    with open(filename, "r") as f:
        raw = f.read()

    raw_map, raw_directions = raw.split("\n\n")
    return raw_map, "".join(raw_directions.split("\n"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw_map, directions = _parse_file(args.filename)
    map_ = Map(raw_map)
    for direction in directions:
        map_.move_robot(direction)
    print(f"Sum of boxes' GPS coordinates: {sum(map_.get_box_coordinates())}")

    wide_map = WideMap(raw_map)
    for direction in directions:
        wide_map.move_robot(direction)
    print(f"Sum of wide boxes' GPS coordinates: {sum(wide_map.get_box_coordinates())}")
