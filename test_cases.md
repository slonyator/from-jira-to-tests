# Test Suite: Token Access & Management
*Generated on: 2025-03-16*

## Requirements Analysis

### Gap 1
- **Description:** Lack of clarity on how the system handles token expiration or renewal.
- **Suggested Clarification:** Specify if there is a mechanism for token expiration and how users can renew or replace their tokens.
- **Confidence Level:** Medium
- **Related Test Cases:** TC008, TC009, TC010, TC011

### Gap 2
- **Description:** Unclear handling of scenarios where a user is part of multiple groups.
- **Suggested Clarification:** Clarify how access is determined if a user belongs to multiple groups at the time of token creation.
- **Confidence Level:** Medium
- **Related Test Cases:** TC012, TC013, TC014, TC015, TC016

### Gap 3
- **Description:** No mention of error handling or user feedback for token-related actions.
- **Suggested Clarification:** Include requirements for user feedback or error messages when actions like creating, deleting, or refreshing tokens fail.
- **Confidence Level:** High
- **Related Test Cases:** None

### Gap 4
- **Description:** Ambiguity regarding the visibility of tokens in the UI for different user roles.
- **Suggested Clarification:** Detail how the UI will indicate the status of tokens (active, deactivated, deleted) for different user roles.
- **Confidence Level:** Medium
- **Related Test Cases:** TC017, TC018, TC019, TC020, TC021

### Gap 5
- **Description:** No information on the security measures for token management.
- **Suggested Clarification:** Outline any security protocols in place for token creation, storage, and access to prevent unauthorized use.
- **Confidence Level:** High
- **Related Test Cases:** TC022, TC023, TC024, TC025, TC026, TC027

## Final Test Suite

### Test Case TC001: Create Non-Legacy Token
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is logged in
- User has no existing non-legacy token
#### Test Steps
1. Navigate to the token management page
2. Click on 'Create New Token' button
#### Expected Results
- Non-legacy token is created successfully
- Token is displayed in the token list
- 'Create New Token' button is disabled

### Test Case TC002: View Non-Legacy Token Access
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
#### Test Steps
1. Navigate to the token management page
2. Locate the non-legacy token in the list
3. Hover over the Access Level column
#### Expected Results
- Access Level shows 'Creator Access'
- Tooltip displays 'Token inherits access permissions from the creator'

### Test Case TC003: Token Access Limitations for Deactivated User
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is deactivated
#### Test Steps
1. Attempt to use the non-legacy token
#### Expected Results
- Token is automatically deactivated
- User cannot access applications with the token

### Test Case TC004: Token Access Limitations for Deleted User
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is deleted from the account
#### Test Steps
1. Attempt to use the non-legacy token
#### Expected Results
- Token is automatically deleted
- User cannot access applications with the token

### Test Case TC005: View Legacy Tokens as Admin
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is logged in as Admin/DevOps
#### Test Steps
1. Navigate to the token management page
#### Expected Results
- All legacy tokens are displayed in the list
- Admin/DevOps can view and delete legacy tokens

### Test Case TC006: Legacy Token Access for Regular Users
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is logged in as Regular/Limited user
#### Test Steps
1. Navigate to the token management page
#### Expected Results
- No legacy tokens are displayed in the list
- User cannot view any legacy tokens

### Test Case TC007: Disable Actions for Legacy Tokens
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is logged in as Admin/DevOps
- Legacy tokens are present
#### Test Steps
1. Locate a legacy token in the list
2. Attempt to copy/download/refresh the legacy token
#### Expected Results
- Copy/download/refresh actions are disabled for legacy tokens

### Test Case TC008: Verify token expiration mechanism
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy extension token.
#### Test Steps
1. Wait for the token to reach its expiration time.
2. Attempt to use the expired token to access applications.
#### Expected Results
- The system should deny access and return an expiration error message.

