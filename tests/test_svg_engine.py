"""Unit tests for the SVG engine."""
from github_profiler.infrastructure.svg_engine import (
    SVGDocument,
    SVGRect,
    SVGText,
    SVGGroup,
)


def test_svg_rect_render():
    """Test rendering an SVGRect."""
    rect = SVGRect(10, 20, 100, 50, rx=5, attributes={"fill": "red"})
    xml = rect.render()
    assert "<rect" in xml
    assert 'x="10"' in xml
    assert 'y="20"' in xml
    assert 'width="100"' in xml
    assert 'height="50"' in xml
    assert 'rx="5"' in xml
    assert 'fill="red"' in xml


def test_svg_text_render():
    """Test rendering an SVGText."""
    text = SVGText("Hello", x=10, y=20, attributes={"class": "title"})
    xml = text.render()
    assert "<text" in xml
    assert 'x="10"' in xml
    assert 'y="20"' in xml
    assert 'class="title"' in xml
    assert ">Hello</text>" in xml


def test_svg_document_render():
    """Test rendering a complete SVGDocument."""
    doc = SVGDocument(800, 600, view_box="0 0 800 600")
    doc.add_style(".title { fill: blue; }")
    doc.add_shape(SVGRect(0, 0, 800, 600))
    doc.add_shape(SVGText("Test", x=10, y=20))
    
    xml = doc.render()
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in xml
    assert 'width="800"' in xml
    assert 'height="600"' in xml
    assert 'viewBox="0 0 800 600"' in xml
    assert "<style>" in xml
    assert ".title { fill: blue; }" in xml
    assert "</svg>" in xml
    assert "<rect" in xml
    assert "<text" in xml
