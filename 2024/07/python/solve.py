import argparse
import itertools
import typing


def _parse_file(filename: str) -> dict[int, list[str]]:
    with open(filename, 'r') as f:
        raw_lines = f.readlines()

    equations = {}
    for line in raw_lines:
        test_value, operands = line.split(':')
        equations[int(test_value.strip())] = [val.strip() for val in operands.split()]
    return equations


def _validate_equations(
    equations: dict[int, list[str]],
    operators: list[str],
) -> dict[int, list[int]]:
    valid_equations = {}
    for test_value, operands in equations.items():
        for possible_equation in _generate_equations(operands, operators):
            if _evaluates(possible_equation, test_value):
                valid_equations[test_value] = possible_equation
                break
    return valid_equations


def _generate_equations(
    operands: list[str],
    operators: list[str],
) -> typing.Iterator[str]:
    operator_permutations = _permute(operators, len(operands) - 1)
    for permutation in operator_permutations:
        yield _interleave(operands, permutation)


def _permute(operators: list[str], length: int) -> typing.Iterator[str]:
    if length == 1:
        for operator in operators:
            yield (operator,)
        return

    for operator in operators:
        for remaining in _permute(operators, length - 1):
            yield (operator, *remaining)


def _interleave(iter_1: typing.Iterable, iter_2: typing.Iterable) -> typing.Iterable:
    flattened = []
    for pair in itertools.zip_longest(iter_1, iter_2):
        for val in pair:
            if val:
                flattened.append(val)
    return flattened


def _evaluates(equation: list[str], result: int) -> bool:
    total = int(equation[0])
    for operator, operand in itertools.batched(equation[1:], 2):
        match operator:
            case '+':
                total += int(operand)
            case '*':
                total *= int(operand)
            case '||':
                total = int(str(total) + operand)
    return total == result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    equations = _parse_file(args.filename)
    valid_equations = _validate_equations(equations, operators=('+', '*'))
    print(
        f'Sum of test values with valid equations (using +, *): {sum(valid_equations.keys())}'
    )

    valid_equations = _validate_equations(equations, operators=('+', '*', '||'))
    print(
        f'Sum of test values with valid equations (using +, *, ||): {sum(valid_equations.keys())}'
    )
