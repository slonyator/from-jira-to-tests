import json

import pytest
from pydantic import ValidationError

from dspy import Prediction

from src.edgecase_generator import (
    TestCase,
    TestSuite,
    EdgeCasePredictor,
    EdgeCaseGeneratorModule,
    EdgeCaseGenerator,
    EdgeCasePrediction,
    format_test_suite_to_markdown,
)


class TestTestCase:
    def test_testcase_creation_success(self):
        """Test successful creation of a TestCase with all required fields."""
        testcase = TestCase(
            id="EXT-001",
            title="Token Creation",
            module="Token Management",
            priority="High",
            type="Functional",
            steps=["Step 1", "Step 2"],
            expected_results=["Result 1", "Result 2"],
        )
        default_value = []
        assert testcase.id == "EXT-001"
        assert testcase.title == "Token Creation"
        assert testcase.module == "Token Management"
        assert testcase.priority == "High"
        assert testcase.type == "Functional"
        assert testcase.prerequisites == default_value
        assert testcase.steps == ["Step 1", "Step 2"]
        assert testcase.expected_results == ["Result 1", "Result 2"]

    def test_testcase_missing_fields(self):
        """Test that ValidationError is raised when a required field is missing."""
        with pytest.raises(ValidationError):
            TestCase(
                id="EXT-001",
                module="Token Management",
                priority="High",
                type="Functional",
                steps=["Step 1"],
            )  # Missing 'title' and 'expected_results'

    def test_testcase_default_prerequisites(self):
        """Test that prerequisites defaults to an empty list."""
        testcase = TestCase(
            id="EXT-001",
            title="Token Creation",
            module="Token Management",
            priority="High",
            type="Functional",
            steps=["Step 1"],
            expected_results=["Result 1"],
        )
        assert testcase.prerequisites == []


class TestTestSuite:
    def test_testsuite_creation_success(self):
        """Test successful creation of a TestSuite with a title and test cases."""
        testcase = TestCase(
            id="EXT-001",
            title="Token Creation",
            module="Token Management",
            priority="High",
            type="Functional",
            steps=["Step 1"],
            expected_results=["Result 1"],
        )
        testsuite = TestSuite(title="Token Suite", test_cases=[testcase])
        assert testsuite.title == "Token Suite"
        assert testsuite.test_cases == [testcase]

    def test_testsuite_missing_title(self):
        """Test that ValidationError is raised when title is missing."""
        with pytest.raises(ValidationError):
            TestSuite(test_cases=[])

    def test_testsuite_default_test_cases(self):
        """Test that test_cases defaults to an empty list."""
        testsuite = TestSuite(title="Empty Suite")
        assert testsuite.title == "Empty Suite"
        assert testsuite.test_cases == []


class TestEdgeCasePredictor:
    def test_forward_success(self, mocker):
        """Test successful prediction with valid JSON output."""
        predictor = EdgeCasePredictor()
        mock_predict = mocker.patch.object(
            predictor.predict,
            "__call__",
            return_value=Prediction(
                prediction='{"needs_edge_cases": true, "reason": "Network issues possible"}'
            ),
        )
        result = predictor.forward("User story text")
        assert result.needs_edge_cases is True
        assert result.reason == "Network issues possible"
        mock_predict.assert_called_once_with(user_story="User story text")

    def test_forward_json_error(self, mocker):
        """Test that ValueError is raised with invalid JSON."""
        predictor = EdgeCasePredictor()
        mocker.patch.object(
            predictor.predict,
            "__call__",
            return_value=Prediction(prediction="invalid json"),
        )
        with pytest.raises(
            ValueError, match="Failed to parse prediction JSON"
        ):
            predictor.forward("User story text")


class TestEdgeCaseGeneratorModule:
    def test_forward_success(self, mocker):
        """Test successful edge case generation with valid JSON output."""
        generator_module = EdgeCaseGeneratorModule()
        edge_case_json = {
            "edge_cases": [
                {
                    "id": "EDGE-001",
                    "title": "Network Failure",
                    "module": "Token Management",
                    "priority": "Medium",
                    "type": "Error Handling",
                    "prerequisites": ["Network throttling"],
                    "steps": ["Create token"],
                    "expected_results": ["Error handled"],
                }
            ]
        }
        mock_generate = mocker.patch.object(
            generator_module.generate,
            "__call__",
            return_value=Prediction(edge_cases=json.dumps(edge_case_json)),
        )
        result = generator_module.forward("User story", "Reason", "{}")
        assert len(result) == 1
        assert result[0]["id"] == "EDGE-001"
        assert result[0]["title"] == "Network Failure"
        mock_generate.assert_called_once_with(
            user_story="User story", reason="Reason", existing_test_suite="{}"
        )

    def test_forward_missing_edge_cases_key(self, mocker):
        """Test that ValueError is raised when 'edge_cases' key is missing."""
        generator_module = EdgeCaseGeneratorModule()
        mock_generate = mocker.patch.object(
            generator_module.generate,
            "__call__",
            return_value=Prediction(edge_cases='{"wrong_key": []}'),
        )
        with pytest.raises(
            ValueError, match="Missing 'edge_cases' key in prediction"
        ):
            generator_module.forward("User story", "Reason", "{}")

    def test_forward_missing_title(self, mocker):
        """Test that ValueError is raised when an edge case lacks a 'title'."""
        generator_module = EdgeCaseGeneratorModule()
        edge_case_json = {
            "edge_cases": [
                {
                    "id": "EDGE-001",
                    "module": "Token Management",
                    "priority": "Medium",
                    "type": "Error Handling",
                    "steps": ["Create token"],
                    "expected_results": ["Error handled"],
                }
            ]
        }
        mock_generate = mocker.patch.object(
            generator_module.generate,
            "__call__",
            return_value=Prediction(edge_cases=json.dumps(edge_case_json)),
        )
        with pytest.raises(
            ValueError,
            match="Each edge case must be a JSON object with a 'title' field",
        ):
            generator_module.forward("User story", "Reason", "{}")