### Test Case TC009: Verify token renewal process
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has an expired non-legacy extension token.
#### Test Steps
1. Navigate to the token management section.
2. Select the option to renew the expired token.
#### Expected Results
- The system should allow the user to renew the token and provide a new token.

### Test Case TC010: Verify token replacement process
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has an active non-legacy extension token.
#### Test Steps
1. Navigate to the token management section.
2. Select the option to replace the current token.
#### Expected Results
- The system should allow the user to replace the token and provide a new token.

### Test Case TC011: Verify tooltip for token expiration
**Module:** Token Management
**Priority:** Low
**Type:** UI
#### Prerequisites
- User has a non-legacy extension token.
#### Test Steps
1. Hover over the token expiration date in the token management section.
#### Expected Results
- A tooltip should appear indicating the expiration policy for the token.

### Test Case TC012: Verify access for user with multiple groups at token creation
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is a member of multiple groups
- User has created a non-legacy extension token
#### Test Steps
1. Log in as the user who has multiple group memberships.
2. Create a non-legacy extension token.
3. Check the access level of the created token.
#### Expected Results
- The token should have access to all groups the user belongs to at the time of creation, including the group Everyone.
- The token should not have access to any groups the user is not a member of.

### Test Case TC013: Verify token access after user group membership change
**Module:** Token Access
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has created a non-legacy extension token
- User is a member of multiple groups
#### Test Steps
1. Log in as the user.
2. Remove the user from one of the groups they belong to.
3. Attempt to use the non-legacy extension token.
#### Expected Results
- The token should only provide access to applications in the remaining groups the user belongs to.
- Access to applications in the removed group should be denied.

### Test Case TC014: Verify token deactivation upon user deactivation
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy extension token
- User is active
#### Test Steps
1. Log in as the user.
2. Deactivate the user account.
3. Attempt to use the non-legacy extension token.
#### Expected Results
- The non-legacy extension token should be automatically deactivated.
- Any attempts to use the token should result in an access denied error.

### Test Case TC015: Verify token deletion upon user deletion
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy extension token
- User is active
#### Test Steps
1. Log in as the user.
2. Delete the user account.
3. Check if the non-legacy extension token still exists.
#### Expected Results
- The non-legacy extension token should be automatically deleted.
- The token should not be retrievable or accessible.

### Test Case TC016: Verify legacy token visibility for Admin/DevOps
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- Admin/DevOps user account exists
- Legacy tokens exist in the system
#### Test Steps
1. Log in as an Admin/DevOps user.
2. Navigate to the legacy tokens section.
3. Check the visibility of legacy tokens.
#### Expected Results
- Admin/DevOps user should be able to view all legacy tokens, including those created by other users.
- Legacy tokens should be listed with appropriate access levels.

### Test Case TC017: Display Active Status for Non-Legacy Token
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
- User is active
#### Test Steps
1. Log in as a regular user with an active non-legacy token.
2. Navigate to the token management section.
3. Observe the status indicator for the non-legacy token.
#### Expected Results
- The status indicator shows 'Active' for the non-legacy token.

### Test Case TC018: Display Deactivated Status for Non-Legacy Token
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
- User is deactivated
#### Test Steps
1. Log in as a regular user whose account has been deactivated.
2. Navigate to the token management section.
3. Observe the status indicator for the non-legacy token.
#### Expected Results
- The status indicator shows 'Deactivated' for the non-legacy token.

### Test Case TC019: Display Deleted Status for Non-Legacy Token
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
- User account has been deleted
#### Test Steps
1. Log in as a regular user whose account has been deleted.
2. Navigate to the token management section.
3. Observe the status indicator for the non-legacy token.
#### Expected Results
- The status indicator shows 'Deleted' for the non-legacy token.

### Test Case TC020: Display Active Status for Legacy Token for Admin/DevOps
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- Admin/DevOps user exists
- Legacy tokens exist
#### Test Steps
1. Log in as an Admin/DevOps user.
2. Navigate to the token management section.
3. Observe the status indicator for legacy tokens.
#### Expected Results
- The status indicator shows 'Active' for all legacy tokens.

