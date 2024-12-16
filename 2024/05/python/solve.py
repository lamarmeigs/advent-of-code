import argparse
import collections
import dataclasses
import functools
import itertools
import typing


def _parse_file(filename: str) -> tuple[dict[str, list[str]], list[list[str]]]:
    with open(filename, "r") as f:
        raw = f.read()
    raw_rules, raw_updates = raw.strip().split("\n\n")

    rules = collections.defaultdict(list)
    for rule in raw_rules.split():
        preceder, follower = rule.split("|")
        rules[preceder].append(follower)

    updates = []
    for update in raw_updates.split():
        updates.append(update.split(","))

    return rules, updates


@dataclasses.dataclass
class Validator:
    rules: dict[str, list[str]]

    def is_valid(self, update: list[str]) -> bool:
        for i, page in enumerate(update):
            allowed_followers = self.rules[page]
            if not all(later_page in allowed_followers for later_page in update[i + 1 :]):
                return False
        return True

    def compare(self, page_1: str, page_2: str) -> int:
        if page_2 in self.rules.get(page_1, []):
            return -1
        elif page_1 in self.rules.get(page_2, []):
            return 1
        else:
            return 0


def _partition_updates(
    updates: list[list[str]],
    rules: dict[str, list[str]],
) -> list[list[str]]:
    validator = Validator(rules)
    return _partition(validator.is_valid, updates)


def _partition(
    predicate: typing.Callable[[typing.Any], bool],
    sequence: typing.Iterable,
) -> typing.Iterable:
    iter1, iter2 = itertools.tee(sequence)
    return filter(predicate, iter1), itertools.filterfalse(predicate, iter2)


def _reorder_updates(
    updates: list[list[str]],
    rules: dict[str, list[str]],
) -> list[list[str]]:
    validator = Validator(rules)
    for update in updates:
        yield sorted(update, key=functools.cmp_to_key(validator.compare))


def _sum_middle_pages(updates: list[list[str]]):
    sum_ = 0
    for update in updates:
        center_index = int((len(update) - 1) / 2)
        sum_ += int(update[center_index])
    return sum_


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    rules, updates = _parse_file(args.filename)
    valid_updates, invalid_updates = _partition_updates(updates, rules)

    sum_ = _sum_middle_pages(valid_updates)
    print(f"Sum of valid updates' center page numbers: {sum_}")

    fixed_updates = _reorder_updates(invalid_updates, rules)
    sum_ = _sum_middle_pages(fixed_updates)
    print(f"Sum of fixed updates' center page numbers: {sum_}")
