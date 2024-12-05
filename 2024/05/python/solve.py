import argparse
import collections


def _parse_file(filename: str) -> tuple[dict[str, list[str]], list[list[str]]]:
    with open(filename, 'r') as f:
        raw = f.read()
    raw_rules, raw_updates = raw.strip().split('\n\n')

    rules = collections.defaultdict(list)
    for rule in raw_rules.split():
        preceder, follower = rule.split('|')
        rules[preceder].append(follower)

    updates = []
    for update in raw_updates.split():
        updates.append(update.split(','))

    return rules, updates


def _filter_valid_updates(
    updates: list[list[str]],
    rules: dict[str, list[str]]
) -> list[list[str]]:
    def _is_valid(update: list[str]) -> bool:
        for i, page in enumerate(update):
            allowed_followers = rules[page]
            if not all(
                later_page in allowed_followers
                for later_page in update[i+1:]
            ):
                return False
        return True

    return filter(_is_valid, updates)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    rules, updates = _parse_file(args.filename)
    valid_updates = _filter_valid_updates(updates, rules)

    sum_ = 0
    for valid_update in valid_updates:
        center_index = int((len(valid_update) - 1) / 2)
        sum_ += int(valid_update[center_index])
    print(f"Sum of valid updates' center page numbers: {sum_}")
