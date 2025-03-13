import dspy
from dspy import BootstrapFewShot

from loguru import logger
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str = Field(..., description="Unique test case identifier")
    module: str = Field(..., description="Module being tested")
    priority: str = Field(..., description="Test priority")
    type: str = Field(..., description="Test type")
    prerequisites: list[str] = Field(
        default_factory=list, description="Conditions required before testing"
    )
    steps: list[str] = Field(..., description="Test steps")
    expected_results: list[str] = Field(..., description="Expected outcomes")


class TestSuite(BaseModel):
    title: str = Field(..., description="Test suite title")
    test_cases: list[TestCase] = Field(
        default_factory=list, description="List of test cases"
    )


class UserStoryToTestCase(dspy.Signature):
    """Convert a user story into detailed functional test cases in Markdown format"""

    user_story = dspy.InputField(desc="User story text")
    test_cases = dspy.OutputField(desc="Markdown-formatted test cases")


examples = [
    dspy.Example(
        user_story="As a user, I want to create a new extension token so that it has access only to my groups.",
        test_cases="""### Test Case EXT-001: New Extension Token Creation
**Module:** Extension Token Management
**Priority:** High
**Type:** Functional

#### Prerequisites
- User is logged into the system
- User has appropriate permissions

#### Test Steps
1. Navigate to Extension Token management page
2. Verify "Create New Token" button state
   - Expected: Button enabled if user has no existing non-legacy token
   - Expected: Button disabled with tooltip if user already has a token
3. Click "Create New Token" button
4. Verify token creation
   - Expected: Token is created with creator's current group access
   - Expected: "Everyone" group is automatically included
   - Expected: "Unassigned Users" group included if user not in custom group

#### Expected Results
- New token created successfully
- Token inherits creator's access permissions
- Access Level column shows "Creator Access" with correct tooltip
- Only one non-legacy token allowed per user""",
    ).with_inputs("user_story"),
    dspy.Example(
        user_story="As an admin, I want to view legacy extension tokens while regular users cannot, so that only authorized personnel can manage them.",
        test_cases="""### Test Case EXT-002: Legacy Token Visibility
**Module:** Extension Token Management
**Priority:** High
**Type:** Functional

#### Prerequisites
- System has existing legacy tokens
- Users of different permission levels exist

#### Test Steps
1. Log in as regular/limited user
   - Expected: Cannot view any legacy tokens
2. Log in as Admin/DevOps user
   - Expected: Can view all legacy tokens
3. Verify legacy token management options
   - Expected: Copy/download/refresh actions disabled
   - Expected: Delete action enabled for Admin/DevOps

#### Expected Results
- Regular users cannot see legacy tokens
- Admin/DevOps can see and manage all legacy tokens
- Legacy tokens show "Global Access" in Access Level column""",
    ).with_inputs("user_story"),
    dspy.Example(
        user_story="As a system admin, I want non-legacy extension tokens to be automatically managed when a creator's account status changes, so that access remains secure.",
        test_cases="""### Test Case EXT-003: Token Deactivation Scenarios
**Module:** Extension Token Management
**Priority:** High
**Type:** Functional

#### Test Steps
1. Deactivate a token creator's account
   - Expected: Non-legacy extension automatically deactivated
2. Delete a token creator's account
   - Expected: Non-legacy extension automatically deleted
3. Verify legacy tokens remain unchanged
   - Expected: No impact on legacy token functionality

#### Expected Results
- Appropriate token deactivation/deletion based on creator account status
- Legacy tokens maintain functionality
- System logs reflect changes""",
    ).with_inputs("user_story"),
    dspy.Example(
        user_story="As an admin, I want to create a new API token with group-based access so that it can only access specific applications.",
        test_cases="""### Test Case API-001: New API Token Group Access
**Module:** API Token Management
**Priority:** High
**Type:** Functional

#### Prerequisites
- Admin/DevOps user access
- Existing groups in system

#### Test Steps
1. Create new API token
2. Verify group access rules:
   - All apps in defined groups at creation time
   - New apps added to defined groups
   - Apps in Everyone group
3. Test group inheritance
   - Expected: Token maintains access to original group apps even if removed
   - Expected: Gains access to new apps added to groups

#### Expected Results
- Token created with correct group access
- Access properly inherited and maintained
- Group changes reflected appropriately""",
    ).with_inputs("user_story"),
]


class TestCaseGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.signature = UserStoryToTestCase
        base_predictor = dspy.Predict(self.signature)
        optimizer = BootstrapFewShot(metric=lambda example, pred: True)
        self.generate = optimizer.compile(base_predictor, trainset=examples)

    def forward(self, user_story):
        logger.info("Generating test cases for user story")
        prediction = self.generate(user_story=user_story)
        return prediction.test_cases
