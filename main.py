import argparse
import asyncio
import sys
from datetime import datetime
import os

import dspy
from dotenv import load_dotenv
from loguru import logger

from src.validator import UserStoryValidator
from src.suite_generator import (
    TestCaseGenerator,
    EdgeCaseGenerator,
    TestSuite,
    format_test_suite_to_markdown,
    trainset,
    TestCase,
)
from src.gap_analyzer import (
    RequirementGapAnalyzer,
    ClarificationTestCaseGenerator,
)


class TestCaseGeneratorApp:
    def __init__(
        self,
        validator_model="openai/gpt-3.5-turbo",
        generator_model="openai/gpt-4o-mini",
    ):
        """Initialize with default language models, overridable via arguments."""
        self.validator_model = validator_model
        self.generator_model = generator_model
        self.lm_validator = dspy.LM(
            self.validator_model,
            max_tokens=300,
            temperature=0.0,
            api_key=os.environ["OPENAI_API_KEY"],
        )
        self.lm_generator = dspy.LM(
            self.generator_model,
            max_tokens=1000,
            temperature=0.0,
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def generate_test_cases(
        self, user_story: str
    ) -> tuple[TestSuite, list[dict]]:
        logger.info("Configuring language model for test case generation")
        dspy.settings.configure(lm=self.lm_generator)

        logger.info("Starting requirement gap analysis")
        gap_analyzer = RequirementGapAnalyzer()
        gaps_list = gap_analyzer.forward(user_story=user_story)

        logger.info("Generating additional test cases for gaps")
        clarification_generator = ClarificationTestCaseGenerator()
        gaps_with_tests = []
        for i, gap_dict in enumerate(gaps_list or [], start=1):
            description = gap_dict.get("description", "")
            clarification = gap_dict.get("suggested_clarification", "")
            confidence_level = gap_dict.get("confidence_level", "")
            logger.info(f"Generating test cases for gap {i}: {description}")
            additional_tests_json = clarification_generator.forward(
                user_story=user_story, clarification=clarification
            )
            additional_tests_pydantic = [
                TestCase(**tc) for tc in additional_tests_json
            ]
            gaps_with_tests.append(
                {
                    "gap": {
                        "description": description,
                        "suggested_clarification": clarification,
                        "confidence_level": confidence_level,
                    },
                    "tests": additional_tests_pydantic,
                }
            )

        logger.info("Generating functional test cases")
        test_generator = TestCaseGenerator(trainset=trainset)
        mainTestSuite = test_generator.forward(user_story=user_story)

        logger.info("Combining main and additional test cases")
        combined_test_cases = mainTestSuite.test_cases + [
            test for item in gaps_with_tests for test in item["tests"]
        ]

        logger.info("Generating edge cases")
        edge_generator = EdgeCaseGenerator()
        extendedSuite = edge_generator.forward(
            user_story=user_story,
            test_suite=TestSuite(
                title="Combined", test_cases=combined_test_cases
            ),
        )

        logger.info("Assigning unique IDs")
        allTests = extendedSuite.test_cases
        for idx, tc in enumerate(allTests or [], start=1):
            tc.id = f"TC{idx:03d}"

        finalTestSuite = TestSuite(
            title="Final Test Suite", test_cases=allTests
        )

        # Prepare gaps with related test IDs
        final_gaps_analysis = []
        for item in gaps_with_tests:
            related_test_ids = [tc.id for tc in item["tests"]]
            final_gaps_analysis.append(
                {"gap": item["gap"], "related_tests": related_test_ids}
            )

        return finalTestSuite, final_gaps_analysis

    def format_markdown_output(
        self, finalTestSuite: TestSuite, final_gaps_analysis: list[dict]
    ) -> tuple[str, str]:
        current_date = datetime.now().strftime("%Y-%m-%d")
        header = f"""# Test Suite: Token Access & Management\n*Generated on: {current_date}*\n\n"""

        # Requirements Analysis Section
        requirements_md = "## Requirements Analysis\n\n"
        if not final_gaps_analysis:
            requirements_md += "No gaps identified.\n"
        else:
            for i, entry in enumerate(final_gaps_analysis or [], start=1):
                requirements_md += f"### Gap {i}\n"
                requirements_md += (
                    f"- **Description:** {entry['gap']['description']}\n"
                )
                requirements_md += f"- **Suggested Clarification:** {entry['gap']['suggested_clarification']}\n"
                requirements_md += f"- **Confidence Level:** {entry['gap']['confidence_level']}\n"
                if entry["related_tests"]:
                    requirements_md += (
                        "- **Related Test Cases:** "
                        + ", ".join(entry["related_tests"])
                        + "\n"
                    )
                else:
                    requirements_md += "- **Related Test Cases:** None\n"
                requirements_md += "\n"

        # Test Suite Section
        suite_md = format_test_suite_to_markdown(finalTestSuite)

        full_md = header + requirements_md + suite_md

        return full_md, requirements_md

    async def process_input(self, input_data: str) -> tuple[str, str]:
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

        logger.info("Validating input data")
        dspy.settings.configure(lm=self.lm_validator)
        validator = UserStoryValidator()
        result = validator(story=input_data)
        if not result.is_valid:
            return (
                result.error_message,
                "",
            )  # Return error message and empty string for requirements section on failure

        logger.info("Generating test suite with edge cases")
        finalTestSuite, final_gaps_analysis = self.generate_test_cases(
            input_data
        )
        logger.info("Formatting output")

        full_md, requirements_section = self.format_markdown_output(
            finalTestSuite=finalTestSuite,
            final_gaps_analysis=final_gaps_analysis,
        )
        return full_md, requirements_section

    def read_file(self, file_path: str) -> str:
        """Read content from a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError as err:
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(
                f"The file '{file_path}' was not found"
            ) from err
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise OSError(
                f"Failed to read file '{file_path}': {str(e)}"
            ) from e

    async def run(
        self, file_path: str = None, output_path: str = "test_cases.md"
    ):
        """Run the test case generation process."""
        try:
            logger.info("Reading input")
            if file_path:
                input_data = self.read_file(file_path)
            elif not sys.stdin.isatty():
                input_data = sys.stdin.read()
            else:
                raise ValueError(
                    "Please provide input via file (--file) or stdin"
                )

            logger.info("Processing input and generating test cases")
            full_md, requirements_section = await self.process_input(
                input_data
            )

            logger.info("Writing test cases to output file")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_md)

            logger.info("Writing requirements analysis to separate file")
            with open("requirements_analysis.md", "w", encoding="utf-8") as f:
                f.write(requirements_section)

            logger.info(f"Test cases written to {output_path}")
            logger.info(
                "Requirements analysis written to requirements_analysis.md"
            )
            print(
                f"Test cases generated successfully. Output written to {output_path}"
            )
            print("Requirements analysis written to requirements_analysis.md")
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
            raise


async def main():
    """Main application entry point."""
    _ = load_dotenv()

    parser = argparse.ArgumentParser(
        description="User Story to Test Case Converter"
    )
    parser.add_argument(
        "--file", type=str, help="Path to input file containing user story"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_cases.md",
        help="Output file path for test cases",
    )
    args = parser.parse_args()

    app = TestCaseGeneratorApp()

    try:
        await app.run(file_path=args.file, output_path=args.output)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
