# From Jira to Test Cases

## Description

TBD

### Key Components:

- **main.py**: The entry point to execute the application.
- **gap_analyzer.py**: Identifies gaps within input data or user stories.
- **validator.py**: Validates input data ensuring integrity and consistency.
- **output_formatter.py**: Formats analysis results and test suites into readable markdown documents.
- **suite_generator.py**: Automates generation of main test cases and edge case scenarios.

## Pre-requisites

Ensure you have the following setup before running the application:

- **Python 3.13** installed on your system.
- **uv** installed for dependency management.
- A valid `.env` file containing your OpenAI API key, formatted as:
  
```bash
OPENAI_API_KEY="your-api-key"
```

- An example user story provided as input_user_story.md in the root of the project directory.
- Clone this repository and navigate to the project directory.
- Install project dependencies using:

```bash
uv sync
```

## Project Structure

Project structure without ignored files and directories:

```bash
.
├── README.md                 # Project documentation
├── input_user_story.md       # Input data or user story
├── main.py                   # Main execution script
├── output                    # Generated outputs
│   ├── additional_gap_tests.md
│   ├── edge_case_tests.md
│   ├── gap_analysis.md
│   └── main_test_cases.md
├── pyproject.toml            # Project configuration and dependencies
├── ruff.toml                 # Code linting configuration
├── src                       # Source code modules
│   ├── __init__.py
│   ├── edge_cases.md
│   ├── gap_analyzer.py
│   ├── output_formatter.py
│   ├── suite_generator.py
│   └── validator.py
├── tests                     # Unit tests
│   ├── __init__.py
│   ├── test_edgcase_generator.py
│   ├── test_testcase_generator.py
│   └── test_validator.py
└── uv.lock                   # Dependency lockfile
``` 

## Usage

```bash
uv run main.py --file input_user_story.md
```

## Running Tests

```bash
uv run pytest tests
```