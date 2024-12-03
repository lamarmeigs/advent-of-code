import argparse
import re


def _parse_file(filename: str) -> list[list[int]]:
    with open(filename, 'r') as f:
        memory = f.read()
    return memory


def _extract_instructions(memory: str) -> list[re.Match]:
    pattern = r'mul\(\d{1,3},\d{1,3}\)'
    instructions = re.findall(pattern, memory)
    return instructions


def _execute_instructions(instructions: list[str]) -> list[int]:
    results = {}
    pattern = r'mul\((?P<op1>\d{1,3}),(?P<op2>\d{1,3})\)'
    for instruction in instructions:
        if match := re.match(pattern, instruction):
            result = int(match.group('op1')) * int(match.group('op2'))
            results[instruction] = result
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    memory = _parse_file(args.filename)
    instructions = _extract_instructions(memory)
    results = _execute_instructions(instructions)
    print(f'Sum of multipy instructions: {sum(results.values())}')
