import argparse
import math


def _parse_file(filename: str) -> str:
    with open(filename, "r") as f:
        raw = f.read()
    return raw.strip()


def _get_secret_numbers(secret: int, count: int) -> int:
    def _mix(secret: int, operand: int) -> int:
        return secret ^ operand

    def _prune(secret: int) -> int:
        return secret % 16777216

    for _ in range(count):
        secret = _mix(secret, secret * 64)
        secret = _prune(secret)
        secret = _mix(secret, math.floor(secret / 32))
        secret = _prune(secret)
        secret = _mix(secret, secret * 2048)
        secret = _prune(secret)

    return secret


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw = _parse_file(args.filename)
    sellers = [int(number) for number in raw.split('\n')]
    secrets = {secret: _get_secret_numbers(secret, 2000) for secret in sellers}
    print(f"Sum 2000th secret numbers: {sum(secrets.values())}")
