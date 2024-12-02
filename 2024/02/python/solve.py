import argparse
import itertools
import typing


def _parse_file(filename: str) -> list[list[int]]:
    with open(filename, 'r') as f:
        lines = f.readlines()

    reports = []
    for line in lines:
        reports.append([int(level) for level in line.split()])

    return reports


def _is_safe(report: list[int]) -> bool:
    is_consistent = report == sorted(report) or report == sorted(report, reverse=True)
    if not is_consistent:
        return False

    for l1, l2 in itertools.pairwise(report):
        if not 0 < abs(l1 - l2) <= 3:
            return False

    return True


def _is_safe_dampened(report: list[int]) -> bool:
    return any(_is_safe(report[:index] + report[index+1:]) for index in range(len(report)))


def _partition(
    predicate: typing.Callable[[typing.Any], bool],
    sequence: typing.Iterable,
) -> typing.Iterable:
    iter1, iter2 = itertools.tee(sequence)
    return filter(predicate, iter1), itertools.filterfalse(predicate, iter2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    reports = _parse_file(args.filename)
    safe_reports, unsafe_reports = _partition(_is_safe, reports)
    safe_reports = list(safe_reports)
    print(f'Safe report # (raw): {len(safe_reports)}')

    safe_reports_dampened = filter(_is_safe_dampened, unsafe_reports)
    safe_reports.extend(safe_reports_dampened)
    print(f'Safe report # (dampened): {len(safe_reports)}')
