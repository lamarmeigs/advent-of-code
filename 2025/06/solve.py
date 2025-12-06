import argparse
import math
import re


def _parse_file(filename: str) -> tuple[list[int], list[str]]:
    with open(filename) as f:
        raw_lines = f.readlines()

    operations = raw_lines.pop().split()
    lines = []
    for line in raw_lines:
        numbers = [int(match.group()) for match in re.finditer(r"\d+", line)]
        lines.append(numbers)
    columns = list(zip(*lines))
    return columns, operations


def _do_math(numbers: list[int], operation: str) -> int:
    match operation:
        case "+":
            result = sum(numbers)
        case "*":
            result = math.prod(numbers)
        case _:
            raise ValueError(f"Unknown operation {operation}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    columns, operations = _parse_file(args.filename)
    result = sum(_do_math(columns[i], operations[i]) for i in range(len(columns)))
    print(f"Sum of all individual problems: {result}")
