import argparse


def _parse_file(filename: str) -> list[str]:
    with open(filename) as f:
        banks = f.readlines()
    return [bank.strip("\n") for bank in banks]


def _get_max_joltage(bank: str, batteries: int) -> int:
    joltage = ''
    remaining_bank = bank
    while batteries:
        potential_batteries = remaining_bank[: len(remaining_bank) - (batteries - 1)]
        digit = max(potential_batteries)
        joltage += digit
        prev_digit = remaining_bank.index(digit)
        remaining_bank = remaining_bank[prev_digit + 1 :]
        batteries -= 1
    return int(joltage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    banks = _parse_file(args.filename)
    joltages = (_get_max_joltage(bank, 2) for bank in banks)
    print(f"Total joltage with 2 batteries: {sum(joltages)}")

    joltages = (_get_max_joltage(bank, 12) for bank in banks)
    print(f"Total joltage with 12 batteries: {sum(joltages)}")
