import pytest
from pydantic import ValidationError

from dspy import Prediction

from src.testcase_generator import TestCase, TestSuite, TestCaseGenerator


class TestTestCase:
    def test_testcase_creation_success(self):
        """Test successful creation of a TestCase with all required fields."""
        testcase = TestCase(
            id="TC001",
            module="Login",
            priority="High",
            type="Functional",
            steps=["Step 1", "Step 2"],
            expected_results=["Result 1", "Result 2"],
        )

        default_value = []

        assert testcase.id == "TC001"
        assert testcase.module == "Login"
        assert testcase.priority == "High"
        assert testcase.type == "Functional"
        assert testcase.prerequisites == default_value
        assert testcase.steps == ["Step 1", "Step 2"]
        assert testcase.expected_results == ["Result 1", "Result 2"]

    def test_testcase_missing_field(self):
        """Test that ValidationError is raised when a required field is missing."""
        with pytest.raises(ValidationError):
            TestCase(
                id="TC001",
                module="Login",
                priority="High",
                type="Functional",
                steps=["Step 1", "Step 2"],
                # missing expected_results
            )

    def test_testcase_default_prerequisites(self):
        """Test that prerequisites defaults to an empty list."""
        testcase = TestCase(
            id="TC001",
            module="Login",
            priority="High",
            type="Functional",
            steps=["Step 1", "Step 2"],
            expected_results=["Result 1", "Result 2"],
        )
        assert testcase.prerequisites == []


class TestTestSuite:
    def test_testsuite_creation_success(self):
        """Test successful creation of a TestSuite with a title and test cases."""
        testcase = TestCase(
            id="TC001",
            module="Login",
            priority="High",
            type="Functional",
            steps=["Step 1", "Step 2"],
            expected_results=["Result 1", "Result 2"],
        )
        testsuite = TestSuite(
            title="Login Functionality", test_cases=[testcase]
        )
        assert testsuite.title == "Login Functionality"
        assert testsuite.test_cases == [testcase]

    def test_testsuite_missing_title(self):
        """Test that ValidationError is raised when title is missing."""
        with pytest.raises(ValidationError):
            TestSuite(
                test_cases=[]
                # missing title
            )

    def test_testsuite_default_test_cases(self):
        """Test that test_cases defaults to an empty list."""
        testsuite = TestSuite(title="Empty Suite")
        assert testsuite.title == "Empty Suite"
        assert testsuite.test_cases == []


class TestTestCaseGenerator:
    def test_forward_success(self, mocker):
        """Test the forward method with a valid user story, mocking dspy.Predict."""
        generator = TestCaseGenerator()
        mock_generate = mocker.patch.object(
            generator.generate,
            "forward",
            return_value=Prediction(test_cases="Mocked test cases"),
        )

        user_story = "As a user, I want to log in."
        result = generator.forward(user_story)

        assert result.test_cases == "Mocked test cases"
        mock_generate.assert_called_once_with(user_story=user_story)

    def test_forward_with_empty_story(self, mocker):
        """Test the forward method with an empty user story, mocking dspy.Predict."""
        generator = TestCaseGenerator()
        mock_generate = mocker.patch.object(
            generator.generate,
            "forward",
            return_value=Prediction(test_cases=""),
        )

        user_story = ""
        result = generator.forward(user_story)

        assert result.test_cases == ""
        mock_generate.assert_called_once_with(user_story=user_story)
