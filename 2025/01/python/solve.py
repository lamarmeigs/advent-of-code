import argparse


def _parse_file(filename: str) -> list[str]:
    with open(filename) as f:
        lines = f.readlines()
    return lines


def _rotate_dial(current_position: int, instruction: str) -> int:
    rotation = int(instruction[1:])
    if instruction.startswith('L'):
        next_position = current_position - rotation
    elif instruction.startswith('R'):
        next_position = current_position + rotation
    return next_position


def _rotate_dial_with_count(current_position: int, instruction: str) -> int:
    next_position = _rotate_dial(current_position, instruction)

    passes_zero = 0
    while next_position < 0:
        next_position += 100
        passes_zero += 1
    while next_position > 100:
        next_position -= 100
        passes_zero += 1
    return next_position, passes_zero


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    instructions = _parse_file(args.filename)
    current_position = 50
    combination = []
    for instruction in instructions:
        current_position = _rotate_dial(current_position, instruction)
        combination.append(current_position % 100)
    print(f"Number of 0s in combination: {combination.count(0)}")

    current_position = 50
    combination = []
    passes_zero = 0
    for instruction in instructions:
        current_position, new_passes_zero = _rotate_dial_with_count(
            current_position,
            instruction,
        )
        passes_zero += new_passes_zero
        combination.append(current_position)
    print(f"Number of 0s while dialing: {passes_zero + combination.count(0)}")
