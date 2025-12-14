import argparse
import dataclasses
import re


def _parse_file(filename: str) -> dict[str, list[str]]:
    with open(filename) as f:
        raw = f.read().strip()

    shapes = []
    for block in raw.split("\n\n"):
        if match := re.fullmatch(r"^\d+:\n([#\.\n]+)$", block):
            shapes.append(match.groups()[0])
        else:
            trees = [tree.strip() for tree in block.split('\n')]
    return shapes, trees


@dataclasses.dataclass
class Present:
    shape: list[str]
    tiles: int = 0

    def __post_init__(self):
        self.tiles = sum(row.count("#") for row in self.shape)

    @classmethod
    def from_raw(cls, raw_shape: str) -> 'Present':
        return cls([row for row in raw_shape.split("\n")])

    def __str__(self):
        return '\n'.join(self.shape)


@dataclasses.dataclass
class Tree:
    width: int
    height: int
    present_count: list[int]

    @classmethod
    def from_raw(cls, raw: str) -> "Tree":
        dimensions, present_count = raw.split(":")
        width, height = dimensions.split("x")
        present_count = [int(count) for count in present_count.strip().split()]
        return cls(int(width), int(height), present_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw_shapes, raw_trees = _parse_file(args.filename)
    presents = [Present.from_raw(shape) for shape in raw_shapes]
    trees = [Tree.from_raw(raw_tree) for raw_tree in raw_trees]

    fillable = 0
    for tree in trees:
        tree_area = tree.width * tree.height
        present_tiles = sum(
            presents[i].tiles * present_count for i, present_count in enumerate(tree.present_count)
        )
        if present_tiles <= tree_area:
            fillable += 1
    print(fillable)
