from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token, generate_message_id, search_message
from src.stats import increase_num_msgs_sent, increase_msgs_exist
from datetime import datetime
from src.notifications import update_notification_tagged, update_notification_react

def message_senddm_v1(token, dm_id, message):
    '''
    Send a message from authorised_user to the DM specified by dm_id and stores
    message in data store

    Arguments:
        - token (string)
        - dm_id (integer)
        - message (string)

    Exceptions:
        InputError - when dm_id does not refer to a valid DM
        InputError - when length of message is less than 1 or over 1000 characters
        AccessError - when token is invalid
        AccessError - when dm_id is valid and the authorised user is not a member of the DM

    Return value:
        { }
    '''

    store = data_store.get()
    dm_messages_dict = {}

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
    
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="length of message is less than 1 or over 1000 characters")
    
    # Generates new message_id then stores it
    message_id = generate_message_id()
    dm_messages_dict['message_id'] = message_id
    
    for user in store['users']:
        if token_user['u_id'] == user['u_id']:
            dm_messages_dict['u_id'] = user['u_id']
    
    # Stores message to data store
    dm_messages_dict['message'] = message
    
    # Get current Unix timestamp then store
    timestamp = int(datetime.now().timestamp())
    dm_messages_dict['time_created'] = timestamp
    dm_messages_dict['reacts'] = [{'react_id': 1, 'u_ids' : [], 'is_this_user_reacted' : False}]
    dm_messages_dict['is_pinned'] = False
    
    # Stores the message into the correct dm
    dm['messages'].insert(0, dm_messages_dict)
    
    data_store.set(store)
    
    increase_num_msgs_sent(token_user['u_id'])
    increase_msgs_exist()
    
    # Update notication for tagged
    update_notification_tagged(token_user['u_id'], dm_id, message, False, True)
    
    return {
        'message_id': message_id
    }
   
