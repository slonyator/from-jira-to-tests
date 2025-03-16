import json
import os
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
import dspy
from dspy.teleprompt import LabeledFewShot


# Shared Models
class TestCase(BaseModel):
    id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., description="Test case title")
    module: str = Field(..., description="Module being tested")
    priority: str = Field(..., description="Test priority")
    type: str = Field(..., description="Test type")
    prerequisites: list[str] = Field(default_factory=list)
    steps: list[str] = Field(..., description="Detailed test steps")
    expected_results: list[str] = Field(..., description="Expected outcomes")


class TestSuite(BaseModel):
    title: str = Field(..., description="Test suite title")
    test_cases: list[TestCase] = Field(default_factory=list)


# Shared Formatting Function
def format_test_suite_to_markdown(test_suite: TestSuite) -> str:
    """Format the test suite into a Markdown string."""
    if not test_suite.test_cases:
        return "## No Test Cases Generated\n"
    markdown = f"## {test_suite.title}\n\n"
    for tc in test_suite.test_cases:
        markdown += f"### Test Case {tc.id}: {tc.title}\n"
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


# Test Case Generator Components
class UserStoryToTestSuite(dspy.Signature):
    """Convert a user story into a test suite with detailed functional test cases covering all requirements."""

    user_story = dspy.InputField(desc="User story text")
    test_suite = dspy.OutputField(
        desc="Test suite with detailed test cases in JSON format"
    )


