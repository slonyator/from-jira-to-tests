## Extension Tokens Test Suite

### Test Case TC-001
**Module:** Token Creation
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is logged in
- User has no existing non-legacy token
#### Test Steps
1. Navigate to the token management page
2. Click on 'Create New Token' button
#### Expected Results
- New non-legacy token is created successfully
- Token is displayed in the token list
- 'Create New Token' button is disabled

### Test Case TC-002
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
#### Test Steps
1. Use the created token to access applications
#### Expected Results
- Token only accesses applications available to the creator
- Group 'Everyone' is included in access
- Group 'Unassigned Users' is included if applicable

### Test Case TC-003
**Module:** Token Deactivation
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is deactivated
#### Test Steps
1. Deactivate the user account
#### Expected Results
- Non-legacy token is automatically deactivated

### Test Case TC-004
**Module:** Token Deletion
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is deleted from the account
#### Test Steps
1. Delete the user account
#### Expected Results
- Non-legacy token is automatically deleted

### Test Case TC-005
**Module:** Legacy Token Visibility
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is a regular or limited user
- User has created legacy tokens
#### Test Steps
1. Navigate to the token management page
#### Expected Results
- Legacy tokens are not displayed in the list

### Test Case TC-006
**Module:** Admin Token Management
**Priority:** High
**Type:** Functional
#### Prerequisites
- User is an Admin or DevOps
#### Test Steps
1. Navigate to the token management page
#### Expected Results
- Admin can view all legacy tokens
- Admin can delete legacy tokens
- Admin cannot copy/download/refresh legacy tokens

### Test Case TC-007
**Module:** Legacy Token Access
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is an Admin or DevOps
- Legacy tokens exist
#### Test Steps
1. Check access level of legacy tokens
#### Expected Results
- Legacy tokens have Global Access
- Tooltip indicates 'Token has access to all apps'

