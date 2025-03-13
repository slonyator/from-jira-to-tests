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
