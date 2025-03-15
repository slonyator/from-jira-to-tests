import json
import os

import dspy
from dotenv import load_dotenv
from loguru import logger
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


class UserStoryToEdgeCaseTestSuite(dspy.Signature):
    """Convert a user story into an edge case test suite in JSON format, focusing on error handling, concurrency, and integration scenarios.
    The output must be a JSON object with a 'title' field (string) and a 'test_cases' field (list of objects). Each test case object must include:
    - 'id': a unique string identifier (e.g., 'EDGE-001'),
    - 'module': a string indicating the module being tested (e.g., 'Token Management'),
    - 'priority': a string (e.g., 'High', 'Medium', 'Low'),
    - 'type': a string indicating the test type (e.g., 'Error Handling', 'Concurrency'),
    - 'prerequisites': a list of strings (optional, default empty),
    - 'steps': a list of strings detailing the test steps,
    - 'expected_results': a list of strings detailing the expected outcomes.
    Ensure the JSON strictly adheres to this structure."""

    user_story = dspy.InputField(desc="User story text")
    edge_case_test_suite = dspy.OutputField(
        desc="Edge case test suite in JSON format adhering to the specified structure"
    )


class EdgeCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_edge_case = dspy.Predict(UserStoryToEdgeCaseTestSuite)

    def needs_edge_cases(self, user_story: str) -> bool:
        """Determine if edge cases are needed based on user story content."""
        edge_keywords = [
            "deactivated",
            "deleted",
            "limit",
            "concurrent",
            "network",
            "error",
            "only one",
        ]
        return any(keyword in user_story.lower() for keyword in edge_keywords)

    def forward(self, user_story):
        if not self.needs_edge_cases(user_story):
            logger.info("No edge cases needed for this user story.")
            return None
        prediction = self.generate_edge_case(user_story=user_story)
        edge_suite_json = prediction.edge_case_test_suite
        logger.debug(f"Raw JSON output from model: {edge_suite_json}")
        try:
            edge_suite_dict = json.loads(edge_suite_json)
            edge_suite = TestSuite(**edge_suite_dict)
            return edge_suite
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse edge case test suite JSON: {e}")
            raise ValueError(f"Failed to parse edge case test suite JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to create EdgeCase TestSuite: {e}")
            raise ValueError(f"Failed to create EdgeCase TestSuite: {e}")


def format_test_suite_to_markdown(test_suite: TestSuite) -> str:
    if not test_suite:
        return "## No Edge Case Test Suite Generated\n"
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


if __name__ == "__main__":
    _ = load_dotenv()

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

    logger.info("Starting edge case generation")
    edge_generator = EdgeCaseGenerator()
    edge_suite = edge_generator.forward(user_story)

    formatted_output = format_test_suite_to_markdown(edge_suite)
    logger.info("Edge case generation completed")
    print(formatted_output)

    output_path = "edge_cases.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_output)
    logger.info(f"Edge cases written to {output_path}")
