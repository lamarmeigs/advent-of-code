import argparse
import dataclasses
import enum


class Direction(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'
    LEFT_UP = 'left_up'
    LEFT_DOWN = 'left_down'
    RIGHT_UP = 'right_up'
    RIGHT_DOWN = 'right_down'


@dataclasses.dataclass
class Letter:
    value: str
    in_word: bool = False

    def __str__(self):
        return self.value


class WordBlock:
    def __init__(self, raw_block: str):
        self.width = 0
        self.height = 0
        self.rows = []
        for row in raw_block.split('\n'):
            self.rows.append([Letter(letter) for letter in row])
            self.height += 1
            self.width = max(self.width, len(row))

    def __getitem__(self, key):
        return self.rows.__getitem__(key)

    @property
    def raw(self):
        return '\n'.join(
            (''.join(letter.value for letter in row))
            for row in self.rows
        )

    @property
    def detected(self):
        return '\n'.join(
            (''.join(letter.value if letter.in_word else '.' for letter in row))
            for row in self.rows
        )

    def find_matches(self, word: str) -> int:
        matches = 0
        for row in range(self.height):
            for column in range(self.width):
                for direction in Direction:
                    if self._find_match(row, column, direction, match='XMAS'):
                        matches += 1
        return matches

    def _find_match(self, row: int, column: int, direction: Direction, match: str) -> bool:
        if (
            row < 0
            or row >= self.height
            or column < 0
            or column >= self.width
        ):
            return False

        if (letter := self[row][column]).value != match[0]:
            return False

        if len(match) == 1:
            letter.in_word = True
            return True

        match direction:
            case Direction.LEFT:
                next_row = row
                next_column = column + 1
            case Direction.RIGHT:
                next_row = row
                next_column = column - 1
            case Direction.UP:
                next_row = row - 1
                next_column = column
            case Direction.DOWN:
                next_row = row + 1
                next_column = column
            case Direction.LEFT_UP:
                next_row = row - 1
                next_column = column - 1
            case Direction.LEFT_DOWN:
                next_row = row + 1
                next_column = column - 1
            case Direction.RIGHT_UP:
                next_row = row - 1
                next_column = column + 1
            case Direction.RIGHT_DOWN:
                next_row = row + 1
                next_column = column + 1

        if self._find_match(next_row, next_column, direction, match[1:]):
            letter.in_word = True
            return True

        return False


def _parse_file(filename: str) -> WordBlock:
    with open(filename, 'r') as f:
        raw = f.read()
    return raw.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw_word_block = _parse_file(args.filename)
    block = WordBlock(raw_word_block)
    word_count = block.find_matches('XMAS')
    print(f'XMAS #: {word_count}')
