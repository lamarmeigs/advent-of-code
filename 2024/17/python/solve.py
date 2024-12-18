import argparse
import dataclasses
import re


class Halt(Exception):
    pass


class InvalidProgram(Exception):
    pass


@dataclasses.dataclass
class Computer:
    register_a: int = 0
    register_b: int = 0
    register_c: int = 0
    instruction_pointer: int = 0
    program: list[int] = dataclasses.field(default_factory=list)
    _output: list[int] = dataclasses.field(default_factory=list)

    def __str__(self):
        return (
            f"A:{self.register_a} "
            f"B:{self.register_b} "
            f"C:{self.register_c} "
            f"Output:{self.output}"
        )

    @property
    def output(self):
        return ','.join(str(output) for output in self._output)

    def run(self):
        try:
            while True:
                instruction, operand = self._get_next_instruction()
                self._execute(instruction, operand)
        except Halt:
            return

    def _get_next_instruction(self) -> tuple[int, int]:
        try:
            instruction = self.program[self.instruction_pointer]
            operand = self.program[self.instruction_pointer + 1]
        except IndexError:
            raise Halt
        return instruction, operand

    def _execute(self, instruction: int, operand: int):
        match instruction:
            case 0:
                self._adv(operand)
                self.instruction_pointer += 2
            case 1:
                self._bxl(operand)
                self.instruction_pointer += 2
            case 2:
                self._bst(operand)
                self.instruction_pointer += 2
            case 3:
                self._jnz(operand)
            case 4:
                self._bxc()
                self.instruction_pointer += 2
            case 5:
                self._out(operand)
                self.instruction_pointer += 2
            case 6:
                self._bdv(operand)
                self.instruction_pointer += 2
            case 7:
                self._cdv(operand)
                self.instruction_pointer += 2
            case _:
                raise InvalidProgram(f"Encountered instruction {instruction}")

    def _parse_operand(self, operand: int) -> int:
        value = None
        if operand in (0, 1, 2, 3):
            value = operand
        elif operand == 4:
            value = self.register_a
        elif operand == 5:
            value = self.register_b
        elif operand == 6:
            value = self.register_c
        else:
            raise InvalidProgram(f"Encountered operand {operand}")
        return value

    def _adv(self, operand: int):
        self._dv(operand, 'register_a')

    def _bdv(self, operand: int):
        self._dv(operand, 'register_b')

    def _cdv(self, operand: int):
        self._dv(operand, 'register_c')

    def _dv(self, operand: int, destination: str):
        value = self._parse_operand(operand)
        result = int(self.register_a / 2**value)
        setattr(self, destination, result)

    def _bxl(self, operand: int):
        self._bx(operand)

    def _bxc(self):
        self._bx(self.register_c)

    def _bx(self, value: int):
        self.register_b = self.register_b ^ value

    def _bst(self, operand: int):
        value = self._parse_operand(operand)
        self.register_b = value % 8

    def _jnz(self, operand: int):
        if self.register_a == 0:
            self.instruction_pointer += 2
        else:
            self.instruction_pointer = operand

    def _out(self, operand: int):
        value = self._parse_operand(operand)
        self._output.append(value % 8)


def _parse_file(filename: str) -> Computer:
    with open(filename, "r") as f:
        raw = f.read()

    return _build_computer(raw.strip())


def _build_computer(raw_computer: str) -> Computer:
    pattern = (
        r"Register A: (?P<reg_a>\d+)\s"
        r"Register B: (?P<reg_b>\d+)\s"
        r"Register C: (?P<reg_c>\d+)\s+"
        r"Program: (?P<program>(\d+,)+\d)"
    )
    if not (match := re.search(pattern, raw_computer)):
        raise ValueError("Unparseable raw input")

    computer = Computer(
        register_a=int(match.group("reg_a")),
        register_b=int(match.group("reg_b")),
        register_c=int(match.group("reg_c")),
        program=[int(inst) for inst in match.group("program").split(",")],
    )
    return computer


def _find_a(computer: Computer, instruction_index: int, guess: int = 0):
    if instruction_index < 0:
        return guess

    for d in range(8):
        register_a = guess << 3 | d
        test_computer = Computer(register_a=register_a, program=computer.program)
        test_computer.run()
        if test_computer._output == test_computer.program[instruction_index:]:
            if solution := _find_a(computer, instruction_index - 1, register_a):
                return solution

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    computer = _parse_file(args.filename)
    computer.run()
    print(f"Expected output: {computer.output}")

    register_a = _find_a(computer, len(computer.program) - 1)
    print(f"Uncorrupted register A: {register_a}")
