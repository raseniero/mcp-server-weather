# Contributing to Weather MCP Server

We welcome contributions! Please follow these guidelines to keep the project consistent and maintainable.

## Development setup

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/YourOrg/weather-mcp-server.git
   cd weather-mcp-server
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Coding standards

- **Formatting**: We use [Black](https://github.com/psf/black) (88‑column, double quotes).
- **Linting**: We use [Flake8](https://flake8.pycqa.org/) for style checks.
- **Type checking**: We use [mypy](http://mypy-lang.org/) for static typing.
- **Docstrings**: Follow Google style. See existing code for examples.

Run quality checks locally:
```bash
black .
flake8
mypy src
```

## Pull request process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make your changes, including tests and documentation updates.
3. Ensure all tests and quality checks pass:
   ```bash
   pytest
   black . --check
   flake8
   mypy src
   ```
4. Push to your fork and open a pull request against `main`.
5. Address review feedback and ensure all CI checks pass.
6. Merge once approved.

Thank you for contributing!