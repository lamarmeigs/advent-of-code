import argparse


def _parse_file(filename: str) -> list[str]:
    with open(filename) as f:
        rows = f.readlines()
    return [row.strip("\n") for row in rows]


def _get_moveable_rolls(rows: list[str]) -> int:
    def _is_roll(x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= len(rows[0]) or y >= len(rows):
            return False
        return rows[y][x] == '@'

    def _count_neighbors(x: int, y: int) -> int:
        neighbors = 0
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if nx == x and ny == y:
                    continue
                if _is_roll(nx, ny):
                    neighbors += 1
        return neighbors

    moveable = []
    for y, row in enumerate(rows):
        for x, position in enumerate(row):
            if _is_roll(x, y) and _count_neighbors(x, y) < 4:
                moveable.append((x, y))
    return moveable


def _remove_rolls(moveable_rolls: list[tuple[int, int]], rows: list[str]):
    for x, y in moveable_rolls:
        rows[y] = rows[y][:x] + '.' + rows[y][x + 1 :]
    return len(moveable_rolls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    rows = _parse_file(args.filename)
    moveable_rolls = _get_moveable_rolls(rows)
    print(f"Moveable rolls: {len(moveable_rolls)}")

    total_removed = 0
    while moveable_rolls:
        total_removed += _remove_rolls(moveable_rolls, rows)
        moveable_rolls = _get_moveable_rolls(rows)
    print(f"Total removeable rolls: {total_removed}")
