from github_profiler.infrastructure.svg_builder import SVGBuilder


def test_svg_builder_empty() -> None:
    builder = SVGBuilder(width=100, height=100, bg_color="#000")
    result = builder.build()
    assert "<svg" in result
    assert 'width="100"' in result
    assert 'fill="#000"' in result


def test_svg_builder_rect() -> None:
    builder = SVGBuilder(width=100, height=100)
    builder.add_rect(10, 10, 50, 50, rx=5, fill="red")
    result = builder.build()
    assert '<rect x="10" y="10" width="50" height="50" rx="5" fill="red"/>' in result


def test_svg_builder_text() -> None:
    builder = SVGBuilder(width=100, height=100)
    builder.add_text("Hello <World>", 10, 20, fill="blue")
    result = builder.build()
    assert '<text x="10" y="20" fill="blue">Hello &lt;World&gt;</text>' in result


def test_svg_builder_groups_and_shadows() -> None:
    builder = SVGBuilder(width=100, height=100)
    builder.add_drop_shadow("card-shadow")
    builder.begin_group(transform="translate(10, 10)", filter="url(#card-shadow)")
    builder.add_rect(0, 0, 10, 10)
    builder.end_group()

    result = builder.build()
    assert "<defs>" in result
    assert '<filter id="card-shadow">' in result
    assert '<g transform="translate(10, 10)" filter="url(#card-shadow)">' in result
    assert "</g>" in result
