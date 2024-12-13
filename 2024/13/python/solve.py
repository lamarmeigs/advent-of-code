import argparse
import dataclasses
import re


@dataclasses.dataclass
class Button:
    x_diff: int
    y_diff: int


@dataclasses.dataclass
class ClawGame:
    a: Button
    b: Button
    prize: tuple[int, int]

    def solve(self) -> tuple[tuple[int, int], int]:
        solution = None
        solution_tokens = None
        for a_presses in range(100, -1, -1):
            if (
                (b_presses := int((self.prize[0] - self.a.x_diff * a_presses) / self.b.x_diff))
                == (self.prize[1] - self.a.y_diff * a_presses) / self.b.y_diff
            ):
                tokens = 3 * a_presses + b_presses
                if not solution_tokens or solution_tokens > tokens:
                    solution_tokens = tokens
                    solution = a_presses, b_presses
        return solution, solution_tokens


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read()

    return _build_games(raw)


def _build_games(raw: str) -> list[ClawGame]:
    games = []
    pattern = (
        r'Button A: X\+(?P<a_x>\d+), Y\+(?P<a_y>\d+)\n'
        r'Button B: X\+(?P<b_x>\d+), Y\+(?P<b_y>\d+)\n'
        r'Prize: X=(?P<prize_x>\d+), Y=(?P<prize_y>\d+)'
    )
    for raw_game in raw.split('\n\n'):
        if not (m := re.match(pattern, raw_game)):
            raise ValueError('Cannot parse game format')
        game = ClawGame(
            a=Button(int(m.group('a_x')), int(m.group('a_y'))),
            b=Button(int(m.group('b_x')), int(m.group('b_y'))),
            prize=(int(m.group('prize_x')), int(m.group('prize_y'))),
        )
        games.append(game)
    return games


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    games = _parse_file(args.filename)
    tokens = sum(game.solve()[1] or 0 for game in games)
    print(f'Tokens necessary to win all possible prizes: {tokens}')
