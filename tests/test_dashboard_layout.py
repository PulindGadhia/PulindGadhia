from github_profiler.domain.components import Canvas, Card, ComponentText, Row, Column
from github_profiler.domain.geometry import Padding
from github_profiler.infrastructure.dashboard_layout import DashboardLayoutEngine


def test_pure_function_layout() -> None:
    """Ensure the original tree is not mutated and is structurally replicated."""
    child1 = Canvas(width=100, height=50)
    child1.children.append(ComponentText(content="test1", x=10, y=10))

    child2 = Canvas(width=200, height=50)
    child2.children.append(ComponentText(content="test2", x=20, y=20))

    row = Row(children=[child1, child2], gap=10)
    row.padding = Padding(left=5, top=5, right=5, bottom=5)
    row.measure()  # Add geometry

    engine = DashboardLayoutEngine()
    result = engine.layout(row)

    assert result is not row  # It should be a clone
    assert isinstance(result, Row)
    assert result.x == 0
    assert result.y == 0

    # Original items should still have 0,0
    assert child1.x == 0
    assert child1.y == 0

    # New items should be offset
    res_child1 = result.children[0]
    res_child2 = result.children[1]

    assert res_child1.x == 5
    assert res_child1.y == 5

    assert res_child2.x == 5 + 100 + 10  # padding_left + width + gap
    assert res_child2.y == 5


def test_black_box_rule() -> None:
    """Ensure layout engine completely ignores Canvas children."""
    canvas = Canvas(width=100, height=100)
    text = ComponentText(content="internal", x=42, y=99)
    canvas.children.append(text)

    engine = DashboardLayoutEngine()
    result = engine.layout(canvas, x=50, y=50)

    assert result.x == 50
    assert result.y == 50

    # Text inside must be identical and UNCHANGED
    assert isinstance(result, Canvas)
    res_text = result.children[0]
    assert res_text.x == 42
    assert res_text.y == 99
    # The reference is retained identically since deep layout wasn't triggered
    assert res_text is text


def test_empty_containers() -> None:
    """Ensure empty rows and columns layout cleanly."""
    engine = DashboardLayoutEngine()
    
    row = Row()
    row.measure()
    res = engine.layout(row)
    assert isinstance(res, Row)
    assert not res.children
    
    col = Column()
    col.measure()
    res2 = engine.layout(col)
    assert isinstance(res2, Column)
    assert not res2.children


def test_nested_layouts_and_cards() -> None:
    """Test all requested edge cases: nesting, large padding, zero gap, multiple cards, negative coords."""
    engine = DashboardLayoutEngine()
    
    # Canvas inside Card
    canvas1 = Canvas(width=100, height=50)
    card1 = Card(content=canvas1, padding=Padding.all(10))
    
    canvas2 = Canvas(width=100, height=50)
    card2 = Card(content=canvas2, padding=Padding.all(10))
    
    # Card inside Row, multiple Cards, zero gap, large padding
    row = Row(children=[card1, card2], gap=0)
    row.padding = Padding.all(20)
    
    # Nested Row inside Column
    col = Column(children=[row], gap=10)
    
    # Ensure properties exist and compute
    col.measure()
    
    # Negative coordinates
    res = engine.layout(col, x=-50, y=-50)
    
    assert res.x == -50
    assert res.y == -50
    
    assert isinstance(res, Column)
    res_row = res.children[0]
    assert isinstance(res_row, Row)
    
    assert res_row.x == -50 # default column padding is 0
    assert res_row.y == -50
    
    res_card1 = res_row.children[0]
    assert isinstance(res_card1, Card)
    res_card2 = res_row.children[1]
    assert isinstance(res_card2, Card)
    
    # Row padding left is 20
    assert res_card1.x == -50 + 20
    # Next card follows immediately since gap is 0
    assert res_card2.x == -50 + 20 + res_card1.width
    
    # Card x is -30 (-50 + 20). Card padding is 10, margin is 10
    res_canvas1 = res_card1.content
    assert res_canvas1.x == -50 + 20 + 10 + 10  # Content is absolute
    assert res_canvas1.y == -50 + 20 + 10 + 10
