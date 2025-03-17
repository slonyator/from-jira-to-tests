import json

import dspy
from loguru import logger
from pydantic import BaseModel, ValidationError

from src.suite_generator import TestCase


class RequirementGap(BaseModel):
    description: str
    suggested_clarification: str
    confidence_level: str


class GapAnalysisSignature(dspy.Signature):
    """Analyze user story for missing or ambiguous requirements."""

    user_story = dspy.InputField(desc="The user story to analyze")
    gaps = dspy.OutputField(
        desc="JSON list of {'description': str, 'suggested_clarification': str, 'confidence_level': str}"
    )


class ClarificationToTestCasesSignature(dspy.Signature):
    """Generate test cases based on clarified requirement. Output must be a valid JSON list of test cases."""

    user_story = dspy.InputField(desc="The original user story")
    clarification = dspy.InputField(desc="The clarified requirement")
    test_cases = dspy.OutputField(
        desc="JSON list of {'id': str, 'title': str, 'module': str, 'priority': str, 'type': str, 'prerequisites': list[str], 'steps': list[str], 'expected_results': list[str]}"
    )


class RequirementGapAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(GapAnalysisSignature)

    def forward(self, user_story: str) -> list[dict]:
        try:
            prediction = self.analyze(user_story=user_story)
            logger.info("Parse JSON into a list of dictionaries")
            gaps_list = json.loads(prediction.gaps)
            logger.info("Validate each gap against the Pydantic model")
            validated_gaps = [
                RequirementGap(**gap).model_dump() for gap in gaps_list
            ]
            return validated_gaps
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(
                f"Failed to analyze gaps: {e}. Raw output: {prediction.gaps}"
            )
            return []
        except Exception as e:
            logger.error(f"Unexpected error in gap analysis: {e}")
            return []


class ClarificationTestCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(ClarificationToTestCasesSignature)

    def forward(self, user_story: str, clarification: str) -> list[dict]:
        try:
            prediction = self.generate(
                user_story=user_story, clarification=clarification
            )
            raw_output = prediction.test_cases
            logger.info("Parse JSON into a list of dictionaries")
            test_cases_list = json.loads(raw_output)
            logger.info("Validate each test case against the Pydantic model")
            validated_test_cases = [
                TestCase(**tc).dict() for tc in test_cases_list
            ]
            return validated_test_cases
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(
                f"Failed to generate test cases: {e}. Problematic raw output: {raw_output}"
            )
            return []
        except Exception as e:
            logger.error(f"Unexpected error in test case generation: {e}")
            return []
