### Test Case EXT-001: New Extension Token Creation
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
- Only one non-legacy token allowed per user