import json

import dspy
from pydantic import BaseModel, Field


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


class UserStoryToTestSuite(dspy.Signature):
    """Convert a user story into a test suite with detailed functional test cases covering all requirements, including UI interactions and backend behaviors where applicable. Output should be a JSON object representing the TestSuite."""

    user_story = dspy.InputField(desc="User story text")
    test_suite = dspy.OutputField(
        desc="Test suite with detailed test cases in JSON format"
    )


# Define a few-shot example
example_user_story = (
    "As a user, I want to create a new account so that I can log in later.\n"
    "## Account Creation\n"
    "- Users can create one account via the registration page.\n"
    "- UX/UI: 'Register' button is enabled only if all fields are filled."
)

example_test_case = TestCase(
    id="TC-001",
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

example_test_suite = TestSuite(
    title="Account Creation Test Suite", test_cases=[example_test_case]
)

# Convert to a JSON-serializable dictionary
example_dict = {
    "user_story": example_user_story,
    "test_suite": example_test_suite.json(),  # Assuming TestSuite has a .json() method
}


class TestCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(UserStoryToTestSuite)

    def forward(self, user_story):
        prompt = (
            f"Below is an example of converting a user story to a test suite:\n\n"
            f"User Story:\n{example_dict['user_story']}\n\n"
            f"Test Suite:\n{example_dict['test_suite']}\n\n"
            f"Now, convert the following user story to a test suite in the same format:\n\n"
            f"User Story:\n{user_story}\n\n"
            f"Test Suite:"
        )
        prediction = self.generate(user_story=prompt)
        try:
            test_suite_json = prediction.test_suite
            test_suite_dict = json.loads(test_suite_json)
            test_suite = TestSuite(**test_suite_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse test suite JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to create TestSuite: {e}")
        return test_suite


def format_test_suite_to_markdown(test_suite: TestSuite) -> str:
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
