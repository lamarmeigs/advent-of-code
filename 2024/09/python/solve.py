import argparse
import typing


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read().strip()
    return raw


def _expand_map(dense_disk_map: str) -> list[int|str]:
    expanded = []
    file_id = 0
    is_free = False
    for block_count in dense_disk_map:
        if is_free:
            expanded += ['.'] * int(block_count)
        else:
            expanded += [file_id] * int(block_count)
            file_id += 1
        is_free = not is_free
    return expanded


def _compact(disk_map: list[int|str]):
    def _free_block_indexes(disk_map: list[int|str]) -> typing.Iterator[int]:
        for i in range(len(disk_map)):
            if disk_map[i] == '.':
                yield i

    free_block_indexes = _free_block_indexes(disk_map)
    for i in range(len(disk_map) - 1,-1,-1):
        if disk_map[i] != '.':
            empty_block = next(free_block_indexes)
            if empty_block > i:
                break
            disk_map[empty_block] = disk_map[i]
            disk_map[i] = '.'


def _get_checksum(disk_map: list[str|int]) -> int:
    return sum(
        position * file_id
        for position, file_id in enumerate(disk_map)
        if file_id != '.'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    dense_disk_map = _parse_file(args.filename)
    disk_map = _expand_map(dense_disk_map)
    _compact(disk_map)
    checksum = _get_checksum(disk_map)
    print(f'Compacted checksum: {checksum}')
