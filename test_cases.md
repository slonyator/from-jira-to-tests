# Test Suite: Token Access & Management
*Generated on: 2025-03-16*

## Extension Tokens Test Suite

### Test Case TC-001: Create Non-Legacy Token
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

### Test Case TC-002: View Non-Legacy Token Access
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

### Test Case TC-003: Token Access Limitations for Deactivated User
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

### Test Case TC-004: Token Access Limitations for Deleted User
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

### Test Case TC-005: View Legacy Tokens as Admin
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

### Test Case TC-006: Legacy Token Access for Regular Users
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

### Test Case TC-007: Disable Actions for Legacy Tokens
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

### Test Case EC-001: Reactivation of Deactivated User
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
- Token is reactivated
- User can access applications with the token

### Test Case EC-002: User in Multiple Groups at Token Creation
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is logged in
- User belongs to multiple groups
#### Test Steps
1. Create a non-legacy token
#### Expected Results
- Token inherits access from all groups the user belongs to
- Access Level reflects combined group access

### Test Case EC-003: Legacy Token Visibility for Deleted User
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User has created a legacy token
- User is deleted from the account
#### Test Steps
1. Log in as Admin/DevOps
2. Navigate to the token management page
#### Expected Results
- Legacy token created by the deleted user is still visible
- Admin/DevOps can delete the legacy token

### Test Case EC-004: Token Access After Group Assignment Change
**Module:** Token Access
**Priority:** High
**Type:** Functional
#### Prerequisites
- User has a non-legacy token
- User is assigned to a custom group
#### Test Steps
1. Change the user's group assignment
2. Attempt to use the non-legacy token
#### Expected Results
- Token access is updated based on new group assignments
- User can only access applications in the new group

### Test Case EC-005: Legacy Token Access for Admin/DevOps
**Module:** Token Management
**Priority:** Medium
**Type:** Functional
#### Prerequisites
- User is logged in as Admin/DevOps
- Legacy tokens are present
#### Test Steps
1. Attempt to copy/download/refresh a legacy token
#### Expected Results
- Actions are disabled for legacy tokens
- Admin/DevOps can only view and delete

