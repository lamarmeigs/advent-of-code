import argparse
import math
import re


def _parse_file(filename: str) -> tuple[list[str], list[str]]:
    with open(filename) as f:
        raw_lines = f.readlines()
    operations = raw_lines.pop().split()
    return raw_lines, operations


def _parse_by_group(raw_numbers: list[str]) -> list[int]:
    lines = []
    for line in raw_numbers:
        numbers = [int(match.group()) for match in re.finditer(r"\d+", line)]
        lines.append(numbers)
    columns = list(zip(*lines))
    return columns


def _parse_by_column(raw_numbers: list[str]) -> list[int]:
    columns = []
    column = []
    for i in range(len(raw_numbers[0])):
        empty_column = True
        number = ''
        for line in raw_numbers:
            character = line[i]
            if not character.isspace():
                number += character
                empty_column = False

        if empty_column:
            columns.append(column)
            column = []
        else:
            column.append(int(number))
    return columns


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

    raw_numbers, operations = _parse_file(args.filename)
    columns = _parse_by_group(raw_numbers)
    result = sum(_do_math(numbers, operation) for numbers, operation in zip(columns, operations))
    print(f"Sum of all individual problems: {result}")

    columns = _parse_by_column(raw_numbers)
    result = sum(_do_math(numbers, operation) for numbers, operation in zip(columns, operations))
    print(f"Sum of all individual columnar problems: {result}")
