import os
import json
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
import dspy


# Pydantic Models
class TestCase(BaseModel):
    id: str = Field(..., description="Unique test case identifier")
    module: str = Field(..., description="Module being tested")
    priority: str = Field(..., description="Test priority")
    type: str = Field(..., description="Test type")
    prerequisites: list[str] = Field(default_factory=list)
    steps: list[str] = Field(..., description="Detailed test steps")
    expected_results: list[str] = Field(..., description="Expected outcomes")


class TestSuite(BaseModel):
    title: str = Field(..., description="Test suite title")
    test_cases: list[TestCase] = Field(default_factory=list)


class EdgeCasePrediction(BaseModel):
    needs_edge_cases: bool
    reason: str


# DSPy Signatures
class UserStoryToEdgeCasePrediction(dspy.Signature):
    """Determine if edge cases are necessary based on the user story. Consider scenarios like network issues, concurrent requests, or other potential edge cases that might not be explicitly mentioned but could impact reliability or performance."""

    user_story = dspy.InputField(desc="User story text")
    prediction = dspy.OutputField(
        desc="Prediction in JSON format with 'needs_edge_cases' (boolean) and 'reason' (string)"
    )


class UserStoryToEdgeCases(dspy.Signature):
    """Generate edge case test cases based on the user story, the reason for needing edge cases, and the existing test suite. Ensure no duplicate test cases."""

    user_story = dspy.InputField(desc="User story text")
    reason = dspy.InputField(desc="Reason for needing edge cases")
    existing_test_suite = dspy.InputField(
        desc="Existing test suite in JSON format"
    )
    edge_cases = dspy.OutputField(
        desc="List of edge case test cases in JSON format"
    )


