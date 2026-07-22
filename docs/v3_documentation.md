# GitHub Profiler V3 Documentation

## 1. Architecture Documentation
The V3 Architecture separates concerns into three layers:
1. **Domain**: `Canvas`, `Card`, `Row`, `Dashboard` (Pure data components).
2. **Application**: `DashboardLayoutEngine` and `DashboardOrchestrator` (Logic and layout calculation).
3. **Infrastructure**: `SVGBuilder` and `DashboardRenderer` (XML translation).

## 2. Plugin Development Guide
To build a plugin in V3:
1. Inherit from `IProfilePlugin`.
2. Define `@property def pipeline(self) -> str: return "dashboard"`.
3. Your `generate` method must return a `Canvas` object.

## 3. Dashboard Layout Guide
The Layout Engine wraps all `Canvas` returns into `Card` components.
Cards are positioned recursively. 
- You can override the default layout by defining `ILayoutStrategy`.
- Set margins, padding, and size constraints directly on the `Canvas`.

## 4. Migration Guide (Legacy to V3)
If you authored a plugin for V2:
1. Change `ComponentGroup` to `Canvas`.
2. Keep your `ComponentBox` and `ComponentText` logic identical.
3. Add `@property def pipeline(self) -> str: return "dashboard"`.
The `DashboardOrchestrator` will handle the rest!

## 5. API Documentation
- `DashboardOrchestrator.build_profile(username)`: Generates the full SVG.
- `DashboardLayoutEngine.layout(dashboard)`: Calculates absolute geometries.
- `SVGBuilder.build(dashboard, theme)`: Transpiles geometry to string SVG.

## 6. Contribution Guide
- Run `ruff check src tests` and `black --check src tests`.
- Run `PYTHONPATH=src mypy --strict src tests`.
- Ensure coverage remains >75%: `PYTHONPATH=src pytest --cov=src --cov-fail-under=75 tests/`.

## 7. Example Plugins
Refer to `src/github_profiler/application/plugins/neofetch.py` for a standard example of typewriter animations wrapped in a V3 `Canvas`.
