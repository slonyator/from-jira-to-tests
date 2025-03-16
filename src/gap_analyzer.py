import json
import re

import dspy
from loguru import logger
from pydantic import BaseModel


class RequirementGap(BaseModel):
    description: str
    suggested_clarification: str
    confidence_level: str


class GapAnalysisSignature(dspy.Signature):
    """Analyze user story for missing or ambiguous requirements."""

    user_story = dspy.InputField(desc="The user story to analyze")
    gaps = dspy.OutputField(
        desc="JSON list of {'description': str,'suggested_clarification': str,'confidence_level': str}"
    )


class ClarificationToTestCasesSignature(dspy.Signature):
    """Generate test cases based on clarified requirement. Output must be valid JSON with all property names in double quotes."""

    user_story = dspy.InputField(desc="The original user story")
    clarification = dspy.InputField(desc="The clarified requirement")
    test_cases = dspy.OutputField(
        desc="Valid JSON list of {'id': str,'title': str,'module': str,'priority': str,'type': str,'prerequisites': list[str],'steps': list[str],'expected_results': list[str]} - all keys must be in double quotes"
    )


class RequirementGapAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(GapAnalysisSignature)

    def forward(self, user_story: str) -> list[dict]:
        try:
            prediction = self.analyze(user_story=user_story)
            gaps_list = json.loads(prediction.gaps)
            if isinstance(gaps_list, list):
                return gaps_list
            else:
                raise ValueError("Gaps are not a list")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to analyze gaps: {e}")
            return []


class ClarificationTestCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(ClarificationToTestCasesSignature)

    def fix_unquoted_keys(self, json_str: str) -> str:
        """Fix unquoted keys in the JSON string by adding double quotes."""
        logger.info(
            "Add quotes around unquoted keys (words followed by a colon)"
        )
        fixed_str = re.sub(r'(?<!")(\w+)(?=\s*:)', r'"\1"', json_str)
        return fixed_str

    def forward(self, user_story: str, clarification: str) -> list[dict]:
        try:
            prediction = self.generate(
                user_story=user_story, clarification=clarification
            )
            raw_output = prediction.test_cases
            logger.debug(
                f"Raw test cases output: {raw_output}"
            )  # Log full raw output
            fixed_output = self.fix_unquoted_keys(raw_output)
            logger.debug(
                f"Fixed test cases output: {fixed_output}"
            )  # Log fixed output
            test_cases_list = json.loads(fixed_output)
            if isinstance(test_cases_list, list):
                return test_cases_list
            else:
                raise ValueError("Test cases are not a list")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                f"Failed to generate test cases: {e}. Problematic raw output: {raw_output}"
            )
            return []
