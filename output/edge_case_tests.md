# Edge Case Tests

## EC006: Reactivation of Deactivated User
- **Module:** Token Access
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User has a non-legacy token
  - User is deactivated
- **Steps:**
  - Reactivate the user account
  - Attempt to use the non-legacy token
- **Expected Results:**
  - Token is reactivated
  - User can access applications with the token

## EC007: User in Multiple Groups at Token Creation
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User is logged in
  - User belongs to multiple groups
- **Steps:**
  - Create a non-legacy token
- **Expected Results:**
  - Token inherits access from all groups the user belongs to
  - Access Level reflects combined group access

## EC008: Legacy Token Visibility for Deleted User
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User has created a legacy token
  - User is deleted from the account
- **Steps:**
  - Log in as Admin/DevOps
  - Navigate to the token management page
- **Expected Results:**
  - Legacy token created by the deleted user is still visible
  - Admin/DevOps can delete the legacy token

## EC009: Token Access After Group Assignment Change
- **Module:** Token Access
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User has a non-legacy token
  - User is assigned to a custom group
- **Steps:**
  - Change the user's group assignment
  - Attempt to use the non-legacy token
- **Expected Results:**
  - Token access is updated based on new group assignments
  - User can only access applications in the new group

## EC010: Legacy Token Access for Admin/DevOps
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User is logged in as Admin/DevOps
  - Legacy tokens are present
- **Steps:**
  - Attempt to copy/download/refresh a legacy token
- **Expected Results:**
  - Actions are disabled for legacy tokens
  - Admin/DevOps can only view and delete

