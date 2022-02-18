from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token
from src.stats import increase_num_dms_joined, decrease_num_dms_joined
from src.stats import increase_dms_exist, decrease_dms_exist, decrease_msgs_exist
from src.notifications import update_notification_added_dm

def dm_create_v1(token, u_ids):
    '''
    Creates a DM using token and u_ids and returns the dm_id

    Arguments:
        - token (string)
        - u_ids (list of integers)

    Exceptions:
        InputError - when any u_id in u_ids does not refer to a valid user
        AccessError - when token is invalid

    Return value:
        { dm_id }
    '''

    store = data_store.get()
    name = []
    dm_dict = {}
    dm_members = []
    dm_messages = []

    dm_id = len(store['dms']) +1
    
    # If token is invalid, AccessError is raised
    # else the payload is returned
    owner = check_valid_token(token)
    
    # Finding user of token (owner)
    for user in store['users']:
        for sess_id in user['session_id']:
            if owner['u_id'] == user['u_id'] and owner['session_id'] == sess_id:
                # Add the creator/owner's handle to name
                name.append(user['handle_str'])
                # Storing owner of dm
                dm_dict['owner'] = user
                # Adding owner to dm_members
                dm_members.append(user)
                break
    
    # Adds the users' handles in name
    for u_id in u_ids:
        for user in store['users']:
            if u_id == user['u_id']:
                name.append(user['handle_str'])
                # Adding valid user to dm_members
                dm_members.append(user)
                break
    
    # If there is an invalid u_id in u_ids then
    # length of name will be not equal length of u_ids
    # Thus there is an InputError
    if len(name) != len(u_ids) + 1:
        raise InputError(description="Invalid user id")
    
    # Alphabetically sorts the list 'name'
    name.sort()

    # Creating and storing the dm_id
    dm_dict['dm_id'] = dm_id

    # Converting 'name' to str then storing
    dm_dict['name'] = ", ".join(name)

    # Storing dm_members to data store
    dm_dict['members'] = dm_members
    
    # Storing dm_messages to data store
    dm_dict['messages'] = dm_messages

    # Append the dm's data to the data store
    store['dms'].append(dm_dict)

    data_store.set(store)
    
    # Increase dms joined for owner of dm
    increase_num_dms_joined(owner['u_id'])
    
    # Increase dms joined for all other users in dm
    for u_id in u_ids:
        if u_id != owner['u_id']:
            increase_num_dms_joined(u_id)
        # Add notification to user
        update_notification_added_dm(owner['u_id'], u_id, dm_id)
    
    # Increase the number of dms that exist in workplace stats
    increase_dms_exist()
            
    return {
        'dm_id': dm_id
    }
    
