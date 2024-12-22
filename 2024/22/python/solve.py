import argparse
import collections
import typing


def _parse_file(filename: str) -> str:
    with open(filename, "r") as f:
        raw = f.read()
    return raw.strip()


def _get_secret_numbers(secret: int) -> typing.Iterator[int]:
    def _mix(secret: int, operand: int) -> int:
        return secret ^ operand

    def _prune(secret: int) -> int:
        return secret % 16777216

    while True:
        secret = _mix(secret, secret * 64)
        secret = _prune(secret)
        # bit shifting is more efficient than `math.floor(secret / 32)`
        secret = _mix(secret, secret >> 5)
        secret = _prune(secret)
        secret = _mix(secret, secret * 2048)
        secret = _prune(secret)
        yield secret


def _get_nth_secret(seller: int, n: int) -> int:
    seller_secrets = _get_secret_numbers(seller)
    for _ in range(2000):
        secret = next(seller_secrets)
    return secret


def _get_price_sequences(sellers: list[int]) -> dict[tuple[int, int, int, int], int]:
    sequence_seller_values = collections.defaultdict(dict)
    for seller in sellers:
        secrets = _get_secret_numbers(seller)

        # Discard the first three prices to build history.
        last_price = seller % 10
        price_change_history = [None]
        for i in range(3):
            secret = next(secrets)
            price = secret % 10
            price_change = price - last_price
            price_change_history.append(price_change)
            last_price = price

        price_change_history = tuple(price_change_history)
        for i in range(1997):
            secret = next(secrets)
            price = secret % 10
            price_change = price - last_price
            price_change_history = price_change_history[1:] + (price_change,)
            if seller not in sequence_seller_values[price_change_history]:
                sequence_seller_values[price_change_history][seller] = price
            last_price = price

    sequence_total_values = {
        sequence: sum(sellers.values()) for sequence, sellers in sequence_seller_values.items()
    }
    return sequence_total_values


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw = _parse_file(args.filename)
    sellers = [int(seller) for seller in raw.split('\n')]
    secrets = {seller: _get_nth_secret(seller, 2000) for seller in sellers}
    print(f"Sum 2000th secret numbers: {sum(secrets.values())}")

    sequence_values = _get_price_sequences(sellers)
    print(f"Maximum bananas: {max(sequence_values.values())}")
