## Edge Case Test Suite for Extension Tokens

### Test Case EDGE-001
**Module:** Token Management
**Priority:** High
**Type:** Error Handling
#### Test Steps
1. Create a non-legacy token for a user.
2. Deactivate the user account.
3. Attempt to use the non-legacy token.
#### Expected Results
- The non-legacy token is automatically deactivated.
- The system returns an error indicating the token is no longer valid.

### Test Case EDGE-002
**Module:** Token Management
**Priority:** High
**Type:** Error Handling
#### Test Steps
1. Create a non-legacy token for a user.
2. Delete the user account.
3. Attempt to use the non-legacy token.
#### Expected Results
- The non-legacy token is automatically deleted.
- The system returns an error indicating the token does not exist.

### Test Case EDGE-003
**Module:** Token Management
**Priority:** Medium
**Type:** Concurrency
#### Test Steps
1. Create a non-legacy token for a user.
2. Simultaneously attempt to create a second non-legacy token for the same user.
#### Expected Results
- The system prevents the creation of a second non-legacy token.
- A tooltip appears indicating that the user can only have one non-legacy token.

### Test Case EDGE-004
**Module:** Token Access
**Priority:** Medium
**Type:** Integration
#### Test Steps
1. Create a non-legacy token for a user assigned to a custom group.
2. Remove the user from the custom group.
3. Use the token to access applications.
#### Expected Results
- The token's responses are limited to applications accessible by the user at the time of using the token.
- The system does not return applications from the removed custom group.

### Test Case EDGE-005
**Module:** Token Management
**Priority:** Low
**Type:** Error Handling
#### Test Steps
1. Attempt to view legacy tokens as a regular user.
2. Attempt to view legacy tokens as an admin user.
#### Expected Results
- Regular users cannot view any legacy tokens.
- Admin users can view all legacy tokens.

