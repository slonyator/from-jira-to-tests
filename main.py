import argparse
import asyncio
import os
import sys

import dspy
from dotenv import load_dotenv
from loguru import logger

from src.output_formatter import OutputFormatter
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
        self.output_formatter = OutputFormatter()

    def get_test_key(self, test_case):
        """Create a unique key based on steps and expected results."""
        steps_str = "|".join(test_case.steps)
        expected_str = "|".join(test_case.expected_results)
        return f"{steps_str}|{expected_str}"

    def generate_test_cases(
        self, user_story: str
    ) -> tuple[TestSuite, TestSuite, list[dict]]:
        dspy.settings.configure(lm=self.lm_generator)
        unique_test_keys = set()

        logger.info("Generating functional test cases")
        test_generator = TestCaseGenerator(trainset=trainset)
        main_test_suite = test_generator.forward(user_story=user_story)
        main_tests = []
        for tc in main_test_suite.test_cases:
            key = self.get_test_key(tc)
            logger.info("Ensure test case is unique")
            if key not in unique_test_keys:
                main_tests.append(tc)
                unique_test_keys.add(key)
        main_test_suite.test_cases = main_tests

        logger.info("Generating edge cases")
        edge_generator = EdgeCaseGenerator()
        edge_test_suite = edge_generator.forward(
            user_story=user_story, test_suite=main_test_suite
        )
        edge_tests = []
        for tc in edge_test_suite.test_cases:
            key = self.get_test_key(tc)
            logger.info("Ensure test case is unique")
            if key not in unique_test_keys:
                edge_tests.append(tc)
                unique_test_keys.add(key)
        edge_test_suite.test_cases = edge_tests

        logger.info("Starting requirement gap analysis")
        gap_analyzer = RequirementGapAnalyzer()
        gaps_list = gap_analyzer.forward(user_story=user_story)

        logger.info("Generating additional test cases for gaps")
        clarification_generator = ClarificationTestCaseGenerator()
        gaps_with_tests = []
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
            unique_additional_tests = []
            for tc in additional_tests_pydantic:
                key = self.get_test_key(tc)
                logger.info("Ensure test case is unique")
                if key not in unique_test_keys:
                    unique_additional_tests.append(tc)
                    unique_test_keys.add(key)
                else:
                    logger.info(
                        f"Skipping duplicate test for gap '{description}': {tc.title}"
                    )
            gaps_with_tests.append(
                {
                    "gap": {
                        "description": description,
                        "suggested_clarification": clarification,
                        "confidence_level": confidence_level,
                    },
                    "tests": unique_additional_tests,
                }
            )

        logger.info("Assigning unique IDs to test cases")
        current_id = 1
        for tc in main_test_suite.test_cases:
            tc.id = f"TC{current_id:03d}"
            current_id += 1
        for tc in edge_test_suite.test_cases:
            tc.id = f"EC{current_id:03d}"
            current_id += 1
        for item in gaps_with_tests:
            for tc in item["tests"]:
                tc.id = f"GT{current_id:03d}"
                current_id += 1

        return main_test_suite, edge_test_suite, gaps_with_tests

    async def process_input(self, input_data: str):
        """Process input and generate separate Markdown files."""
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

        logger.info("Validating input data")
        dspy.settings.configure(lm=self.lm_validator)
        validator = UserStoryValidator()
        result = validator(story=input_data)
        if not result.is_valid:
            logger.error(f"{result.error_message}")
            logger.info("User story is invalid, no test cases generated.")
            return

        logger.info("Generating test suite components")
        main_test_suite, edge_test_suite, gaps_with_tests = (
            self.generate_test_cases(input_data)
        )

        logger.info("Format test cases to markdown")
        main_md = self.output_formatter.format_test_cases(
            main_test_suite.test_cases, "Main Test Cases"
        )

        logger.info("Format edge case tests to markdown")
        edge_md = self.output_formatter.format_test_cases(
            edge_test_suite.test_cases, "Edge Case Tests"
        )

        logger.info("Format additional test cases to markdown")
        additional_md = self.output_formatter.format_additional_test_cases(
            gaps_with_tests
        )

        logger.info("Format gap analysis to markdown")
        gap_analysis_md = self.output_formatter.format_gap_analysis(
            gaps_with_tests
        )

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
        logger.info(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