class TestEdgeCaseGenerator:
    def test_needs_edge_cases_success(self, mocker):
        """Test needs_edge_cases with mocked predictor."""
        generator = EdgeCaseGenerator()
        mock_forward = mocker.patch.object(
            generator.predictor,
            "forward",
            return_value=EdgeCasePrediction(
                needs_edge_cases=True, reason="Test reason"
            ),
        )
        result = generator.needs_edge_cases("User story")
        assert result.needs_edge_cases is True
        assert result.reason == "Test reason"
        mock_forward.assert_called_once_with("User story")

    def test_forward_no_edge_cases_needed(self, mocker):
        """Test forward when no edge cases are needed."""
        generator = EdgeCaseGenerator()
        initial_suite = TestSuite(title="Test Suite", test_cases=[])
        mocker.patch.object(
            generator.predictor,
            "forward",
            return_value=EdgeCasePrediction(
                needs_edge_cases=False, reason="No issues"
            ),
        )
        result = generator.forward("User story", initial_suite)
        assert result == initial_suite
        assert len(result.test_cases) == 0

    def test_forward_with_edge_cases(self, mocker):
        """Test forward with edge cases added, avoiding duplicates."""
        generator = EdgeCaseGenerator()
        initial_suite = TestSuite(
            title="Test Suite",
            test_cases=[
                TestCase(
                    id="EXT-001",
                    title="Initial Test",
                    module="Test",
                    priority="High",
                    type="Functional",
                    steps=["Step 1"],
                    expected_results=["Result 1"],
                )
            ],
        )
        mocker.patch.object(
            generator.predictor,
            "forward",
            return_value=EdgeCasePrediction(
                needs_edge_cases=True, reason="Network issues"
            ),
        )
        edge_case_json = {
            "edge_cases": [
                {
                    "id": "EXT-001",  # Duplicate ID
                    "title": "Duplicate Test",
                    "module": "Test",
                    "priority": "Medium",
                    "type": "Error",
                    "steps": ["Step A"],
                    "expected_results": ["Result A"],
                },
                {
                    "id": "EDGE-001",
                    "title": "Network Failure",
                    "module": "Test",
                    "priority": "Medium",
                    "type": "Error",
                    "steps": ["Step B"],
                    "expected_results": ["Result B"],
                },
            ]
        }
        mocker.patch.object(
            generator.generator,
            "forward",
            return_value=edge_case_json["edge_cases"],
        )
        result = generator.forward("User story", initial_suite)
        assert (
            len(result.test_cases) == 2
        )  # Only one new case added due to duplicate ID
        assert result.test_cases[1].id == "EDGE-001"
        assert result.test_cases[1].title == "Network Failure"


class TestFormatTestSuiteToMarkdown:
    def test_format_empty_suite(self):
        """Test formatting an empty test suite."""
        suite = TestSuite(title="Empty Suite")
        result = format_test_suite_to_markdown(suite)
        assert result == "## Empty Suite\n\n## No Test Cases Generated\n"

    def test_format_with_test_cases(self):
        """Test formatting a suite with test cases."""
        suite = TestSuite(
            title="Test Suite",
            test_cases=[
                TestCase(
                    id="EXT-001",
                    title="Token Test",
                    module="Token Management",
                    priority="High",
                    type="Functional",
                    prerequisites=["Pre 1"],
                    steps=["Step 1"],
                    expected_results=["Result 1"],
                )
            ],
        )
        result = format_test_suite_to_markdown(suite)
        expected = (
            "## Test Suite\n\n"
            "### Test Case EXT-001: Token Test\n"
            "**Module:** Token Management\n"
            "**Priority:** High\n"
            "**Type:** Functional\n"
            "#### Prerequisites\n"
            "- Pre 1\n"
            "#### Test Steps\n"
            "1. Step 1\n"
            "#### Expected Results\n"
            "- Result 1\n\n"
        )
        assert result == expected
