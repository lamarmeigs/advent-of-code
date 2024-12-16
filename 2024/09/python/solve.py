import argparse
import typing


def _parse_file(filename: str) -> str:
    with open(filename, "r") as f:
        raw = f.read().strip()
    return raw


def _expand_map(dense_disk_map: str) -> list[int | str]:
    expanded = []
    file_id = 0
    is_free = False
    for block_count in dense_disk_map:
        if is_free:
            expanded += ["."] * int(block_count)
        else:
            expanded += [file_id] * int(block_count)
            file_id += 1
        is_free = not is_free
    return expanded


def _compact(disk_map: list[int | str]):
    def _free_block_indexes(disk_map: list[int | str]) -> typing.Iterator[int]:
        for i in range(len(disk_map)):
            if disk_map[i] == ".":
                yield i

    free_block_indexes = _free_block_indexes(disk_map)
    for i in range(len(disk_map) - 1, -1, -1):
        if disk_map[i] != ".":
            empty_block = next(free_block_indexes)
            if empty_block > i:
                break
            disk_map[empty_block] = disk_map[i]
            disk_map[i] = "."


def _compact_nofrag(disk_map: list[int | str]):
    def _file_block_ranges(disk_map: list[int | str]) -> typing.Iterator[tuple[int, int]]:
        file_id = disk_map[-1]
        end_block = len(disk_map) - 1
        start_block = end_block
        while start_block >= 0:
            if disk_map[start_block - 1] != file_id or start_block == 0:
                yield (start_block, end_block)
                end_block = start_block - 1
                while disk_map[end_block] == ".":
                    end_block -= 1
                file_id = disk_map[end_block]
                start_block = end_block + 1
            start_block -= 1

    def _find_empty_space(size: int) -> tuple[int, int] | None:
        start_block = disk_map.index(".")
        end_block = start_block
        while end_block < len(disk_map):
            if disk_map[end_block] != ".":
                start_block = disk_map[end_block:].index(".") + end_block
                end_block = start_block
            elif end_block - start_block + 1 == size:
                return (start_block, end_block)
            else:
                end_block += 1
        return None

    for file_start_block, file_end_block in _file_block_ranges(disk_map):
        size = file_end_block - file_start_block + 1
        empty_blocks = _find_empty_space(size)
        if empty_blocks and empty_blocks[1] < file_start_block:
            disk_map[empty_blocks[0] : empty_blocks[1] + 1] = disk_map[
                file_start_block : file_end_block + 1
            ]
            disk_map[file_start_block : file_end_block + 1] = ["."] * size


def _get_checksum(disk_map: list[str | int]) -> int:
    return sum(position * file_id for position, file_id in enumerate(disk_map) if file_id != ".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    dense_disk_map = _parse_file(args.filename)
    disk_map = _expand_map(dense_disk_map)
    _compact(disk_map)
    checksum = _get_checksum(disk_map)
    print(f"Compacted checksum: {checksum}")

    disk_map = _expand_map(dense_disk_map)
    _compact_nofrag(disk_map)
    checksum = _get_checksum(disk_map)
    print(f"Compacted, unfragmented checksum: {checksum}")
