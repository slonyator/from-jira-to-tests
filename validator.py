import os
from dotenv import load_dotenv
import dspy
from dspy import Signature, Module, InputField, OutputField, Prediction
from loguru import logger

load_dotenv()

lm = dspy.LM("openai/gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])
dspy.settings.configure(lm=lm)


class AmbiguitySignature(Signature):
    """Determine if the user story is clear, precise, and unambiguous."""

    story = InputField(desc="The user story to validate")
    is_valid = OutputField(
        desc="Whether the story is unambiguous (true/false)"
    )
    error_message = OutputField(
        desc="Explanation if the story is ambiguous", default=None
    )


class CompletenessSignature(Signature):
    """Determine if the user story is complete with user role, goal, and benefit."""

    story = InputField(desc="The user story to validate")
    is_valid = OutputField(desc="Whether the story is complete (true/false)")
    error_message = OutputField(
        desc="Explanation if the story is incomplete", default=None
    )


class ContradictionSignature(Signature):
    """Determine if the user story has no contradictions in its requirements."""

    story = InputField(desc="The user story to validate")
    is_valid = OutputField(
        desc="Whether the story is free of contradictions (true/false)"
    )
    error_message = OutputField(
        desc="Explanation if the story has contradictions", default=None
    )


class UserStoryValidator(Module):
    """Validate a user story for ambiguity, completeness, and contradictions."""

    def __init__(self):
        super().__init__()
        self.check_ambiguity = dspy.Predict(AmbiguitySignature)
        self.check_completeness = dspy.Predict(CompletenessSignature)
        self.check_contradictions = dspy.Predict(ContradictionSignature)

    def forward(self, story):
        logger.info("Check for ambiguity")
        ambiguity_result = self.check_ambiguity(story=story)
        if not ambiguity_result.is_valid:
            return Prediction(
                is_valid=False,
                error_message=f"Ambiguity issue: {ambiguity_result.error_message}",
            )

        logger.info("Check for completeness")
        completeness_result = self.check_completeness(story=story)
        if not completeness_result.is_valid:
            return Prediction(
                is_valid=False,
                error_message=f"Completeness issue: {completeness_result.error_message}",
            )

        logger.info("Check for contradictions")
        contradiction_result = self.check_contradictions(story=story)
        if not contradiction_result.is_valid:
            return Prediction(
                is_valid=False,
                error_message=f"Contradiction issue: {contradiction_result.error_message}",
            )

        logger.info("User story is valid")
        return Prediction(is_valid=True, error_message=None)


if __name__ == "__main__":
    validator = UserStoryValidator()

    test_stories = [
        "As a bank customer, I want to withdraw cash from an ATM using my debit card so that I can access my money without visiting a branch.",
    ]

    for i, input_story in enumerate(test_stories):
        print(f"Testing story {i + 1}: {input_story}")
        result = validator(story=input_story)
        if result.is_valid:
            print("  - Valid")
        else:
            print("  - Invalid:", result.error_message)
        print()
