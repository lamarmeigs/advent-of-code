import argparse
import dataclasses


@dataclasses.dataclass
class Region:
    plots: list['Plot'] = dataclasses.field(default_factory=list)

    def __add__(self, other):
        region = Region(plots=self.plots + other.plots)
        return region

    def __getitem__(self, key) -> 'Plot':
        if isinstance(key, tuple) and len(key) == 2:
            return self.plots[key[0]][key[1]]
        return self.plots.__getitem__(key)

    @property
    def fence_price(self) -> int:
        return self.area * self.perimeter

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        perimeter = 0
        for plot in self.plots:
            possible_neighbors = (
                Plot(row=plot.row-1, column=plot.column, value=plot.value),
                Plot(row=plot.row+1, column=plot.column, value=plot.value),
                Plot(row=plot.row, column=plot.column-1, value=plot.value),
                Plot(row=plot.row, column=plot.column+1, value=plot.value),
            )
            for neighbor in possible_neighbors:
                if neighbor not in self.plots:
                    perimeter += 1
        return perimeter


@dataclasses.dataclass
class Plot:
    row: int
    column: int
    value: str
    region: Region = None

    def __eq__(self, other: 'Plot'):
        return (
            self.row == other.row
            and self.column == other.column
            and self.value == self.value
        )

    def __repr__(self):
        return f'{self.value} ({self.row},{self.column})'


def _parse_file(filename: str) -> str:
    with open(filename, 'r') as f:
        raw = f.read()
    return raw.strip()


def _build_map(raw_map: str) -> list[list[Plot]]:
    map_ = []
    for row_index, raw_row in enumerate(raw_map.split('\n')):
        row = []
        for column_index, raw_plot in enumerate(raw_row):
            plot = Plot(
                row=row_index,
                column=column_index,
                value=raw_plot,
            )
            row.append(plot)
        map_.append(row)
    return map_


def _detect_regions(map_: list[list[Plot]]) -> list[Region]:
    regions = []
    for row_index, row in enumerate(map_):
        for column_index, plot in enumerate(row):
            region = None
            if column_index > 0:
                neighbor_left = map_[row_index][column_index-1]
                if neighbor_left.value == plot.value:
                    region = neighbor_left.region
            if row_index > 0:
                neighbor_up = map_[row_index-1][column_index]
                if (
                    neighbor_up.value == plot.value
                    and neighbor_up.region != region
                ):
                    if not region:
                        region = neighbor_up.region
                    else:
                        regions.remove(neighbor_left.region)
                        regions.remove(neighbor_up.region)
                        region = neighbor_left.region + neighbor_up.region
                        for old_plot in region.plots:
                            map_[old_plot.row][old_plot.column].region = region
                        regions.append(region)

            if region:
                plot.region = region
                region.plots.append(plot)
            else:
                region = Region(plots=[plot])
                plot.region = region
                regions.append(region)
    return regions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    raw = _parse_file(args.filename)
    map_ = _build_map(raw)
    regions = _detect_regions(map_)
    print(f"Total price of fencing: {sum(region.fence_price for region in regions)}")
