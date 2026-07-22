import xml.etree.ElementTree as ET

from github_profiler.domain.components import (
    Canvas,
    Card,
    Column,
    ComponentText,
    Dashboard,
    Row,
)
from github_profiler.domain.geometry import Padding
from github_profiler.domain.theme import Theme
from github_profiler.infrastructure.dashboard_renderer import DashboardRenderer


def test_empty_dashboard() -> None:
    theme = Theme()
    dash = Dashboard()
    renderer = DashboardRenderer()
    svg = renderer.render(dash, theme)

    # Empty dashboard geometry is 0x0
    assert 'viewBox="0 0 0.0 0.0"' in svg
    assert '<rect width="100%" height="100%"' in svg


def test_dashboard_with_single_card_and_canvas_translation() -> None:
    theme = Theme()
    canvas = Canvas(width=100, height=100)
    canvas.children.append(ComponentText(content="Inner Text", x=10, y=10))
    # Assign specific padding to test calculation
    card = Card(content=canvas, border_radius=12, shadow=True, padding=Padding.all(15))
    dash = Dashboard(children=[card])

    renderer = DashboardRenderer()
    svg = renderer.render(dash, theme)

    # 1. SVG Validity check
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"

    # 2. Canvas Translation check
    # Dashboard padding is 0, Card margin is 10, Card padding is 15.
    # Canvas x should be 10 (margin) + 15 (padding) = 25
    assert 'transform="translate(25.0, 25.0)"' in svg

    # 3. Text rendering inside translated Canvas
    assert ">Inner Text</text>" in svg
    # The inner logic doesn't offset x, it uses exactly what's given.
    assert 'x="10"' in svg

    # 4. Shadow & Rounded Corners Check
    assert 'filter="url(#card-shadow)"' in svg
    assert 'rx="12"' in svg


def test_nested_rows_columns_and_multiple_cards() -> None:
    theme = Theme()

    card1 = Card(content=Canvas(width=50, height=50))
    card2 = Card(content=Canvas(width=50, height=50))

    row = Row(children=[card1, card2])
    col = Column(children=[row])

    dash = Dashboard(children=[col])

    renderer = DashboardRenderer()
    svg = renderer.render(dash, theme)

    # Ensure two cards exist
    assert svg.count('filter="url(#card-shadow)"') == 2
    # Ensure both canvases are translated correctly
    assert svg.count('transform="translate') == 2
