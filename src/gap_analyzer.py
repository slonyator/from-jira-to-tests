import json
from loguru import logger
from pydantic import BaseModel
import dspy


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
    """Generate test cases based on clarified requirement."""

    user_story = dspy.InputField(desc="The original user story")
    clarification = dspy.InputField(desc="The clarified requirement")
    test_cases = dspy.OutputField(
        desc="JSON list of {'id': str,'title': str,'module': str,'priority': str,'type': str,'prerequisites': list[str],'steps': list[str],'expected_results': list[str]}"
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

    def forward(self, user_story: str, clarification: str) -> list[dict]:
        try:
            prediction = self.generate(
                user_story=user_story, clarification=clarification
            )
            test_cases_list = json.loads(prediction.test_cases)
            if isinstance(test_cases_list, list):
                return test_cases_list
            else:
                raise ValueError("Test cases are not a list")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to generate test cases: {e}")
            return []