def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of

    Arguments:
        - token (string)

    Exceptions:
        AccessError - when token is invalid

    Return value:
        { dms }
    '''

    store = data_store.get()
    dms = []

    # Finding user of token
    decoded_token = check_valid_token(token)

    # Find all the dms that user is in
    for dm in store['dms']:
        for user in dm['members']:
            if decoded_token['u_id'] == user['u_id']:
                dms.append({'dm_id': dm['dm_id'], 'name': dm['name']})

    return {
        'dms': dms
    }
    
def dm_remove_v1(token, dm_id):
    '''
    Removes an existing DM but only the original creator of the DM can

    Arguments:
        - token (string)
        - dm_id (integer)

    Exceptions:
        InputError - when dm_id does not refer to a valid DM
        AccessError - when token is invalid
        AccessError - when dm_id is valid and the authorised user is not the original DM creator

    Return value:
        { }
    '''

    store = data_store.get()

    # Finding user of token
    token_user = check_valid_token(token)

    # Raise an InputError if dm_id is invalid
    valid_dm_id = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm_details = dm
            valid_dm_id = True

    if valid_dm_id == False:
        raise InputError(description="dm_id does not refer to a valid DM")

    # Raise an AccessError if dm_id is valid and user is not a owner of the DM
    # If user is owner then remove the DM
    valid_owner = False
    for dm in store['dms']:
        if token_user['u_id'] == dm['owner']['u_id'] and dm_id == dm['dm_id']:
            valid_owner = True
            store['dms'].remove(dm)

    if valid_owner == False:
        raise AccessError(description="dm_id is valid and the authorised user is not the original DM creator")

    data_store.set(store)
    
    # Decrease dms joined for owner of dm
    decrease_num_dms_joined(token_user['u_id'])
    
    # Decrease dms joined for all other members of dm
    for members in dm_details['members']:
        if members['u_id'] != token_user['u_id']:
            decrease_num_dms_joined(members['u_id'])
            
    # Decrease the number of dms that exist in workplace stats
    decrease_dms_exist()
    
    num_msgs_to_remove = len(dm_details['messages'])
    decrease_msgs_exist(num_msgs_to_remove)

    return {
    }

def dm_details_v1(token, dm_id):
    '''
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM

    Arguments:
        - token (string)
        - dm_id (integer)

    Exceptions:
        InputError - when dm_id does not refer to a valid DM
        AccessError - when token is invalid
        AccessError - when dm_id is valid and the authorised user is not a member of the DM

    Return value:
        { name, members }
    '''

    store = data_store.get()

    # Finding user of token
    token_user = check_valid_token(token)

    # Raise an InputError if dm_id is invalid
    valid_dm_id = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            valid_dm_id = True
            break

    if valid_dm_id == False:
        raise InputError(description="dm_id does not refer to a valid DM")

    # Raise an AccessError if dm_id is valid and user is not a member of the DM
    valid_member = False
    for member in dm['members']:
        if token_user['u_id'] == member['u_id']:
            valid_member = True
            break

    if valid_member == False:
        raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM")

    return {
        'name': dm['name'],
        'members': dm['members']
    }

def dm_leave_v1(token, dm_id):
    '''
    Removes a member of DM but name of DM is not updated

    Arguments:
        - token (string)
        - dm_id (integer)

    Exceptions:
        InputError - when dm_id does not refer to a valid DM
        AccessError - when token is invalid
        AccessError - when dm_id is valid and the authorised user is not a member of the DM

    Return value:
        { }
    '''

    store = data_store.get()

    # Finding user of token
    token_user = check_valid_token(token)

    # Raise an InputError if dm_id is invalid
    valid_dm_id = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            valid_dm_id = True
            break

    if valid_dm_id == False:
        raise InputError(description="dm_id does not refer to a valid DM")

    # Raise an AccessError if dm_id is valid and user is not a member of the DM
    valid_member = False
    for member in dm['members']:
        if token_user['u_id'] == member['u_id']:
	        dm['members'].remove(member)
	        valid_member = True
	        break

    if valid_member == False:
        raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM")

    if token_user['u_id'] == dm['owner']['u_id']:
        dm['owner'] = None
    
    # Decrease dms joined for user that left
    decrease_num_dms_joined(token_user['u_id'])
    
    return {
    }
    
def dm_messages_v1(token, dm_id, start):
    '''
    Returns up to 50 messages in a given DM

    Arguments:
        - token (sting)
        - dm_id (integer)
        - start (integer)

    Exceptions:
        InputError - when dm_id does not refer to a valid DM
        InputError - start is greater than the total number of messages in the channel
        AccessError - when token is invalid
        AccessError - when dm_id is valid and the authorised user is not a member of the DM

    Return value:
        { messages, start, end }
    '''

    store = data_store.get()
    
    # Finding user of token
    token_user = check_valid_token(token)
    
    # Raise an InputError if dm_id is invalid
    valid_dm_id = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            valid_dm_id = True
            break
    
    if valid_dm_id == False:
        raise InputError(description="dm_id does not refer to a valid DM")
    
    # Raise an AccessError if dm_id is valid and user is not a member of the DM
    valid_member = False
    for member in dm['members']:
        if token_user['u_id'] == member['u_id']:
	        valid_member = True
	        break

    if valid_member == False:
        raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM")
    
    # Raise an InputError when start is greater than total number of messages in DM
    if start > len(dm['messages']):
        raise InputError(description="start is greater than the total number of messages in the DM")
    
    messages = []
    end = 0
    
    for message in dm['messages']:
        if end < start:
            end += 1
        elif end == start + 50:
            break
        else:
            messages.append(message)
            end += 1
    
    if end == len(dm['messages']):
        end = -1
    
    return {
        'messages': messages,
        'start': start,
        'end': end
    }
