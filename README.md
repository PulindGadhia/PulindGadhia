# GitHub Profiler v3.0

> **Note:** V3 introduces the new Dashboard Layout Engine. Please see the [V3 Documentation](docs/v3_documentation.md) for architecture details, plugin development guides, and legacy migration instructions. Built strictly using Clean Architecture and SOLID principles, this tool fetches your GitHub data and generates beautiful, animated SVG heatmaps, neofetch-style cards, and an ASCII portrait from your avatar—all capable of being embedded directly into your GitHub README.

## Demo GIF
![Demo](game.gif)

## Features
- **Terminal Rendering Engine**: Zero-dependency ANSI layout engine for rich terminal output.
- **SVG Animation Engine**: Object-oriented SVG generation without heavy dependencies.
- **ASCII Portrait Generator**: Leverages OpenCV and rembg to convert your avatar to a crisp ASCII portrait.
- **GitHub GraphQL Client**: Highly efficient data fetching.
- **Heatmap Generator**: Customizable SVG heatmap of your contribution calendar.
- **Neofetch Card**: Beautiful system-style summary card for your GitHub profile.
- **README Generator**: Automates injecting assets into a Markdown template.
- **Automated CI/CD**: Pre-configured GitHub Actions to run the generator on a schedule.
- **CLI**: A robust Command-Line Interface for manual execution.

## Architecture
This project adheres strictly to **Clean Architecture** to ensure maintainability, scalability, and independence from external frameworks.
- **Domain**: Core business entities (`GitHubUser`, `ContributionDay`, `Repository`) and interfaces.
- **Infrastructure**: Adapters for GitHub GraphQL, SVG building, and Terminal Rendering.
- **Application**: Use cases defining specific generators (ASCII, Heatmap, Neofetch).
- **Presentation**: The argparse CLI, serving as the composition root for Dependency Injection.

## Project Structure
```text
.
├── src/
│   └── github_profiler/
│       ├── domain/            # Entities and Interfaces
│       ├── infrastructure/    # API Clients, SVG & Terminal Engines
│       ├── application/       # Asset Generators (Heatmap, ASCII, etc.)
│       └── presentation/      # CLI Interface
├── tests/                     # Unit Tests
├── output/                    # Generated Assets
├── main.py                    # Entry Point
├── pyproject.toml             # Project Configuration (Ruff, Black, MyPy)
└── requirements.txt           # Dependencies
```

## Installation
Requires Python 3.11+.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/github-profiler.git
   cd github-profiler
   ```
2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage
You must generate a GitHub Personal Access Token (PAT) with read access to your profile data and repositories. Set it as an environment variable:
```bash
export GITHUB_TOKEN="your_personal_access_token"
```

Run the generator:
```bash
python main.py <github_username> --output-dir ./output
```

## CLI Examples
**Basic Execution:**
```bash
python main.py octocat
```

**Custom Output Directory & Verbose Logging:**
```bash
python main.py octocat --output-dir ./assets --verbose
```

**Passing Token Explicitly:**
```bash
python main.py octocat --token "ghp_xxxxxxxxxxxx"
```

## Configuration
The project is pre-configured with industry-standard development tools via `pyproject.toml`:
- **Ruff**: For lightning-fast linting.
- **Black**: For uncompromising code formatting.
- **MyPy**: For strict static type checking.
- **Pytest**: For unit testing.

## Generated Assets
When you run the tool, the following files are produced in the target output directory:
- `assets/heatmap.svg`: The contribution calendar heatmap.
- `assets/neofetch.svg`: The Neofetch-style profile card with ASCII art.
- `README.md`: The orchestrated Markdown file containing your generated assets.

## Testing
Run the test suite using `pytest`:
```bash
pytest
```
To run linting and type checking:
```bash
ruff check .
black --check .
mypy src/
```

## Roadmap
- [ ] Add support for custom SVG color themes (e.g., Dracula, Nord).
- [ ] Add more granular animation controls to the SVG Engine.
- [ ] Implement a caching layer for the GraphQL client to minimize API calls.
- [ ] Expand the neofetch card with language usage statistics.

## Contributing
Contributions are welcome. Please ensure that all code adheres to Clean Architecture and SOLID principles. 
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Ensure tests, linting, and type checks pass.
4. Commit your changes (`git commit -m 'feat: Add amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
