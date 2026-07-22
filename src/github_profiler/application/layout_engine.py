"""Dashboard layout engine."""

from github_profiler.domain.components import ComponentGroup
from github_profiler.domain.layout import Dashboard, Row, Column, Grid


class DashboardLayoutEngine:
    """Converts dashboard layouts into positioned UI components."""

    def layout(self, dashboard: Dashboard) -> ComponentGroup:
        root = ComponentGroup(x=0, y=0)

        current_y = dashboard.padding

        for item in dashboard.children:

            if isinstance(item, Row):
                group = self._layout_row(item)
                group.x = dashboard.padding
                group.y = current_y
                current_y += group.height + dashboard.spacing
                root.children.append(group)

            elif isinstance(item, Column):
                group = self._layout_column(item)
                group.x = dashboard.padding
                group.y = current_y
                current_y += group.height + dashboard.spacing
                root.children.append(group)

            elif isinstance(item, Grid):
                group = self._layout_grid(item)
                group.x = dashboard.padding
                group.y = current_y
                current_y += group.height + dashboard.spacing
                root.children.append(group)

        return root

    def _layout_row(self, row: Row) -> ComponentGroup:
        group = ComponentGroup(x=0, y=0)

        x = row.padding
        max_height = 0

        for item in row.children:
            comp = item.component
            comp.x = x
            comp.y = row.padding

            x += comp.width + row.spacing
            max_height = max(max_height, comp.height)

            group.children.append(comp)

        group.width = x
        group.height = max_height + row.padding * 2

        return group

    def _layout_column(self, column: Column) -> ComponentGroup:
        group = ComponentGroup(x=0, y=0)

        y = column.padding
        max_width = 0

        for item in column.children:
            comp = item.component
            comp.x = column.padding
            comp.y = y

            y += comp.height + column.spacing
            max_width = max(max_width, comp.width)

            group.children.append(comp)

        group.width = max_width + column.padding * 2
        group.height = y

        return group

    def _layout_grid(self, grid: Grid) -> ComponentGroup:
        group = ComponentGroup(x=0, y=0)

        col = 0
        row = 0

        cell_w = 320
        cell_h = 220

        for item in grid.children:
            comp = item.component

            comp.x = col * (cell_w + grid.spacing)
            comp.y = row * (cell_h + grid.spacing)

            group.children.append(comp)

            col += 1

            if col >= grid.columns:
                col = 0
                row += 1

        group.width = grid.columns * (cell_w + grid.spacing)
        group.height = (row + 1) * (cell_h + grid.spacing)

        return group