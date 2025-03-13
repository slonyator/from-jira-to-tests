import dspy
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str = Field(..., description="Unique test case identifier")
    module: str = Field(..., description="Module being tested")
    priority: str = Field(..., description="Test priority")
    type: str = Field(..., description="Test type")
    prerequisites: list[str] = Field(default_factory=list)
    steps: list[str] = Field(..., description="Test steps")
    expected_results: list[str] = Field(..., description="Expected outcomes")


class TestSuite(BaseModel):
    title: str = Field(..., description="Test suite title")
    test_cases: list[TestCase] = Field(default_factory=list)


class UserStoryToTestCase(dspy.Signature):
    """Convert a user story into detailed functional test cases"""

    user_story = dspy.InputField(desc="User story text")
    test_cases = dspy.OutputField(
        desc="List of detailed test cases in markdown format"
    )
