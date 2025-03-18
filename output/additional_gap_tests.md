# Additional Tests for Gaps

## Gap: Unclear handling of users in multiple groups.
- **Suggested Clarification:** What happens if a user belongs to multiple groups? Should the token have access to all groups or just the group at the time of token creation?
- **Confidence Level:** Medium

### GT011: Verify access for non-legacy token with multiple groups
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User is a member of multiple groups
  - User has created a non-legacy token
- **Steps:**
  - Log in as the user who created the non-legacy token.
  - Check the groups the user belongs to at the time of token creation.
  - Use the non-legacy token to access applications.
- **Expected Results:**
  - The token should only provide access to the applications of the group the user was in at the time of token creation, not all groups.

### GT012: Verify token access after user group change
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User has a non-legacy token
  - User belongs to multiple groups
- **Steps:**
  - Change the user's group membership after the token has been created.
  - Use the non-legacy token to access applications.
- **Expected Results:**
  - The token should still limit access to the applications of the group the user was in at the time of token creation.

### GT013: Verify deactivation of non-legacy token upon user deactivation
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User has a non-legacy token
  - User is active
- **Steps:**
  - Deactivate the user account.
  - Attempt to use the non-legacy token.
- **Expected Results:**
  - The non-legacy token should be automatically deactivated and not allow access to any applications.

### GT014: Verify deletion of non-legacy token upon user deletion
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User has a non-legacy token
  - User is active
- **Steps:**
  - Delete the user account.
  - Attempt to use the non-legacy token.
- **Expected Results:**
  - The non-legacy token should be automatically deleted and not allow access to any applications.

### GT015: Verify legacy token visibility for Admin/DevOps
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - Admin/DevOps user account
  - Legacy tokens exist
- **Steps:**
  - Log in as an Admin/DevOps user.
  - Navigate to the legacy tokens section.
- **Expected Results:**
  - Admin/DevOps user should be able to view all legacy tokens, including those created by other users and those with no creators.

### GT016: Verify legacy token access for Regular/Limited users
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - Regular/Limited user account
  - Legacy tokens exist
- **Steps:**
  - Log in as a Regular/Limited user.
  - Navigate to the legacy tokens section.
- **Expected Results:**
  - Regular/Limited user should not be able to view any legacy tokens, including their own.

## Gap: Lack of detail on reactivation of users.
- **Suggested Clarification:** What is the expected behavior if a deactivated user is reactivated? Should their token be reactivated automatically?
- **Confidence Level:** Medium

### GT017: Verify token deactivation for deactivated user
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User account is active
  - User has created a non-legacy extension token
- **Steps:**
  - Deactivate the user account
  - Attempt to use the non-legacy extension token
- **Expected Results:**
  - The non-legacy extension token is deactivated automatically
  - User cannot access applications using the token

### GT018: Verify token deletion for deleted user
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User account is active
  - User has created a non-legacy extension token
- **Steps:**
  - Delete the user account
  - Check the status of the non-legacy extension token
- **Expected Results:**
  - The non-legacy extension token is deleted automatically
  - Token is no longer accessible

### GT019: Verify token reactivation for reactivated user
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User account is deactivated
  - User has created a non-legacy extension token
- **Steps:**
  - Reactivate the user account
  - Check the status of the non-legacy extension token
- **Expected Results:**
  - The non-legacy extension token is not reactivated automatically
  - User must create a new token if needed

### GT020: Verify access level for non-legacy token
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Functional
- **Prerequisites:**
  - User account is active
  - User has created a non-legacy extension token
- **Steps:**
  - Use the non-legacy extension token
  - Check the applications accessible by the token
- **Expected Results:**
  - Token only provides access to applications of the creator at the time of token usage
  - Group Everyone is included in the access

### GT021: Verify legacy token visibility for Admin/DevOps
- **Module:** Token Management
- **Priority:** Low
- **Type:** Functional
- **Prerequisites:**
  - Admin/DevOps user account is active
  - Legacy tokens exist
- **Steps:**
  - Log in as Admin/DevOps user
  - View the list of legacy tokens
- **Expected Results:**
  - Admin/DevOps user can view all legacy tokens
  - Legacy tokens are displayed regardless of creator status

## Gap: Ambiguity in user experience for token management.
- **Suggested Clarification:** Provide more details on the user interface elements for token management, especially for different user roles.
- **Confidence Level:** High

