import argparse
import asyncio
import sys
from datetime import datetime

import dspy
from dotenv import load_dotenv
from loguru import logger

from tc_definition import TestCaseGenerator
from validator import UserStoryValidator


class TestCaseGenerationError(Exception):
    """Exception raised for errors in the test case generation process."""

    pass


async def generate_test_cases(user_story: str) -> str:
    """Generate test cases using an LLM based on the user story provided."""
    try:
        logger.info("Starting test case generation")
        start_time = datetime.now()

        lm = dspy.LM(
            model="openai/gpt-4o-mini",
            max_tokens=1000,
            temperature=0.0,
        )
        dspy.settings.configure(lm=lm)

        generator = TestCaseGenerator()
        prediction = generator(user_story=user_story)

        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Test cases generated successfully in {execution_time} seconds"
        )

        return prediction.test_cases

    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise TestCaseGenerationError(
            f"Failed to generate test cases: {str(e)}"
        ) from e


def format_markdown_output(test_cases: str) -> str:
    """Format the output in proper Markdown"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    header = f"""# Test Suite: Token Access & Management
*Generated on: {current_date}*

"""
    return header + test_cases


async def process_input(input_data: str) -> str:
    """Process input and generate test cases"""
    try:
        logger.info("Validating input data")
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

        validator = UserStoryValidator()
        result = validator(story=input_data)
        if not result.is_valid:
            return result.error_message

        logger.info("Processing user story input")

        logger.info("Generating test cases")
        test_cases = await generate_test_cases(input_data)

        logger.info("Formatting output")
        formatted_output = format_markdown_output(test_cases)

        return formatted_output

    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        raise


def read_file(file_path: str) -> str:
    """Read content from a file"""
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
        raise OSError(f"Failed to read file '{file_path}': {str(e)}") from e


async def main():
    """Main application entry point"""
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

    try:
        logger.info("Reading input")
        if args.file:
            input_data = read_file(args.file)
        elif not sys.stdin.isatty():
            input_data = sys.stdin.read()
        else:
            raise ValueError("Please provide input via file (--file) or stdin")

        logger.info("processing input and generating test cases")
        result = await process_input(input_data)

        logger.info("Writing test cases to output file")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)

        logger.info(f"Test cases written to {args.output}")
        print(
            f"Test cases generated successfully. Output written to {args.output}"
        )

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
