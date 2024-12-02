import argparse
import itertools


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    reports = _parse_file(args.filename)
    safe_reports = list(filter(_is_safe, reports))
    print(f'Safe report #: {len(safe_reports)}')
