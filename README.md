# From Jira to Test Cases

## Description

This Python application automatically converts agile user stories into detailed, functional test cases using advanced AI technology. It streamlines testing by rapidly generating comprehensive test suites directly from agile project requirements, enhancing productivity and improving software quality.

### Features:
- **AI-Powered Test Case Generation:** Automatically translates agile user stories into detailed, structured functional test cases.
- **Flexible Input Methods:** Supports command-line arguments, standard input (stdin), and input via text files.
- **Markdown Outputs:** Provides clean, markdown-formatted documentation for easy integration into project documentation or collaboration tools.

### Key Components

- **`main.py`**: The primary script to initiate the application, manage input processing, and trigger test generation.
- **`gap_analyzer.py`**: Identifies unclear or incomplete elements within user stories, highlighting areas requiring further specification or refinement.
- **`validator.py`**: Ensures input data integrity by validating user stories for clarity, completeness, and absence of contradictions.
- **`output_formatter.py`**: Formats the generated test cases and gap analyses into markdown files for readability and easy documentation.
- **`suite_generator.py`**: Automatically generates comprehensive test suites, including main scenarios, edge cases, and additional tests based on gap analysis.

## Pre-requisites

To successfully run this application, ensure the following requirements are met:

- **Python 3.13** installed on your system. You can verify it running `python --version` in your terminal.
- **uv** installed for dependency management. You can verify it running `uv --version` in your terminal.
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

### Running the Application

```bash
uv run main.py --file input_user_story.md
```

### Logs

Logs generated during execution provide detailed insights into the application's workflow:

- Input Reading: Reads and parses the provided user story.
- Validation: Checks user stories for ambiguity, completeness, and contradictions.
- Test Generation: 
  - functional test cases 
  - edge cases 
  - identifies requirement gaps 
  - suggestions for required clarifications
- Output Generation: Formats and saves all generated files in the output directory.

Logs include timestamps and information levels `(INFO)` to clearly indicate each processing step.

```bash
uv run main.py --file input_user_story.md
2025-03-17 01:42:17.827 | INFO     | __main__:run:206 - Reading input
2025-03-17 01:42:17.828 | INFO     | __main__:run:216 - Processing input and generating test cases
2025-03-17 01:42:17.828 | INFO     | __main__:process_input:147 - Validating input data
2025-03-17 01:42:17.830 | INFO     | src.validator:forward:50 - Check for ambiguity
2025-03-17 01:42:17.836 | INFO     | src.validator:forward:58 - Check for completeness
2025-03-17 01:42:17.837 | INFO     | src.validator:forward:66 - Check for contradictions
2025-03-17 01:42:17.837 | INFO     | src.validator:forward:74 - User story is valid
2025-03-17 01:42:17.837 | INFO     | __main__:process_input:156 - Generating test suite components
2025-03-17 01:42:17.837 | INFO     | __main__:generate_test_cases:61 - Generating functional test cases
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:67 - Ensure test case is unique
2025-03-17 01:42:17.839 | INFO     | __main__:generate_test_cases:73 - Generating edge cases
2025-03-17 01:42:17.841 | INFO     | src.suite_generator:forward:180 - Generated and added 5 edge cases
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:81 - Ensure test case is unique
2025-03-17 01:42:17.841 | INFO     | __main__:generate_test_cases:87 - Starting requirement gap analysis
2025-03-17 01:42:17.842 | INFO     | src.gap_analyzer:forward:43 - Parse JSON into a list of dictionaries
2025-03-17 01:42:17.842 | INFO     | src.gap_analyzer:forward:45 - Validate each gap against the Pydantic model
2025-03-17 01:42:17.842 | INFO     | __main__:generate_test_cases:91 - Generating additional test cases for gaps
2025-03-17 01:42:17.842 | INFO     | __main__:generate_test_cases:98 - Generating test cases for gap: Unclear handling of users in multiple groups.
2025-03-17 01:42:17.843 | INFO     | src.gap_analyzer:forward:71 - Parse JSON into a list of dictionaries
2025-03-17 01:42:17.843 | INFO     | src.gap_analyzer:forward:73 - Validate each test case against the Pydantic model
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.843 | INFO     | __main__:generate_test_cases:98 - Generating test cases for gap: Lack of detail on reactivation of users.
2025-03-17 01:42:17.844 | INFO     | src.gap_analyzer:forward:71 - Parse JSON into a list of dictionaries
2025-03-17 01:42:17.844 | INFO     | src.gap_analyzer:forward:73 - Validate each test case against the Pydantic model
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.844 | INFO     | __main__:generate_test_cases:98 - Generating test cases for gap: Ambiguity in user experience for token management.
2025-03-17 01:42:17.845 | INFO     | src.gap_analyzer:forward:71 - Parse JSON into a list of dictionaries
2025-03-17 01:42:17.845 | INFO     | src.gap_analyzer:forward:73 - Validate each test case against the Pydantic model
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.845 | INFO     | __main__:generate_test_cases:98 - Generating test cases for gap: No mention of error handling or notifications.
2025-03-17 01:42:17.846 | INFO     | src.gap_analyzer:forward:71 - Parse JSON into a list of dictionaries
2025-03-17 01:42:17.846 | INFO     | src.gap_analyzer:forward:73 - Validate each test case against the Pydantic model
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:108 - Ensure test case is unique
2025-03-17 01:42:17.846 | INFO     | __main__:generate_test_cases:127 - Assigning unique IDs to test cases
2025-03-17 01:42:17.846 | INFO     | __main__:process_input:161 - Format test cases to markdown
2025-03-17 01:42:17.847 | INFO     | __main__:process_input:166 - Format edge case tests to markdown
2025-03-17 01:42:17.847 | INFO     | __main__:process_input:171 - Format additional test cases to markdown
2025-03-17 01:42:17.847 | INFO     | __main__:process_input:176 - Format gap analysis to markdown
2025-03-17 01:42:17.847 | INFO     | __main__:process_input:181 - Ensure output directory exists
2025-03-17 01:42:17.847 | INFO     | __main__:process_input:184 - Saving output files
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:196 - Test cases and analysis generated successfully.
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:197 - Files saved in ./output directory:
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:198 - - main_test_cases.md
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:199 - - edge_case_tests.md
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:200 - - gap_analysis.md
2025-03-17 01:42:17.848 | INFO     | __main__:process_input:201 - - additional_gap_tests.md
```

### Output

When you run the application with the command 
`uv run main.py --file input_user_story.md`, it processes the user story and 
generates a comprehensive set of test cases and analysis files. These outputs 
are saved in the `output` directory as Markdown-formatted documents. Here’s 
what you’ll get:

- **`main_test_cases.md`**: Contains the primary functional test cases derived directly from the user story. These cover the core functionality and ensure the main requirements are testable.
- **`edge_case_tests.md`**: Includes test cases for edge scenarios, such as unusual inputs or boundary conditions, to verify the system’s robustness.
- **`gap_analysis.md`**: Lists identified gaps or ambiguities in the user story, along with suggested clarifications, helping you refine requirements.
- **`additional_gap_tests.md`**: Provides additional test cases specifically designed to address the gaps identified in the gap analysis, ensuring complete coverage.

All output files are automatically saved in the `./output` directory, ready for 
review or integration into your testing workflow.


## Running Tests

You can run the unit tests for this application using the following command:

```bash
uv run pytest tests
```