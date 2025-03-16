import json
import pytest

from src.suite_generator import (
    TestSuite,
    TestCase,
    EdgeCasePrediction,
    EdgeCaseGenerator,
    EdgeCaseGeneratorModule,
    EdgeCasePredictor,
)


class TestEdgeCasePredictorForward:
    def test_success(self, mocker):
        fake_prediction = type("Fake", (), {})()
        fake_prediction.prediction = json.dumps(
            {"needs_edge_cases": True, "reason": "network issues"}
        )

        predictor = EdgeCasePredictor()
        # Patch the 'predict' attribute on our predictor instance
        mocker.patch.object(predictor, "predict", return_value=fake_prediction)

        result = predictor.forward("Some user story")
        assert result.needs_edge_cases is True
        assert result.reason == "network issues"

    def test_invalid_json(self, mocker):
        fake_prediction = type("Fake", (), {})()
        fake_prediction.prediction = "not a valid json"

        predictor = EdgeCasePredictor()
        mocker.patch.object(predictor, "predict", return_value=fake_prediction)

        with pytest.raises(
            ValueError, match="Failed to parse prediction JSON"
        ):
            predictor.forward("Some user story")


class TestEdgeCaseGeneratorModuleForward:
    def test_success(self, mocker):
        edge_cases = [
            {
                "id": "EDGE-001",
                "title": "Test Edge Case",
                "module": "Module1",
                "priority": "High",
                "type": "Error Handling",
                "prerequisites": ["Prereq1"],
                "steps": ["Step1", "Step2"],
                "expected_results": ["Expected1"],
            }
        ]
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = json.dumps({"edge_cases": edge_cases})

        module = EdgeCaseGeneratorModule()
        mocker.patch.object(module, "generate", return_value=fake_response)

        result = module.forward("Some user story", "Some reason", "{}")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "EDGE-001"

    def test_missing_edge_cases_key(self, mocker):
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = json.dumps({"not_edge_cases": []})

        module = EdgeCaseGeneratorModule()
        mocker.patch.object(module, "generate", return_value=fake_response)

        with pytest.raises(
            ValueError, match="Missing 'edge_cases' key in prediction"
        ):
            module.forward("Some user story", "Some reason", "{}")

    def test_non_list(self, mocker):
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = json.dumps({"edge_cases": "not a list"})

        module = EdgeCaseGeneratorModule()
        mocker.patch.object(module, "generate", return_value=fake_response)

        with pytest.raises(ValueError, match="Edge cases must be a JSON list"):
            module.forward("Some user story", "Some reason", "{}")

    def test_missing_title(self, mocker):
        edge_cases = [
            {
                "id": "EDGE-001",
                # "title" is missing
                "module": "Module1",
                "priority": "High",
                "type": "Error Handling",
                "prerequisites": ["Prereq1"],
                "steps": ["Step1"],
                "expected_results": ["Expected1"],
            }
        ]
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = json.dumps({"edge_cases": edge_cases})

        module = EdgeCaseGeneratorModule()
        mocker.patch.object(module, "generate", return_value=fake_response)

        with pytest.raises(
            ValueError,
            match="Each edge case must be a JSON object with a 'title' field",
        ):
            module.forward("Some user story", "Some reason", "{}")

    def test_invalid_json(self, mocker):
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = "not json"

        module = EdgeCaseGeneratorModule()
        mocker.patch.object(module, "generate", return_value=fake_response)

        with pytest.raises(
            ValueError, match="Failed to parse edge cases JSON"
        ):
            module.forward("Some user story", "Some reason", "{}")


class TestEdgeCaseGeneratorForward:
    def test_no_edge_cases_needed(self, mocker):
        generator = EdgeCaseGenerator()

        fake_prediction = EdgeCasePrediction(
            needs_edge_cases=False, reason="No issues"
        )
        mocker.patch.object(
            generator.predictor, "forward", return_value=fake_prediction
        )

        test_suite = TestSuite(
            title="Suite",
            test_cases=[
                TestCase(
                    id="TC-001",
                    title="Existing Test",
                    module="Module1",
                    priority="High",
                    type="Functional",
                    prerequisites=[],
                    steps=["Step1"],
                    expected_results=["Result1"],
                )
            ],
        )

        result_suite = generator.forward("Some user story", test_suite)
        # Expect the test suite to remain unchanged.
        assert len(result_suite.test_cases) == 1
        assert result_suite.test_cases[0].id == "TC-001"

    def test_with_edge_cases(self, mocker):
        generator = EdgeCaseGenerator()

        fake_prediction = EdgeCasePrediction(
            needs_edge_cases=True, reason="Edge needed for network issues"
        )
        mocker.patch.object(
            generator.predictor, "forward", return_value=fake_prediction
        )

        edge_cases = [
            {
                "id": "EDGE-001",
                "title": "Edge Case 1",
                "module": "ModuleA",
                "priority": "Medium",
                "type": "Error Handling",
                "prerequisites": [],
                "steps": ["Step A"],
                "expected_results": ["Result A"],
            },
            {
                "id": "EDGE-002",
                "title": "Edge Case 2",
                "module": "ModuleB",
                "priority": "Low",
                "type": "Error Handling",
                "prerequisites": [],
                "steps": ["Step B"],
                "expected_results": ["Result B"],
            },
        ]
        fake_response = type("Fake", (), {})()
        fake_response.edge_cases = json.dumps({"edge_cases": edge_cases})
        # Patch the generator module forward method to return our list of edge cases.
        mocker.patch.object(
            generator.generator, "forward", return_value=edge_cases
        )

        existing_test_case = TestCase(
            id="EDGE-001",
            title="Existing Edge Case",
            module="ModuleA",
            priority="Medium",
            type="Error Handling",
            prerequisites=[],
            steps=["Existing step"],
            expected_results=["Existing result"],
        )
        test_suite = TestSuite(title="Suite", test_cases=[existing_test_case])

        result_suite = generator.forward("Some user story", test_suite)
        # Only EDGE-002 should be added since EDGE-001 is already present.
        assert len(result_suite.test_cases) == 2
        ids = {tc.id for tc in result_suite.test_cases}
        assert "EDGE-001" in ids
        assert "EDGE-002" in ids
