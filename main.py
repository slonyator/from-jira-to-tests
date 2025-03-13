from datetime import datetime

import dspy
from loguru import logger

from tc_definition import TestCaseGenerator


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

        logger.info("Processing user story input")

        logger.info("Generating test cases")
        test_cases = await generate_test_cases(input_data)

        logger.info("Formatting output")
        formatted_output = format_markdown_output(test_cases)

        return formatted_output

    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        raise
