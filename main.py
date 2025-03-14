import argparse
import asyncio
import sys
from datetime import datetime
import os

import dspy
from dotenv import load_dotenv
from loguru import logger

from src.validator import UserStoryValidator
from src.testcase_generator import TestCaseGenerator, TestSuite


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

    def generate_test_cases(self, user_story: str) -> TestSuite:
        logger.info("Starting test case generation")
        start_time = datetime.now()
        dspy.settings.configure(lm=self.lm_generator)
        generator = TestCaseGenerator()
        test_suite = generator(user_story=user_story)
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Test suite generated successfully in {execution_time} seconds"
        )
        return test_suite

    def format_markdown_output(self, test_cases: str) -> str:
        """Format the output in proper Markdown."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        header = f"""# Test Suite: Token Access & Management
*Generated on: {current_date}*

"""
        return header + test_cases

    async def process_input(self, input_data: str) -> str:
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

        logger.info("Validating input data")
        dspy.settings.configure(lm=self.lm_validator)
        validator = UserStoryValidator()
        result = validator(story=input_data)
        if not result.is_valid:
            return result.error_message

        logger.info("Generating test suite")
        test_suite = self.generate_test_cases(input_data)
        logger.info("Formatting output")
        from src.testcase_generator import format_test_suite_to_markdown

        formatted_output = format_test_suite_to_markdown(test_suite)
        return formatted_output

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
            result = await self.process_input(input_data)

            logger.info("Writing test cases to output file")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

            logger.info(f"Test cases written to {output_path}")
            print(
                f"Test cases generated successfully. Output written to {output_path}"
            )
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
        "--output", type=str, default="test_cases.md", help="Output file path"
    )
    args = parser.parse_args()

    # Create app instance with default or custom models
    app = (
        TestCaseGeneratorApp()
    )  # Defaults to gpt-3.5-turbo for validator, gpt-4o-mini for generator
    # Example with custom models: app = TestCaseGeneratorApp(validator_model="openai/gpt-4", generator_model="openai/gpt-4o")

    try:
        await app.run(file_path=args.file, output_path=args.output)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
