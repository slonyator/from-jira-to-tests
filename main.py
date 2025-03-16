import argparse
import asyncio
import os
import sys

import dspy
from dotenv import load_dotenv
from loguru import logger

from src.gap_analyzer import (
    RequirementGapAnalyzer,
    ClarificationTestCaseGenerator,
)
from src.suite_generator import (
    TestCaseGenerator,
    EdgeCaseGenerator,
    TestSuite,
    trainset,
    TestCase,
)
from src.validator import UserStoryValidator


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
    ) -> tuple[TestSuite, TestSuite, list[dict]]:
        """Generate separate test suites and gap analysis with related tests."""
        dspy.settings.configure(lm=self.lm_generator)

        logger.info("Generating functional test cases")
        test_generator = TestCaseGenerator(trainset=trainset)
        main_test_suite = test_generator.forward(user_story=user_story)
        for idx, tc in enumerate(main_test_suite.test_cases, start=1):
            tc.id = f"TC{idx:03d}"

        logger.info("Generating edge cases")
        edge_generator = EdgeCaseGenerator()
        edge_test_suite = edge_generator.forward(
            user_story=user_story, test_suite=main_test_suite
        )
        for idx, tc in enumerate(edge_test_suite.test_cases, start=1):
            tc.id = f"EC{idx:03d}"

        logger.info("Starting requirement gap analysis")
        gap_analyzer = RequirementGapAnalyzer()
        gaps_list = gap_analyzer.forward(user_story=user_story)

        logger.info("Generating additional test cases for gaps")
        clarification_generator = ClarificationTestCaseGenerator()
        gaps_with_tests = []
        current_id = 1
        for gap_dict in gaps_list or []:
            description = gap_dict.get("description", "")
            clarification = gap_dict.get("suggested_clarification", "")
            confidence_level = gap_dict.get("confidence_level", "")
            logger.info(f"Generating test cases for gap: {description}")
            additional_tests_json = clarification_generator.forward(
                user_story=user_story, clarification=clarification
            )
            additional_tests_pydantic = [
                TestCase(**tc) for tc in additional_tests_json
            ]
            for tc in additional_tests_pydantic:
                tc.id = f"GT{current_id:03d}"
                current_id += 1
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

        return main_test_suite, edge_test_suite, gaps_with_tests

    def format_test_cases(self, test_cases: list[TestCase], title: str) -> str:
        """Format a list of test cases into Markdown."""
        md = f"# {title}\n\n"
        if not test_cases:
            md += "No test cases generated.\n"
        else:
            for tc in test_cases:
                md += f"## {tc.id}: {tc.title}\n"
                md += f"- **Module:** {tc.module}\n"
                md += f"- **Priority:** {tc.priority}\n"
                md += f"- **Type:** {tc.type}\n"
                md += "- **Prerequisites:**\n"
                for prereq in tc.prerequisites:
                    md += f"  - {prereq}\n"
                md += "- **Steps:**\n"
                for step in tc.steps:
                    md += f"  - {step}\n"
                md += "- **Expected Results:**\n"
                for result in tc.expected_results:
                    md += f"  - {result}\n"
                md += "\n"
        return md

    def format_additional_test_cases(self, gaps_with_tests: list[dict]) -> str:
        """Format additional test cases grouped by gap into Markdown."""
        md = "# Additional Tests for Gaps\n\n"
        if not gaps_with_tests:
            md += "No additional tests needed.\n"
        else:
            for item in gaps_with_tests:
                gap = item["gap"]
                tests = item["tests"]
                md += f"## Gap: {gap['description']}\n"
                md += f"- **Suggested Clarification:** {gap['suggested_clarification']}\n"
                md += f"- **Confidence Level:** {gap['confidence_level']}\n\n"
                for tc in tests:
                    md += f"### {tc.id}: {tc.title}\n"
                    md += f"- **Module:** {tc.module}\n"
                    md += f"- **Priority:** {tc.priority}\n"
                    md += f"- **Type:** {tc.type}\n"
                    md += "- **Prerequisites:**\n"
                    for prereq in tc.prerequisites:
                        md += f"  - {prereq}\n"
                    md += "- **Steps:**\n"
                    for step in tc.steps:
                        md += f"  - {step}\n"
                    md += "- **Expected Results:**\n"
                    for result in tc.expected_results:
                        md += f"  - {result}\n"
                    md += "\n"
        return md

    def format_gap_analysis(self, gaps_with_tests: list[dict]) -> str:
        """Format gap analysis findings into Markdown."""
        md = "# Gap Analysis\n\n"
        if not gaps_with_tests:
            md += "No gaps identified.\n"
        else:
            for i, item in enumerate(gaps_with_tests, start=1):
                gap = item["gap"]
                related_tests = [tc.id for tc in item["tests"]]
                md += f"## Gap {i}\n"
                md += f"- **Description:** {gap['description']}\n"
                md += f"- **Suggested Clarification:** {gap['suggested_clarification']}\n"
                md += f"- **Confidence Level:** {gap['confidence_level']}\n"
                if related_tests:
                    md += (
                        "- **Related Test Cases:** "
                        + ", ".join(related_tests)
                        + "\n"
                    )
                else:
                    md += "- **Related Test Cases:** None\n"
                md += "\n"
        return md

    async def process_input(self, input_data: str):
        """Process input and generate separate Markdown files."""
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

        logger.info("Validating input data")
        dspy.settings.configure(lm=self.lm_validator)
        validator = UserStoryValidator()
        result = validator(story=input_data)
        if not result.is_valid:
            logger.info(f"Error: {result.error_message}")
            logger.info("User story is invalid, no test cases generated.")
            return

        logger.info("Generating test suite components")
        main_test_suite, edge_test_suite, gaps_with_tests = (
            self.generate_test_cases(input_data)
        )

        logger.info("Format test cases to markdown")
        main_md = self.format_test_cases(
            main_test_suite.test_cases, "Main Test Cases"
        )

        logger.info("Format edge case tests to markdown")
        edge_md = self.format_test_cases(
            edge_test_suite.test_cases, "Edge Case Tests"
        )

        logger.info("Format additional test cases to markdown")
        additional_md = self.format_additional_test_cases(gaps_with_tests)

        logger.info("Format gap analysis to markdown")
        gap_analysis_md = self.format_gap_analysis(gaps_with_tests)

        logger.info("Ensure output directory exists")
        os.makedirs("./output", exist_ok=True)

        logger.info("Saving output files")
        with open("./output/main_test_cases.md", "w", encoding="utf-8") as f:
            f.write(main_md)
        with open("./output/edge_case_tests.md", "w", encoding="utf-8") as f:
            f.write(edge_md)
        with open(
            "./output/additional_gap_tests.md", "w", encoding="utf-8"
        ) as f:
            f.write(additional_md)
        with open("./output/gap_analysis.md", "w", encoding="utf-8") as f:
            f.write(gap_analysis_md)

        logger.info("Test cases and analysis generated successfully.")
        logger.info("Files saved in ./output directory:")
        logger.info("- main_test_cases.md")
        logger.info("- edge_case_tests.md")
        logger.info("- gap_analysis.md")
        logger.info("- additional_gap_tests.md")

    async def run(self, file_path: str = None):
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
            await self.process_input(input_data)
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
            raise

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


async def main():
    """Main application entry point."""
    _ = load_dotenv()
    parser = argparse.ArgumentParser(
        description="User Story to Test Case Converter"
    )
    parser.add_argument(
        "--file", type=str, help="Path to input file containing user story"
    )
    args = parser.parse_args()
    app = TestCaseGeneratorApp()
    try:
        await app.run(file_path=args.file)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