class TestCaseGenerator(dspy.Module):
    def __init__(self, trainset=None):
        super().__init__()
        self.generate = dspy.Predict(UserStoryToTestSuite)
        if trainset:
            teleprompter = LabeledFewShot()
            self.generate = teleprompter.compile(
                student=self.generate, trainset=trainset
            )

    def forward(self, user_story):
        prediction = self.generate(user_story=user_story)
        try:
            test_suite_json = prediction.test_suite
            test_suite_dict = json.loads(test_suite_json)
            return TestSuite(**test_suite_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse test suite JSON: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to create TestSuite: {e}") from e


# Edge Case Generator Components
class EdgeCasePrediction(BaseModel):
    needs_edge_cases: bool
    reason: str


class UserStoryToEdgeCasePrediction(dspy.Signature):
    """Determine if edge cases are necessary based on the user story."""

    user_story = dspy.InputField(desc="User story text")
    prediction = dspy.OutputField(
        desc="Prediction in JSON format with 'needs_edge_cases' (boolean) and 'reason' (string)"
    )


class UserStoryToEdgeCases(dspy.Signature):
    """Generate edge case test cases based on the user story, reason, and existing test suite."""

    user_story = dspy.InputField(desc="User story text")
    reason = dspy.InputField(desc="Reason for needing edge cases")
    existing_test_suite = dspy.InputField(
        desc="Existing test suite in JSON format"
    )
    edge_cases = dspy.OutputField(
        desc="JSON object with 'edge_cases' key containing a list of edge case test cases"
    )


class EdgeCasePredictor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(UserStoryToEdgeCasePrediction)

    def forward(self, user_story: str) -> EdgeCasePrediction:
        prediction = self.predict(user_story=user_story)
        try:
            prediction_dict = json.loads(prediction.prediction)
            return EdgeCasePrediction(**prediction_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse prediction JSON: {e}") from e


class EdgeCaseGeneratorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(UserStoryToEdgeCases)

    def forward(
        self, user_story: str, reason: str, existing_test_suite: str
    ) -> list:
        prediction = self.generate(
            user_story=user_story,
            reason=reason,
            existing_test_suite=existing_test_suite,
        )
        try:
            parsed_data = json.loads(prediction.edge_cases)
            if "edge_cases" not in parsed_data:
                raise ValueError("Missing 'edge_cases' key in prediction")
            edge_cases_list = parsed_data["edge_cases"]
            if not isinstance(edge_cases_list, list):
                raise ValueError("Edge cases must be a JSON list")
            return edge_cases_list
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse edge cases JSON: {e}") from e


class EdgeCaseGenerator:
    def __init__(self):
        self.predictor = EdgeCasePredictor()
        self.generator = EdgeCaseGeneratorModule()

    def needs_edge_cases(self, user_story: str) -> EdgeCasePrediction:
        return self.predictor.forward(user_story)

    def forward(self, user_story: str, test_suite: TestSuite) -> TestSuite:
        prediction = self.needs_edge_cases(user_story)
        if not prediction.needs_edge_cases:
            logger.info("No edge cases needed for this user story.")
            return test_suite

        existing_suite_json = test_suite.model_dump_json()
        edge_cases_list = self.generator.forward(
            user_story=user_story,
            reason=prediction.reason,
            existing_test_suite=existing_suite_json,
        )

        existing_ids = {tc.id for tc in test_suite.test_cases}
        new_edge_cases = [
            TestCase(**edge_case)
            for edge_case in edge_cases_list
            if edge_case["id"] not in existing_ids
        ]
        test_suite.test_cases.extend(new_edge_cases)
        logger.info(f"Generated and added {len(new_edge_cases)} edge cases")
        return test_suite


# Example Data for TestCaseGenerator
example_user_story_1 = (
    "As a user, I want to create a new account so that I can log in later.\n"
    "## Account Creation\n- Users can create one account via the registration page.\n- UX/UI: 'Register' button is enabled only if all fields are filled."
)
example_test_suite_1 = TestSuite(
    title="Account Creation Test Suite",
    test_cases=[
        TestCase(
            id="TC-001",
            title="User Account Creation",
            module="Account Management",
            priority="High",
            type="Functional",
            prerequisites=["User is not logged in"],
            steps=[
                "Navigate to the registration page",
                "Fill in the required fields (username, password, email)",
                "Verify that the 'Register' button is enabled",
                "Click the 'Register' button",
            ],
            expected_results=[
                "Account is created successfully",
                "User is redirected to the login page",
                "Confirmation email is sent (if applicable)",
            ],
        )
    ],
)
example_user_story_2 = "As a bank customer, I want to withdraw cash from an ATM using my debit card so that I can access my money without visiting a branch."
example_test_suite_2 = TestSuite(
    title="ATM Cash Withdrawal Test Suite",
    test_cases=[
        TestCase(
            id="TC001",
            title="ATM Cash Withdrawal",
            module="ATM Services",
            priority="High",
            type="Functional",
            prerequisites=[
                "User has a valid debit card",
                "User has sufficient funds in account",
                "ATM has sufficient cash",
            ],
            steps=[
                "Insert debit card into ATM",
                "Enter valid PIN",
                "Select 'Withdraw Cash' option",
                "Select account (checking/savings)",
                "Enter valid withdrawal amount",
                "Confirm transaction",
                "Take cash and card",
            ],
            expected_results=[
                "System authenticates user successfully",
                "System verifies sufficient funds",
                "System dispenses correct amount of cash",
                "System updates account balance",
                "System generates receipt",
                "Transaction appears in account history",
            ],
        )
    ],
)
trainset = [
    dspy.Example(
        user_story=example_user_story_1,
        test_suite=example_test_suite_1.model_dump_json(),
    ),
    dspy.Example(
        user_story=example_user_story_2,
        test_suite=example_test_suite_2.model_dump_json(),
    ),
]


# Main Function
def main():
    load_dotenv()
    generator_model = "openai/gpt-4o-mini"
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        raise ValueError("Please set OPENAI_API_KEY in your environment.")

    lm_generator = dspy.LM(
        model=generator_model,
        max_tokens=1000,
        temperature=0.0,
        api_key=api_key,
    )
    dspy.settings.configure(lm=lm_generator)

    # Example user story for testing
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

    # Generate initial test suite
    test_generator = TestCaseGenerator(trainset=trainset)
    initial_suite = test_generator.forward(user_story)

    # Extend with edge cases
    edge_generator = EdgeCaseGenerator()
    extended_suite = edge_generator.forward(
        user_story=user_story, test_suite=initial_suite
    )

    # Output results
    formatted_output = format_test_suite_to_markdown(extended_suite)
    print(formatted_output)

    output_path = "extended_test_cases.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_output)
    logger.info(f"Extended test cases written to {output_path}")


if __name__ == "__main__":
    main()
