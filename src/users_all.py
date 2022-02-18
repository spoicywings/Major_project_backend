from src.data_store import data_store
from src.other import check_valid_token

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details
    
    Arguments:
        token (string)
        
    Exceptions:
        N/A
        
    Return value:
        { users }
    '''
    
    # Check the token is valid
    check_valid_token(token)
    
    store = data_store.get()
    
    # Create a new empty list
    users_list = []
    
    # Get every user and add their details to an empty dictionary
    for user in store['users']:
        if user['name_first'] != 'Removed' and user['name_last'] != 'user':
            users_dict = {}
        
            users_dict['u_id'] = user['u_id']
            users_dict['email'] = user['email']
            users_dict['name_first'] = user['name_first']
            users_dict['name_last'] = user['name_last']
            users_dict['handle_str'] = user['handle_str']
            users_dict['profile_img_url'] = user['profile_img_url']
        
            # Append the user details to the list
            users_list.append(users_dict)
    
    # Return the list
    return {
        'users': users_list
    }
    