### Test Case TC021: Ensure Regular/Limited Users Cannot View Legacy Tokens
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- Regular or Limited user exists
- Legacy tokens exist
#### Test Steps
1. Log in as a Regular or Limited user.
2. Navigate to the token management section.
3. Check for the presence of legacy tokens.
#### Expected Results
- No legacy tokens are displayed in the token management section.

### Test Case TC022: Verify user-based access for new extension tokens
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is logged in
- User has permission to create a non-legacy token
#### Test Steps
1. Create a new non-legacy extension token.
2. Assign the token to a user with specific group access.
3. Attempt to use the token to access applications.
#### Expected Results
- Token should only allow access to applications within the user's assigned groups.
- The group 'Everyone' should always be included in the access.

### Test Case TC023: Verify automatic deactivation of token upon user deactivation
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has an active non-legacy extension token
- User is logged in
#### Test Steps
1. Deactivate the user account.
2. Attempt to use the non-legacy extension token.
#### Expected Results
- The token should be automatically deactivated and not allow access to any applications.

### Test Case TC024: Verify automatic deletion of token upon user deletion
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has an active non-legacy extension token
- User is logged in
#### Test Steps
1. Delete the user account.
2. Check if the non-legacy extension token is still available.
#### Expected Results
- The non-legacy extension token should be automatically deleted and not found in the token list.

### Test Case TC025: Verify legacy token visibility for Admin/DevOps
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- Admin/DevOps user is logged in
- Legacy tokens exist in the system
#### Test Steps
1. Navigate to the token management section.
2. Check the list of tokens available.
#### Expected Results
- Admin/DevOps user should be able to view all legacy tokens, including those created by other users.

### Test Case TC026: Verify restricted actions on legacy tokens for regular users
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- Regular user is logged in
- User has created a legacy token
#### Test Steps
1. Navigate to the token management section.
2. Attempt to copy/download/refresh the legacy token.
#### Expected Results
- All actions (copy/download/refresh) should be disabled for the legacy token.

### Test Case TC027: Verify tooltip information for token access levels
**Module:** Token Management
**Priority:** Low
**Type:** Functional
#### Prerequisites
- User is logged in
- User has created a non-legacy token
#### Test Steps
1. Hover over the access level column for the non-legacy token.
#### Expected Results
- Tooltip should display: 'Token inherits access permissions from the creator.'

### Test Case TC028: Reactivation of Deactivated User
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is deactivated
#### Test Steps
1. Reactivate the user account
2. Attempt to use the non-legacy token
#### Expected Results
- The token should be automatically reactivated
- User can access applications with the token

### Test Case TC029: Token Access for User with Multiple Groups
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is a member of multiple groups
- User has created a non-legacy extension token
#### Test Steps
1. Log in as the user
2. Create a non-legacy extension token
3. Remove the user from one of the groups
4. Attempt to use the non-legacy extension token
#### Expected Results
- The token should provide access only to applications in the remaining groups
- Access to applications in the removed group should be denied

### Test Case TC030: Legacy Token Access for Deleted User
**Module:** Token Access
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has created a legacy token
- User account has been deleted
#### Test Steps
1. Check if the legacy token is still accessible
#### Expected Results
- The legacy token should still be active and accessible by Admin/DevOps
- Regular/Limited users should not see the token

### Test Case TC031: Token Access After Group Reassignment
**Module:** Token Access
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has created a non-legacy extension token
- User is a member of multiple groups
#### Test Steps
1. Remove the user from all groups
2. Attempt to use the non-legacy extension token
#### Expected Results
- The token should deny access to all applications since the user has no group memberships

### Test Case TC032: Token Creation with No Group Membership
**Module:** Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is not assigned to any custom group
#### Test Steps
1. Create a non-legacy extension token
2. Check the access level of the created token
#### Expected Results
- The token should have access to the group 'Everyone' and 'Unassigned Users' only

