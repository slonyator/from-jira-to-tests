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
- New non-legacy token is created
- Token is displayed in the token list
- 'Create New Token' button is disabled

### Test Case TC-002
**Module:** Token Access Control
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
#### Test Steps
1. Use the token to access applications
#### Expected Results
- Access is limited to the groups of the creator at the time of using the token
- Group 'Everyone' is always included
- Group 'Unassigned Users' is included if applicable

### Test Case TC-003
**Module:** Token Deactivation
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
- User is deactivated
#### Test Steps
1. Attempt to use the non-legacy token
#### Expected Results
- Token is automatically deactivated
- User cannot access applications using the token

### Test Case TC-004
**Module:** Token Deletion
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
- User is deleted from the account
#### Test Steps
1. Attempt to use the non-legacy token
#### Expected Results
- Token is automatically deleted
- User cannot access applications using the token

### Test Case TC-005
**Module:** Legacy Token Visibility
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is a regular or limited user
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
- Admin can delete any legacy token
- Admin cannot copy/download/refresh legacy tokens

### Test Case TC-007
**Module:** Token Tooltip Verification
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has created a non-legacy token
#### Test Steps
1. Hover over the token access level column
#### Expected Results
- Tooltip appears: 'Token inherits access permissions from the creator'

### Test Case TC-008
**Module:** Legacy Token Access Level
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is an Admin or DevOps
#### Test Steps
1. Navigate to the token management page
2. Check the access level of legacy tokens
#### Expected Results
- Legacy tokens show 'Global Access' in the access level column
- Tooltip appears: 'Token has access to all apps'