def message_react_v1(token, message_id, react_id):
    '''
    User react to a message with a given react_id

    Arguments:
        - token (string)
        - message_id(integer)
        - react_id (integer)

    Exceptions:
        InputError - when message_id is not valid in the channel/dm is user is in
        InputError - message already contains a react from the user
        InputError - when react_id is not valid
        
    Return value:
        { }
    '''
    store = data_store.get()
    decode = check_valid_token(token)
    
    user_details = {}
    # Fetches data of the user
    for user in store['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user
    
    valid_react_id = [1]
    
    # Error if react_id is invalid
    if react_id not in valid_react_id:
        raise InputError(description="Invalid react id")
    
    message_return = search_message(message_id)
    
    # Error is message id is invalid
    if message_return[0] == False:
        raise InputError(description="Invalid message id")
    else:
        index = message_return[1] - 1
        m_index = message_return[3] - 1 
        if message_return[2] == 0:
            channel_message_action(index, m_index, user_details, react_id, "react")
                    
        if message_return[2] == 1:
            dm_message_action(index, m_index, user_details, react_id, "react")
           
    # Update notication for react
    update_notification_react(decode['u_id'], message_id)
    
    data_store.set(store)
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    User unreact to a message with a given react_id

    Arguments:
        - token (string)
        - message_id(integer)
        - react_id (integer)

    Exceptions:
        InputError - when message_id is not valid in the channel/dm is user is in
        InputError - message already contains a react from the user
        InputError - when react_id is not valid
        
    Return value:
        { }
    '''
    store = data_store.get()
    decode = check_valid_token(token)
    
    user_details = {}
    # Fetches data of the user
    for user in store['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user
    
    valid_react_id = [1]
    
    # Error if react_id is invalid
    if react_id not in valid_react_id:
        raise InputError(description="Invalid react id")
    
    message_return = search_message(message_id)
    
    # Error is message id is invalid
    if message_return[0] == False:
        raise InputError(description="Invalid message id")
    else:
        index = message_return[1] - 1
        m_index = message_return[3] - 1 
        if message_return[2] == 0:
            channel_message_action(index, m_index, user_details, react_id, "unreact")
                    
        if message_return[2] == 1:
            dm_message_action(index, m_index, user_details, react_id, "unreact")
    data_store.set(store)
    return {}


# A function which will react or unreact a message in a channel given the action,
# message_id and react_id
def channel_message_action(index, m_index, user_details, react_id, action):
    store = data_store.get()
    get_channel = store['channels'][index]
    # Error if user not in channel
    if user_details not in get_channel['all_members']:
        raise InputError(description="You are not in this channel")
    else:
        get_message = get_channel['messages'][m_index]
        user_react = user_details['u_id']
        if action == "react": 
            reaction = get_message['reacts'][0]
            # Raise error if there is already same reaction by the same user
            if user_react in reaction['u_ids'] and reaction['react_id'] == react_id:
                raise InputError(description="You have already react to this message with this reaction")
            reaction['u_ids'].append(user_react)
            reaction['is_this_user_reacted'] = True
                
        if action == "unreact":
            remove = False
            reaction = get_message['reacts'][0]
            if user_react in reaction['u_ids']:
                reaction['u_ids'].remove(user_react)
                reaction['is_this_user_reacted'] = False
                remove = True
            if remove == False:
                # Error if there is no reaction from the user
                raise InputError(description="Message has no reaction of the reaction")
                    
        if action == "pin":
            # Error if message is already pinned
            if get_message['is_pinned'] == True:
                raise InputError(description="Message is already pinned")
            # Error if user does not have owner permission
            if user_details not in get_channel['owner_members']:
                raise InputError(description="You do not have permission to pin")
            get_message['is_pinned'] = True
            
        if action == "unpin":
            # Default is false hence already unpinned
            if user_details not in get_channel['owner_members']:
                raise InputError(description="You do not have permission to pin")
            if get_message['is_pinned'] == False:
                raise InputError(description="Message is already unpinned")
            get_message['is_pinned'] = False
            
    data_store.set(store)
    return {}
    
# A function which will react or unreact a dm in a channel given the action,
# message_id and react_id
def dm_message_action(index, m_index, user_details, react_id, action):
    store = data_store.get()
    get_dms = store['dms'][index]
    # Error if user not in dms
    if user_details not in get_dms['members']:
        raise InputError(description="You are not in this dm")
    else:
        get_message = get_dms['messages'][m_index]
        user_react = user_details['u_id']
        if action == "react":
            reaction = get_message['reacts'][0]
            if user_react in reaction['u_ids'] and reaction['react_id'] == react_id:
                raise InputError(description="You have already react to this message with this reaction")
            reaction['u_ids'].append(user_react)
            reaction['is_this_user_reacted'] = True 
                
        if action == "unreact":
            remove = False
            reaction = get_message['reacts'][0]
            if user_react in reaction['u_ids'] and reaction['react_id'] == react_id:
                remove = True
                reaction['u_ids'].remove(user_react)
                reaction['is_this_user_reacted'] = False 
            if remove == False:
                raise InputError(description="Message has no reaction of the reaction")
                    
        if action == "pin":
            if get_message['is_pinned'] == True:
                raise InputError(description="Message is already pinned")
            if user_details['u_id'] != get_dms['owner']['u_id']:
                raise InputError(description="You do not have permission to pin")
            get_message['is_pinned'] = True
            
        if action == "unpin":
            if user_details['u_id'] != get_dms['owner']['u_id']:
                raise InputError(description="You do not have permission to pin")
            if get_message['is_pinned'] == False:
                raise InputError(description="Message is already unpinned")
            get_message['is_pinned'] = False
            
    data_store.set(store)
    return {}

def message_pin_v1(token, message_id):      
    '''
    User pin a message with a given message_id

    Arguments:
        - token (string)
        - message_id(integer)
        - react_id (integer)

    Exceptions:
        InputError - when message_id is not valid in the channel/dm is user is in
        InputError - user does not have owner permission
        InputError - message is already pinned
        
    Return value:
        { }
    '''
    store = data_store.get()
    decode = check_valid_token(token)
    
    user_details = {}
    # Fetches data of the user
    for user in store['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user

    message_return = search_message(message_id)
    
    # Error is message id is invalid
    if message_return[0] == False:
        raise InputError(description="Invalid message id")
    else:
        index = message_return[1] - 1
        m_index = message_return[3] - 1 
        if message_return[2] == 0:
            channel_message_action(index, m_index, user_details, -1, "pin")
                    
        if message_return[2] == 1:
            dm_message_action(index, m_index, user_details, -1, "pin")
    return {} 

def message_unpin_v1(token, message_id):
    '''
    User pin a message with a given message_id

    Arguments:
        - token (string)
        - message_id(integer)
        - react_id (integer)

    Exceptions:
        InputError - when message_id is not valid in the channel/dm is user is in
        InputError - user does not have owner permission
        InputError - message is already unpinned
        
    Return value:
        { }
    '''
    store = data_store.get()
    decode = check_valid_token(token)
    
    user_details = {}
    # Fetches data of the user
    for user in store['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user

    message_return = search_message(message_id)
    
    # Error is message id is invalid
    if message_return[0] == False:
        raise InputError(description="Invalid message id")
    else:
        index = message_return[1] - 1
        m_index = message_return[3] - 1 
        if message_return[2] == 0:
            channel_message_action(index, m_index, user_details, -1, "unpin")
                    
        if message_return[2] == 1:
            dm_message_action(index, m_index, user_details, -1, "unpin")
    data_store.set(store)
    return {}
