# **Extension Tokens**

## New Extension Tokens have user-based access

- New extension tokens (aka non-legacy tokens) are **user-based** and will have access only to the groups of their creator at the time of using the token.
    
    - The group Everyone is always included.
        
    - The group Unassigned Users is included if the user is not assigned to any custom group.
        
- When using the token the BE should limit the token's responses only to applications accessible by the creator at that time.
    
    If the creator is deactivated from the account, the non-legacy extension will be automatically deactivated.
    
    If the creator is deleted from the account, the non-legacy extension will be automatically deleted.
    
    Legacy tokens will not be updated. They should continue working without any changes and will have access to all apps (Global Access). 
    

## Token Access

UX/UI Requirements. 

- New extension tokens (aka non-legacy tokens) are **user-based** and will have access only to the groups of their creator at the time of using the token.
    
    - The group Everyone is always included.
        
    - The group Unassigned Users is included if the user is not assigned to any custom group.
        
- When using the token the BE should limit the token's responses only to applications accessible by the creator at that time.
    
- If the creator is deactivated from the account, the non-legacy extension will be automatically deactivated.
    
- If the creator is deleted from the account, the non-legacy extension will be automatically deleted.
    
- Legacy tokens will not be updated. They should continue working without any changes and will have access to all apps (Global Access). 
    

**No UI is required for this use case.** 

## Token Management

**Users can have only one non-legacy extension token**

UX/UI Requirements. 

- All users (regular, limited, admin, devops) can have **only one** non-legacy token.
    
    - They can view / copy / download / refresh / delete this token.
        
        The **Create New Token** button is disabled, in case a new token already appears on the list.
        
        - In this case, the proper tooltip appears on hover. 
            
    - The token's access will appear in the Access Level column: Creator Access and the the following tooltip on hover: Token inherits access permissions from the creator.
        

**Legacy extension tokens are only visitable to Admin/DevOps**  

- Regular users or Limited users **cannot view** any legacy tokens, including:
    
    - Legacy tokens they have created. These tokens will not be displayed on the list (even though they are still active).
        
    - Legacy tokens with no creators will not appear on the list (even though they are still active).
        
- Admin / DevOps users **can view** and **delete all legacy tokens**, including:
    
    - Legacy tokens they have created.
        
    - Legacy tokens other users have created.
        
    - Legacy tokens with no creators.
        
- No user can copy/download/refresh legacy tokens. These actions will appear disabled for legacy extension tokens.
    
- Legacy tokens will have Global Access (access to all apps, as of today). This will be indicated in the Access Level column. With the tooltip: Token has access to all apps.