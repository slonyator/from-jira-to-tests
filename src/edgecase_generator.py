import os
import json
import dspy
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field


# Pydantic Models (unchanged)
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


# New Signature for Missing Edge Cases
class UserStoryToMissingEdgeCases(dspy.Signature):
    """Analyze a user story and an existing test suite to identify and generate missing edge case test cases in JSON format.
    The output must be a JSON list of test case objects that cover edge scenarios (e.g., network failures, concurrency issues, boundary conditions) not already addressed in the existing test suite. Each test case object must include:
    - 'id': a unique string identifier (e.g., 'EDGE-001'),
    - 'module': a string (e.g., 'Token Management'),
    - 'priority': a string (e.g., 'High', 'Medium', 'Low'),
    - 'type': a string (e.g., 'Error Handling', 'Concurrency'),
    - 'prerequisites': a list of strings (optional, default empty),
    - 'steps': a list of strings detailing the test steps,
    - 'expected_results': a list of strings detailing the expected outcomes.
    Review the user story for triggers like 'deactivated', 'deleted', 'only one', 'limit', 'network', 'error', or 'concurrent', and ensure the output only includes edge cases not already covered by the existing test suite’s test cases (provided as JSON)."""

    user_story = dspy.InputField(desc="User story text")
    existing_test_suite = dspy.InputField(
        desc="Existing test suite in JSON format"
    )
    missing_edge_case_test_cases = dspy.OutputField(
        desc="List of missing edge case test cases in JSON format"
    )


# Updated EdgeCaseGenerator
class EdgeCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_edge = dspy.Predict(UserStoryToMissingEdgeCases)

    def needs_edge_cases(self, user_story: str) -> bool:
        """Determine if edge cases might be relevant based on user story content."""
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

    def forward(self, user_story: str, test_suite: TestSuite) -> TestSuite:
        """Extend the provided TestSuite with missing edge case test cases."""
        if not self.needs_edge_cases(user_story):
            logger.info("No edge cases needed for this user story.")
            return test_suite

        # Convert existing test suite to JSON for analysis by the LM
        existing_suite_json = test_suite.model_dump_json()
        prediction = self.generate_edge(
            user_story=user_story, existing_test_suite=existing_suite_json
        )
        edge_cases_json = prediction.missing_edge_case_test_cases
        logger.debug(
            f"Raw JSON output from model for missing edge cases: {edge_cases_json}"
        )

        try:
            edge_cases_list = json.loads(edge_cases_json)
            if not isinstance(edge_cases_list, list):
                raise ValueError(
                    "Edge case output must be a JSON list of test cases"
                )

            # Append only new edge cases to the suite
            existing_ids = {
                tc.id for tc in test_suite.test_cases
            }  # Track existing IDs to avoid duplicates
            for edge_case_dict in edge_cases_list:
                if edge_case_dict.get("id") not in existing_ids:
                    edge_case = TestCase(**edge_case_dict)
                    test_suite.test_cases.append(edge_case)
                    existing_ids.add(edge_case.id)
            return test_suite

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse edge case test cases JSON: {e}")
            raise ValueError(f"Failed to parse edge case test cases JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to extend TestSuite with edge cases: {e}")
            raise ValueError(
                f"Failed to extend TestSuite with edge cases: {e}"
            )


def format_test_suite_to_markdown(test_suite: TestSuite) -> str:
    if not test_suite or not test_suite.test_cases:
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


def main():
    # Load environment variables
    load_dotenv()

    # Configure the language model
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

    # User story from your example
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

    # Initial TestSuite from your example
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

    # Extend with missing edge cases
    logger.info("Starting edge case generation")
    edge_generator = EdgeCaseGenerator()
    extended_suite = edge_generator.forward(
        user_story=user_story, test_suite=initial_suite
    )

    # Format and print output
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
