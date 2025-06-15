# Tasks for Code Quality Improvements

## Relevant Files

- `src/weather/__init__.py` - Package initialization file
- `src/weather/server.py` - MCP server implementation
- `src/weather/nws_client.py` - NWS API client module
- `src/weather/models.py` - Data models and types
- `tests/__init__.py` - Test package initialization
- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_nws_client.py` - Tests for NWS client
- `tests/test_server.py` - Tests for MCP server endpoints
- `pyproject.toml` - Project metadata and dependencies
- `.flake8` - Flake8 configuration
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation
- `CONTRIBUTING.md` - Contribution guidelines

## Notes

- Follow TDD practices: Write tests first, then implement the minimal code to pass
- Run tests frequently with `pytest`
- Use `black` for code formatting
- Use `flake8` for linting
- Maintain backward compatibility throughout all changes

## Tasks

### 1.0 Project Setup and Configuration

- [x] 1.1 Create project structure
  - [x] 1.1.1 Create `src/weather` directory structure
  - [x] 1.1.2 Move existing `weather.py` to `src/weather/server.py`
  - [x] 1.1.3 Create `__init__.py` in `src/weather`
  - [x] 1.1.4 Create `tests` directory with `__init__.py`
  - [x] 1.1.5 Create `conftest.py` for pytest configuration

- [x] 1.2 Configure development environment
  - [x] 1.2.1 Update `pyproject.toml` with project metadata
  - [x] 1.2.2 Add development dependencies (pytest, black, flake8, mypy)
  - [x] 1.2.3 Configure black and flake8 in `pyproject.toml`
  - [x] 1.2.4 Create `.flake8` configuration file
  - [x] 1.2.5 Update `.gitignore` for Python projects

### 2.0 Refactor NWS Client Module

- [x] 2.1 Create NWS client module
  - [x] 2.1.1 Create `tests/test_nws_client.py`
  - [x] 2.1.2 Write failing test for `NWSClient` initialization
  - [x] 2.1.3 Create `nws_client.py` with minimal implementation
  - [x] 2.1.4 Refactor to pass initialization test
  - [x] 2.1.5 Add type hints and docstrings

- [x] 2.2 Implement request utilities
  - [x] 2.2.1 Write failing test for `_make_request` method
  - [x] 2.2.2 Implement minimal `_make_request` method in `NWSClient`
  - [x] 2.2.3 Add tests for error cases
  - [x] 2.2.4 Refactor implementation to pass all tests

- [x] 2.3 Add NWS API endpoints
  - [x] 2.3.1 Write test for `get_alerts` method
  - [x] 2.3.2 Implement `get_alerts` method
  - [x] 2.3.3 Write test for `get_forecast` method
  - [x] 2.3.4 Implement `get_forecast` method
  - [x] 2.3.5 Add response validation and error handling

### 3.0 Refactor Server Module

- [ ] 3.1 Restructure server implementation
  - [x] 3.1.1 Write failing test for server initialization
  - [x] 3.1.2 Refactor server code to pass initialization test
  - [ ] 3.1.3 Add type hints and docstrings
  - [ ] 3.1.4 Implement proper error handling

- [ ] 3.2 Update endpoint implementations
  - [ ] 3.2.1 Write test for `/get_alerts` endpoint
  - [ ] 3.2.2 Refactor endpoint to use NWS client
  - [ ] 3.2.3 Write test for `/get_forecast` endpoint
  - [ ] 3.2.4 Refactor endpoint to use NWS client
  - [ ] 3.2.5 Add input validation

### 4.0 Implement Unit Tests

- [ ] 4.1 Set up test fixtures
  - [ ] 4.1.1 Create mock NWS API responses
  - [ ] 4.1.2 Set up pytest fixtures for client and server
  - [ ] 4.1.3 Configure test coverage reporting

- [ ] 4.2 Test NWS client
  - [ ] 4.2.1 Test successful API responses
  - [ ] 4.2.2 Test error handling
  - [ ] 4.2.3 Test response parsing
  - [ ] 4.2.4 Test rate limiting and retries

- [ ] 4.3 Test server endpoints
  - [ ] 4.3.1 Test endpoint registration
  - [ ] 4.3.2 Test request validation
  - [ ] 4.3.3 Test error responses
  - [ ] 4.3.4 Test integration with NWS client

### 5.0 Documentation and Finalization

- [ ] 5.1 Create/update README
  - [ ] 5.1.1 Add project description
  - [ ] 5.1.2 Document installation
  - [ ] 5.1.3 Add usage examples
  - [ ] 5.1.4 Document API reference

- [ ] 5.2 Add contribution guidelines
  - [ ] 5.2.1 Document development setup
  - [ ] 5.2.2 Explain coding standards
  - [ ] 5.2.3 Describe pull request process

- [ ] 5.3 Final checks
  - [ ] 5.3.1 Run all tests
  - [ ] 5.3.2 Check code coverage
  - [ ] 5.3.3 Run linter and formatter
  - [ ] 5.3.4 Verify backward compatibility
