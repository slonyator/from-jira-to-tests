import dspy
from dspy import Signature, Module, InputField, OutputField, Prediction
from loguru import logger


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
        self.check_ambiguity = dspy.ChainOfThought(AmbiguitySignature)
        self.check_completeness = dspy.ChainOfThought(CompletenessSignature)
        self.check_contradictions = dspy.ChainOfThought(ContradictionSignature)

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
