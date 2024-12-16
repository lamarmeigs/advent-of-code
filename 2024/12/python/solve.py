import argparse
import dataclasses
import enum


class Direction(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@dataclasses.dataclass
class Region:
    plots: list["Plot"] = dataclasses.field(default_factory=list)

    def __add__(self, other):
        region = Region(plots=self.plots + other.plots)
        return region

    def __getitem__(self, key) -> "Plot":
        if isinstance(key, tuple) and len(key) == 2:
            return self.plots[key[0]][key[1]]
        return self.plots.__getitem__(key)

    def price_fencing(self, is_bulk: bool = False) -> int:
        if is_bulk:
            cost = self.area * self.side_count
        else:
            cost = self.area * self.perimeter
        return cost

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        perimeter = 0
        for plot in self.plots:
            possible_neighbors = (
                Plot(row=plot.row - 1, column=plot.column, value=plot.value),
                Plot(row=plot.row + 1, column=plot.column, value=plot.value),
                Plot(row=plot.row, column=plot.column - 1, value=plot.value),
                Plot(row=plot.row, column=plot.column + 1, value=plot.value),
            )
            for neighbor in possible_neighbors:
                if neighbor not in self.plots:
                    perimeter += 1
        return perimeter

    @property
    def side_count(self) -> int:
        count = 0
        for plot in self.plots:
            for side in Direction:
                match side:
                    case Direction.LEFT:
                        plot_across = Plot(plot.row, plot.column - 1, plot.value)
                        old_neighbor = Plot(plot.row - 1, plot.column, plot.value)
                        across_old_neighbor = Plot(plot.row - 1, plot.column - 1, plot.value)
                    case Direction.RIGHT:
                        plot_across = Plot(plot.row, plot.column + 1, plot.value)
                        old_neighbor = Plot(plot.row - 1, plot.column, plot.value)
                        across_old_neighbor = Plot(plot.row - 1, plot.column + 1, plot.value)
                    case Direction.UP:
                        plot_across = Plot(plot.row - 1, plot.column, plot.value)
                        old_neighbor = Plot(plot.row, plot.column - 1, plot.value)
                        across_old_neighbor = Plot(plot.row - 1, plot.column - 1, plot.value)
                    case Direction.DOWN:
                        plot_across = Plot(plot.row + 1, plot.column, plot.value)
                        old_neighbor = Plot(plot.row, plot.column - 1, plot.value)
                        across_old_neighbor = Plot(plot.row + 1, plot.column - 1, plot.value)

                is_edge = plot_across not in self.plots
                already_counted = (
                    old_neighbor in self.plots and across_old_neighbor not in self.plots
                )
                if is_edge and not already_counted:
                    count += 1
        return count


@dataclasses.dataclass
class Plot:
    row: int
    column: int
    value: str
    region: Region = None

    def __eq__(self, other: "Plot"):
        return self.row == other.row and self.column == other.column and self.value == self.value

    def __repr__(self):
        return f"{self.value} ({self.row},{self.column})"


def _parse_file(filename: str) -> str:
    with open(filename, "r") as f:
        raw = f.read()
    return raw.strip()


def _build_map(raw_map: str) -> list[list[Plot]]:
    map_ = []
    for row_index, raw_row in enumerate(raw_map.split("\n")):
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
                neighbor_left = map_[row_index][column_index - 1]
                if neighbor_left.value == plot.value:
                    region = neighbor_left.region
            if row_index > 0:
                neighbor_up = map_[row_index - 1][column_index]
                if neighbor_up.value == plot.value and neighbor_up.region != region:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    raw = _parse_file(args.filename)
    map_ = _build_map(raw)
    regions = _detect_regions(map_)
    price = sum(region.price_fencing() for region in regions)
    print(f"Total price of fencing: {price}")

    bulk_price = sum(region.price_fencing(is_bulk=True) for region in regions)
    print(f"Total price of bulk fencing: {bulk_price}")