# DSPy Modules
class EdgeCasePredictor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(UserStoryToEdgeCasePrediction)

    def forward(self, user_story: str) -> EdgeCasePrediction:
        """Generate an edge case prediction for the given user story."""
        prediction = self.predict(user_story=user_story)
        try:
            prediction_dict = json.loads(prediction.prediction)
            return EdgeCasePrediction(**prediction_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse prediction JSON: {e}")


class EdgeCaseGeneratorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(UserStoryToEdgeCases)

    def forward(
        self, user_story: str, reason: str, existing_test_suite: str
    ) -> list:
        """Generate edge cases based on the inputs."""
        prediction = self.generate(
            user_story=user_story,
            reason=reason,
            existing_test_suite=existing_test_suite,
        )
        logger.debug(f"Raw edge cases prediction: {prediction.edge_cases}")
        try:
            # Parse the JSON string into a Python object
            parsed_data = json.loads(prediction.edge_cases)

            # Check if the "edge_cases" key exists
            if "edge_cases" not in parsed_data:
                raise ValueError("Missing 'edge_cases' key in prediction")

            # Extract the list from the "edge_cases" key
            edge_cases_list = parsed_data["edge_cases"]

            # Validate that it's a list
            if not isinstance(edge_cases_list, list):
                raise ValueError("Edge cases must be a JSON list")

            # Optional: Validate that each item is a dictionary
            for edge_case in edge_cases_list:
                if not isinstance(edge_case, dict):
                    raise ValueError(
                        "Each edge case must be a JSON object (dictionary)"
                    )

            # Return the list of edge cases
            return edge_cases_list
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse edge cases JSON: {e}")


# EdgeCaseGenerator Class
class EdgeCaseGenerator:
    def __init__(self):
        """Initialize with predictor and generator modules."""
        self.predictor = EdgeCasePredictor()
        self.generator = EdgeCaseGeneratorModule()

    def needs_edge_cases(self, user_story: str) -> EdgeCasePrediction:
        """Determine if edge cases are needed."""
        prediction = self.predictor.forward(user_story)
        logger.info(
            f"Edge case prediction: {prediction.needs_edge_cases}, Reason: {prediction.reason}"
        )
        return prediction

    def forward(self, user_story: str, test_suite: TestSuite) -> TestSuite:
        """Extend the TestSuite with edge cases if necessary."""
        prediction = self.needs_edge_cases(user_story)
        if not prediction.needs_edge_cases:
            logger.info("No edge cases needed for this user story.")
            return test_suite

        # Convert existing test suite to JSON for the generator
        existing_suite_json = test_suite.model_dump_json()

        # Generate edge cases based on user story, reason, and existing suite
        logger.info("Generating edge cases...")
        edge_cases_list = self.generator.forward(
            user_story=user_story,
            reason=prediction.reason,
            existing_test_suite=existing_suite_json,
        )

        # Add generated edge cases to the test suite, avoiding duplicates
        existing_ids = {tc.id for tc in test_suite.test_cases}
        new_edge_cases = []
        for edge_case_dict in edge_cases_list:
            edge_case = TestCase(**edge_case_dict)
            if edge_case.id not in existing_ids:
                new_edge_cases.append(edge_case)
                existing_ids.add(edge_case.id)

        test_suite.test_cases.extend(new_edge_cases)
        logger.info(f"Generated and added {len(new_edge_cases)} edge cases")
        return test_suite


# Utility Function
def format_test_suite_to_markdown(test_suite: TestSuite) -> str:
    """Format the test suite into a Markdown string."""
    if not test_suite.test_cases:
        return "## No Test Cases Generated\n"
    markdown = f"## {test_suite.title}\n\n"
    for tc in test_suite.test_cases:
        markdown += f"### Test Case {tc.id}\n"
        markdown += f"**Module:** {tc.module}\n"
        markdown += f"**Priority:** {tc.priority}\n"
        markdown += f"**Type:** {tc.type}\n"
        if tc.prerequisites:
            markdown += "#### Prerequisites\n"
            for prereq in tc.prerequisites:
                markdown += f"- {prereq}\n"
        markdown += "#### Test Steps\n"
        for i, step in enumerate(tc.steps, 1):
            markdown += f"{i}. {step}\n"
        markdown += "#### Expected Results\n"
        for result in tc.expected_results:
            markdown += f"- {result}\n"
        markdown += "\n"
    return markdown


# Main Function
def main():
    """Main execution function to generate and output the extended test suite."""
    # Load environment variables
    load_dotenv()
    generator_model = "openai/gpt-4o-mini"
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        raise ValueError("Please set OPENAI_API_KEY in your environment.")

    # Configure DSPy with the language model
    lm_generator = dspy.LM(
        model=generator_model,
        max_tokens=1000,
        temperature=0.0,
        api_key=api_key,
    )
    dspy.settings.configure(lm=lm_generator)

    # Define user story
    user_story = (
        "# **Extension Tokens**\n\n"
        "## New Extension Tokens have user-based access\n"
        "- New extension tokens (aka non-legacy tokens) are **user-based** and will have access only to the groups of their creator at the time of using the token.\n"
        "    - The group Everyone is always included.\n"
        "    - The group Unassigned Users is included if the user is not assigned to any custom group.\n"
        "- When using the token the BE should limit the token's responses only to applications accessible by the creator at that time.\n"
        "    If the creator is deactivated from the account, the non-legacy extension will be automatically deactivated.\n"
        "    If the creator is deleted from the account, the non-legacy extension will be automatically deleted.\n"
        "    Legacy tokens will not be updated. They should continue working without any changes and will have access to all apps (Global Access).\n\n"
        "## Token Access\n"
        "UX/UI Requirements.\n"
        "- New extension tokens (aka non-legacy tokens) are **user-based** and will have access only to the groups of their creator at the time of using the token.\n"
        "    - The group Everyone is always included.\n"
        "    - The group Unassigned Users is included if the user is not assigned to any custom group.\n"
        "- When using the token the BE should limit the token's responses only to applications accessible by the creator at that time.\n"
        "- If the creator is deactivated from the account, the non-legacy extension will be automatically deactivated.\n"
        "- If the creator is deleted from the account, the non-legacy extension will be automatically deleted.\n"
        "- Legacy tokens will not be updated. They should continue working without any changes and will have access to all apps (Global Access).\n"
        "**No UI is required for this use case.**\n\n"
        "## Token Management\n"
        "**Users can have only one non-legacy extension token**\n"
        "UX/UI Requirements.\n"
        "- All users (regular, limited, admin, devops) can have **only one** non-legacy token.\n"
        "    - They can view / copy / download / refresh / delete this token.\n"
        "        The **Create New Token** button is disabled, in case a new token already appears on the list.\n"
        "        - In this case, the proper tooltip appears on hover.\n"
        "    - The token's access will appear in the Access Level column: Creator Access and the following tooltip on hover: Token inherits access permissions from the creator.\n"
        "**Legacy extension tokens are only visitable to Admin/DevOps**\n"
        "- Regular users or Limited users **cannot view** any legacy tokens, including:\n"
        "    - Legacy tokens they have created. These tokens will not be displayed on the list (even though they are still active).\n"
        "    - Legacy tokens with no creators will not appear on the list (even though they are still active).\n"
        "- Admin / DevOps users **can view** and **delete all legacy tokens**, including:\n"
        "    - Legacy tokens they have created.\n"
        "    - Legacy tokens other users have created.\n"
        "    - Legacy tokens with no creators.\n"
        "- No user can copy/download/refresh legacy tokens. These actions will appear disabled for legacy extension tokens.\n"
        "- Legacy tokens will have Global Access (access to all apps, as of today). This will be indicated in the Access Level column. With the tooltip: Token has access to all apps."
    )

    # Define initial test suite
    initial_suite = TestSuite(
        title="Extension Tokens Test Suite",
        test_cases=[
            TestCase(
                id="EXT-001",
                module="Extension Token Management",
                priority="High",
                type="Functional",
                prerequisites=[
                    "User is logged into the system",
                    "User has appropriate permissions",
                ],
                steps=[
                    "Navigate to Extension Token management page",
                    "Verify 'Create New Token' button state",
                    "Click 'Create New Token' button",
                    "Verify token creation",
                ],
                expected_results=[
                    "New token created successfully",
                    "Token inherits creator's access permissions",
                    "Access Level column shows 'Creator Access' with correct tooltip",
                    "Only one non-legacy token allowed per user",
                ],
            ),
            TestCase(
                id="EXT-002",
                module="Extension Token Management",
                priority="High",
                type="Functional",
                prerequisites=[
                    "System has existing legacy tokens",
                    "Users of different permission levels exist",
                ],
                steps=[
                    "Log in as regular/limited user",
                    "Log in as Admin/DevOps user",
                    "Verify legacy token management options",
                ],
                expected_results=[
                    "Regular users cannot see legacy tokens",
                    "Admin/DevOps can see and manage all legacy tokens",
                    "Legacy tokens show 'Global Access' in Access Level column",
                ],
            ),
            TestCase(
                id="EXT-003",
                module="Extension Token Management",
                priority="High",
                type="Functional",
                steps=[
                    "Deactivate a token creator's account",
                    "Delete a token creator's account",
                    "Verify legacy tokens remain unchanged",
                ],
                expected_results=[
                    "Appropriate token deactivation/deletion based on creator account status",
                    "Legacy tokens maintain functionality",
                    "System logs reflect changes",
                ],
            ),
        ],
    )

    # Generate edge cases and extend the test suite
    logger.info("Starting edge case generation")
    edge_generator = EdgeCaseGenerator()
    extended_suite = edge_generator.forward(
        user_story=user_story, test_suite=initial_suite
    )

    # Format and output the extended test suite
    formatted_output = format_test_suite_to_markdown(extended_suite)
    logger.info("Edge case generation completed")
    print(formatted_output)

    # Write to file
    output_path = "extended_test_cases.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_output)
    logger.info(f"Extended test cases written to {output_path}")


if __name__ == "__main__":
    main()
