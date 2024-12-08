import argparse
import collections
import itertools


class Map:
    def __init__(self, raw_grid: str, has_harmonics: bool = False):
        self.width = 0
        self.height = 0
        self.antennas = collections.defaultdict(list)
        self.antinodes = collections.defaultdict(list)
        self.has_harmonics = has_harmonics
        self._detect_antennas(raw_grid)
        self._infer_antinodes()

    def _detect_antennas(self, raw_grid: str):
        for row_index, raw_row in enumerate(raw_grid.split()):
            self.height = max(row_index + 1, self.height)
            for column_index, frequency in enumerate(raw_row):
                self.width = max(column_index + 1, self.width)
                if frequency != '.':
                    self.antennas[frequency].append((row_index, column_index))

    def _infer_antinodes(self):
        def _add_vector(
            coordinates: tuple[int, ...],
            vector: tuple[int, ...]
        ) -> tuple[int, ...]:
            return tuple(sum(_) for _ in zip(coordinates, vector))

        def _in_map(coordinates: tuple[int, ...]) -> bool:
            return (
                0 <= coordinates[0] < self.width
                and 0 <= coordinates[1] < self.height
            )

        for frequency, antennas in self.antennas.items():
            for a1, a2 in itertools.combinations(antennas, 2):
                row_diff = a1[0] - a2[0]
                column_diff = a1[1] - a2[1]

                a1_vector = (row_diff, column_diff)
                a2_vector = (-row_diff, -column_diff)

                if self.has_harmonics:
                    for start_node, vector in [(a1, a1_vector), (a2, a2_vector)]:
                        antinode = start_node
                        while _in_map(antinode):
                            self.antinodes[frequency].append(antinode)
                            antinode = _add_vector(antinode, vector)
                else:
                    if _in_map(antinode_1 := _add_vector(a1, a1_vector)):
                        self.antinodes[frequency].append(antinode_1)
                    if _in_map(antinode_2 := _add_vector(a2, a2_vector)):
                        self.antinodes[frequency].append(antinode_2)

    def __str__(self):
        rendered_rows = []
        for row_index in range(self.height):
            rendered_row = ['.'] * self.width
            rendered_rows.append(rendered_row)

        for antinodes in self.antinodes.values():
            for row, column in antinodes:
                rendered_rows[row][column] = '#'

        for frequency, antennas in self.antennas.items():
            for row, column in antennas:
                rendered_rows[row][column] = frequency

        return '\n'.join(''.join(row) for row in rendered_rows)


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw_grid = f.read()
    return raw_grid


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw_map = _parse_file(args.filename)
    map_ = Map(raw_map)
    antinodes = itertools.chain(*map_.antinodes.values())
    print(f'Antinode #: {len(set(antinodes))}')

    map_ = Map(raw_map, has_harmonics=True)
    antinodes = itertools.chain(*map_.antinodes.values())
    print(f'Antinode #: {len(set(antinodes))}')
