from src.data_store import data_store
from src.other import check_valid_token, decode_jwt
from src.error import InputError, AccessError

def count_global_owners():
    store = data_store.get()
    number_of_global = 0
    for user in store['users']:
        if user['global_owner'] == True:
            number_of_global += 1
    return number_of_global        

def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    If the token is a global owner, then change the permssion of the user given 
    by their u_id
    
    Arguments:
        - token (string)
        - u_id (integer)
        - permission_id (integer)
        
    Exceptions:
        InputError:
            - u_id does not exist
            - u_id refers to the only existing global owner
            - permission_id is invalid
            
        AccessError:
            - token is not a global owner
    '''
    
    # Check if the token is valid
    decode = check_valid_token(token)
    input_id = permission_id
    # Check if u_id is valid
    store = data_store.get()
    valid_user = False
    for user in store['users']:
        if user['u_id'] == u_id:
            valid_user = True
            break
    if valid_user == False:
        raise InputError(description="Invalid user id")
    
    # Check if permission_id is valid
    valid_permission = [1, 2]
    if permission_id not in valid_permission:
        raise InputError(description="Invalid permission id")

    
    num_global_owners = count_global_owners()
    
    # Searches and fetches the user by their u_id
    target_user = {}
    auth_user = {}
    for user in store['users']:
        if user['u_id'] == u_id:
            target_user = user
        if user['u_id'] == decode['u_id']:
            auth_user = user
                
    # If the auth_user is not a global_owner
    if auth_user['global_owner'] == False:
        raise AccessError(description="You do not have permission to perform this action")
    
    if input_id == 1:
        # If no error appears then promote the user
        target_user['global_owner'] = True
        target_user['global_member'] = False
        data_store.set(store)    
        
    if input_id == 2:
        # If the only global user tries to demote themselves raise error
        if target_user['u_id'] == decode['u_id'] and num_global_owners == 1:        
            raise InputError(description="Cannot not demote yourself")
        
        
        # If no error appears then demote the user
        target_user['global_owner'] = False
        target_user['global_member'] = True
        data_store.set(store)

    return {
    }    

def admin_user_remove_v1(token, u_id):
    '''
    If the token is a global owner, remove a user given by their u_id
    
    Arguments:
        - token (string)
        - u_id (integer)
        
    Exceptions:
        InputError:
            - u_id does not exist
            - u_id refers to the only existing global owner
            
        AccessError:
            - token is not a global owner
    '''
    # Check if the token is valid
    decode = check_valid_token(token)
    
    # Check if u_id is valid
    store = data_store.get()
    valid_user = False
    for user in store['users']:
        if user['u_id'] == u_id:
            valid_user = True
            break
    if valid_user == False:
        raise InputError(description="Invalid user id")
    
    num_global_owners = count_global_owners()
    
    # Searches and fetches the user and the autherised user
    target_user = {}
    auth_user = {}
    for user in store['users']:
        if user['u_id'] == u_id:
            target_user = user
        if user['u_id'] == decode['u_id']:
            auth_user = user
    
    
    if auth_user['global_owner'] == False:
        raise AccessError(description="You do not have permission to perform this action")
        
    if auth_user['global_owner'] == True:
        if num_global_owners == 1 and auth_user['u_id'] == target_user['u_id']:
            raise InputError(description="You are the only global owner, need more owners") 
        else:
            # Remove the user from all channels
            for channel in store['channels']:
                if target_user in channel['all_members']:
                    channel['all_members'].remove(target_user)
                if target_user in channel['owner_members']:
                    channel['owner_members'].remove(target_user)
                # Remove the message sent by that user in the channels
                for message in channel['messages']:
                    if message['u_id'] == target_user['u_id']:
                        message['u_id'] = "Removed user"
            # Remove the user from all dms
            for dm in store['dms']:
                if target_user == dm['owner']:
                    dm['owner'] == ""
                if target_user in dm['members']:
                    dm['members'].remove(target_user)
                # Remove the message sent by that user in the dms
                for message in dm['messages']:
                    if message['u_id'] == target_user['u_id']:
                        message['u_id'] = "Removed user"
                        message['message'] = "Removed user"
             
            # After removing them from channels and dms
            # change their name to Removed User and remove their 
            # email and handle so it can be still reuseable
            target_user['name_first'] = "Removed"
            target_user['name_last'] = "user"
            target_user['email'] = ""
            target_user['handle_str'] = ""
            
    data_store.set(store)

    return {
    }   
            
            
    
