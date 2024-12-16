import argparse
import dataclasses
import math
import re


@dataclasses.dataclass
class Robot:
    x: int
    y: int
    velocity: tuple[int, int]


@dataclasses.dataclass
class Map:
    width: int = 101
    height: int = 103
    robots: list[Robot] = dataclasses.field(default_factory=list)

    @property
    def safety_factor(self) -> int:
        half_x = self.width // 2
        half_y = self.height // 2
        quandrant_count = [0, 0, 0, 0]
        for robot in self.robots:
            if robot.x < half_x and robot.y < half_y:
                quandrant_count[0] += 1
            elif robot.x > half_x and robot.y < half_y:
                quandrant_count[1] += 1
            elif robot.x < half_x and robot.y > half_y:
                quandrant_count[2] += 1
            elif robot.x > half_x and robot.y > half_y:
                quandrant_count[3] += 1
        return math.prod(quandrant_count)

    def tick(self):
        for robot in self.robots:
            robot.x = (robot.x + robot.velocity[0]) % self.width
            robot.y = (robot.y + robot.velocity[1]) % self.height

    def is_tree(self):
        pattern = (
            f"1.{{{self.width - 1}}}"
            f"1{{{3}}}.{{{self.width - 3}}}"
            f"1{{{5}}}.{{{self.width - 5}}}"
            f"1{{{7}}}.{{{self.width - 7}}}"
            f"1{{{9}}}.{{{self.width - 9}}}"
        )
        return bool(re.search(pattern, str(self), re.DOTALL))

    def __str__(self):
        positions = [[0] * self.width for _ in range(self.height)]
        for robot in self.robots:
            positions[robot.y][robot.x] += 1
        return "\n".join(
            "".join("." if position == 0 else str(position) for position in row)
            for row in positions
        )


def _parse_file(filename: str) -> Map:
    with open(filename, "r") as f:
        raw = f.read()

    return _build_map(raw.strip())


def _build_map(raw: str) -> Map:
    robots = []
    pattern = r"p=(?P<x>\d+),(?P<y>\d+) v=(?P<x_diff>-?\d+),(?P<y_diff>-?\d+)"
    for raw_robot in raw.split("\n"):
        if not (m := re.match(pattern, raw_robot)):
            raise ValueError(f"Cannot parse robot format: {raw_robot}")
        robot = Robot(
            x=int(m.group("x")),
            y=int(m.group("y")),
            velocity=(int(m.group("x_diff")), int(m.group("y_diff"))),
        )
        robots.append(robot)
    return Map(robots=robots)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    map_ = _parse_file(args.filename)
    for _ in range(100):
        map_.tick()
    print(f"Safety factor after 100s: {map_.safety_factor}")

    map_ = _parse_file(args.filename)
    seconds = 0
    while not map_.is_tree():
        map_.tick()
        seconds += 1
    print(f"Seconds until easter egg: {seconds}")
