import pytest
from dspy import Prediction
from loguru import logger

from src.validator import UserStoryValidator


class TestUserStoryValidator:
    @pytest.fixture
    def validator(self):
        """Fixture to provide a fresh UserStoryValidator instance for each test."""
        return UserStoryValidator()

    def test_valid_story(self, validator, mocker):
        """Test a valid user story where all checks pass."""
        logger.info(
            "Mocking ChainOfThought responses to simulate a valid story"
        )
        mock_ambiguity = mocker.patch.object(
            validator.check_ambiguity,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )
        mock_completeness = mocker.patch.object(
            validator.check_completeness,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )
        mock_contradictions = mocker.patch.object(
            validator.check_contradictions,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )

        story = "As a user, I want to log in so that I can access my account."
        result = validator.forward(story)

        # Assertions
        assert result.is_valid is True
        assert result.error_message is None
        mock_ambiguity.assert_called_once_with(story=story)
        mock_completeness.assert_called_once_with(story=story)
        mock_contradictions.assert_called_once_with(story=story)

    def test_ambiguous_story(self, validator, mocker):
        """Test a story that fails the ambiguity check."""
        logger.info(
            "Mocking the ChainOfThought responses for an ambiguous story"
        )
        mock_ambiguity = mocker.patch.object(
            validator.check_ambiguity,
            "forward",
            return_value=Prediction(
                is_valid=False, error_message="Story is ambiguous"
            ),
        )
        mock_completeness = mocker.patch.object(
            validator.check_completeness, "forward"
        )
        mock_contradictions = mocker.patch.object(
            validator.check_contradictions, "forward"
        )

        story = "As a user, I want to do something."
        result = validator.forward(story)

        # Assertions
        assert result.is_valid is False
        assert "Ambiguity issue: Story is ambiguous" in result.error_message
        mock_ambiguity.assert_called_once_with(story=story)
        mock_completeness.assert_not_called()  # Should stop after ambiguity check
        mock_contradictions.assert_not_called()

    def test_incomplete_story(self, validator, mocker):
        """Test a story that fails the completeness check."""
        logger.info(
            "Mocking the ChainOfThought responses for an incomplete story"
        )
        mock_ambiguity = mocker.patch.object(
            validator.check_ambiguity,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )
        mock_completeness = mocker.patch.object(
            validator.check_completeness,
            "forward",
            return_value=Prediction(
                is_valid=False, error_message="Story is incomplete"
            ),
        )
        mock_contradictions = mocker.patch.object(
            validator.check_contradictions, "forward"
        )

        story = "I want to log in."
        result = validator.forward(story)

        # Assertions
        assert result.is_valid is False
        assert (
            "Completeness issue: Story is incomplete" in result.error_message
        )
        mock_ambiguity.assert_called_once_with(story=story)
        mock_completeness.assert_called_once_with(story=story)
        mock_contradictions.assert_not_called()

    def test_contradictory_story(self, validator, mocker):
        """Test a story that fails the contradiction check."""
        logger.info(
            "Mocking the ChainOfThought responses for a contradictory story"
        )
        mock_ambiguity = mocker.patch.object(
            validator.check_ambiguity,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )
        mock_completeness = mocker.patch.object(
            validator.check_completeness,
            "forward",
            return_value=Prediction(is_valid=True, error_message=None),
        )
        mock_contradictions = mocker.patch.object(
            validator.check_contradictions,
            "forward",
            return_value=Prediction(
                is_valid=False, error_message="Story has contradictions"
            ),
        )

        story = "As a user, I want to log in without providing credentials."
        result = validator.forward(story)

        # Assertions
        assert result.is_valid is False
        assert (
            "Contradiction issue: Story has contradictions"
            in result.error_message
        )
        mock_ambiguity.assert_called_once_with(story=story)
        mock_completeness.assert_called_once_with(story=story)
        mock_contradictions.assert_called_once_with(story=story)