### GT022: Verify non-legacy token creation for regular user
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User is logged in as a regular user
  - User has no existing non-legacy token
- **Steps:**
  - Navigate to the token management page
  - Click on the 'Create New Token' button
- **Expected Results:**
  - A new non-legacy token is created
  - The token appears in the token list
  - The 'Create New Token' button is disabled

### GT023: Verify tooltip for disabled 'Create New Token' button
- **Module:** Token Management
- **Priority:** Medium
- **Type:** UI
- **Prerequisites:**
  - User is logged in as a regular user
  - User has an existing non-legacy token
- **Steps:**
  - Hover over the 'Create New Token' button
- **Expected Results:**
  - Tooltip appears stating 'You can only have one non-legacy token'

### GT024: Verify access level display for non-legacy token
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User is logged in as a regular user
  - User has a non-legacy token
- **Steps:**
  - Navigate to the token management page
- **Expected Results:**
  - Access Level column shows 'Creator Access'
  - Tooltip on hover states 'Token inherits access permissions from the creator'

### GT025: Verify legacy token visibility for Admin user
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User is logged in as an Admin
  - There are existing legacy tokens
- **Steps:**
  - Navigate to the token management page
- **Expected Results:**
  - All legacy tokens are visible in the token list
  - Admin can view and delete legacy tokens

### GT026: Verify legacy token visibility for Limited user
- **Module:** Token Management
- **Priority:** High
- **Type:** Functional
- **Prerequisites:**
  - User is logged in as a Limited user
  - User has created legacy tokens
- **Steps:**
  - Navigate to the token management page
- **Expected Results:**
  - No legacy tokens are visible in the token list

### GT027: Verify actions for legacy tokens
- **Module:** Token Management
- **Priority:** Medium
- **Type:** UI
- **Prerequisites:**
  - User is logged in as a regular user
  - User has created legacy tokens
- **Steps:**
  - Navigate to the token management page
  - Attempt to copy/download/refresh a legacy token
- **Expected Results:**
  - Copy/download/refresh actions are disabled for legacy tokens

## Gap: No mention of error handling or notifications.
- **Suggested Clarification:** What notifications or error messages should be displayed to users when they attempt to perform actions that are not allowed?
- **Confidence Level:** Medium

### GT028: Attempt to create a new non-legacy token when one already exists
- **Module:** Token Management
- **Priority:** High
- **Type:** Negative
- **Prerequisites:**
  - User has an existing non-legacy token
- **Steps:**
  - Navigate to the Token Management section
  - Click on the 'Create New Token' button
- **Expected Results:**
  - The 'Create New Token' button is disabled
  - A tooltip appears stating 'You already have a non-legacy token'

### GT029: Attempt to view legacy tokens as a regular user
- **Module:** Token Management
- **Priority:** High
- **Type:** Negative
- **Prerequisites:**
  - User is a regular user
  - User has created legacy tokens
- **Steps:**
  - Navigate to the Token Management section
- **Expected Results:**
  - Legacy tokens are not displayed in the list
  - No error message is shown, but the user cannot see any legacy tokens

### GT030: Attempt to copy/download/refresh a legacy token
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Negative
- **Prerequisites:**
  - User is an admin or DevOps
  - User has access to legacy tokens
- **Steps:**
  - Navigate to the Token Management section
  - Select a legacy token
  - Attempt to copy the token
  - Attempt to download the token
  - Attempt to refresh the token
- **Expected Results:**
  - Copy, download, and refresh actions are disabled
  - No notifications are displayed for disabled actions

### GT031: Attempt to delete a legacy token as a regular user
- **Module:** Token Management
- **Priority:** High
- **Type:** Negative
- **Prerequisites:**
  - User is a regular user
  - User has created legacy tokens
- **Steps:**
  - Navigate to the Token Management section
  - Select a legacy token
  - Attempt to delete the legacy token
- **Expected Results:**
  - Delete action is disabled
  - No error message is shown, but the user cannot delete the legacy token

### GT032: Attempt to view legacy tokens as an admin user
- **Module:** Token Management
- **Priority:** Medium
- **Type:** Positive
- **Prerequisites:**
  - User is an admin
  - User has created legacy tokens
- **Steps:**
  - Navigate to the Token Management section
- **Expected Results:**
  - Legacy tokens are displayed in the list
  - User can view and delete legacy tokens

