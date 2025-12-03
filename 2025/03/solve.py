import argparse


def _parse_file(filename: str) -> list[str]:
    with open(filename) as f:
        banks = f.readlines()
    return (bank.strip("\n") for bank in banks)


def _get_max_joltage(bank: str) -> int:
    digit_1 = bank.index(max(bank[:-1]))
    digit_2 = bank.index(max(bank[digit_1 + 1 :]))
    return int(bank[digit_1] + bank[digit_2])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    banks = _parse_file(args.filename)
    joltages = (_get_max_joltage(bank) for bank in banks)
    print(f"Total joltage: {sum(joltages)}")
