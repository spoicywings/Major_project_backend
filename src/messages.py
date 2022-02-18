from src.data_store import data_store
from src.error import InputError, AccessError
from datetime import datetime
from src.other import check_valid_token, generate_message_id
from src.other import decode_jwt
from src.stats import increase_num_msgs_sent, increase_msgs_exist, decrease_msgs_exist
from src.message import message_senddm_v1
from src.notifications import update_notification_tagged
from time import sleep

def message_send_v1(token, channel_id, message):
    '''
    Given a user's token, valid channel id, and message, sends a message and returns the created message_id

    Arguments:
        - token,
        - channel_id,
        - message

    Exceptions:
        InputError - channel_id is invalid
        InputError - length of message is < 1 or > 1000 characters
        AccessError - channel_id is valid but authorised user is not a member

    Return value:
        { message_id }
    '''

    store = data_store.get()
    decode = check_valid_token(token)
    
    # Check if channel id is valid
    check_valid_channel(channel_id)

    # Check if user has access to the channel
    check_channel_access(decode, channel_id)

    # Check if number of messages is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError('Message character number invalid')
        
    # CREATE MESSAGE ID - PUT THIS IN A SEPARATE HELPER FUNCTION, ADD TO DATASTORE
    message_id = generate_message_id()

    # CREATE MESSAGE TIMESTAMP
    time_created = datetime.now().timestamp()

    # ADD MESSAGE TO CHANNEL
    new_message = {
        'message_id': message_id,
        'u_id': decode['u_id'],
        'message': message,
        'time_created': time_created,
        'reacts': [{'react_id': 1, 'u_ids' : [], 'is_this_user_reacted' : False}],
        'is_pinned': False
    }
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            channel['messages'].insert(0, new_message)

    data_store.set(store)
    
    increase_num_msgs_sent(decode['u_id'])
    increase_msgs_exist()

    # Update notication for tagged
    update_notification_tagged(decode['u_id'], channel_id, message, True, False)

    return {
        'message_id': message_id
    }



def message_edit_v1(token, message_id, message):
    '''
    Given a user's token, valid message id, and message, edits the message

    Arguments:
        - token,
        - message_id,
        - message

    Exceptions:
        InputError - length of message > 1000 characters
        InputError - message_id does not exist in the channel or DM
        AccessError - message was not sent by requesting user
        AccessError - authorised user does not have owner permissions

    Return value:
        {}
    '''

    store = data_store.get()
    decode = check_valid_token(token)
    
    '''
    # Check is message id is valid
    message_valid = check_messageid_valid(decode['u_id'], message_id)

    # Check if authorised user is owner of message
    user_is_owner = check_user_is_owner(decode['u_id'], message_valid)

    # Check if authorised user is owner of channel
    check_user_own_message(decode['u_id'], in_channel, in_dm)
    '''
    
    in_channel, in_dm = check_messageid_valid(decode['u_id'], message_id)
    
    user_own_message = check_user_own_message(decode['u_id'], message_id, in_channel, in_dm)
    user_is_owner = check_user_is_owner(decode['u_id'], in_channel, in_dm)
    
    if user_own_message == False and user_is_owner == False:
        raise AccessError(description = 'Message not sent by requested user')
    
    if len(message) > 1000:
        raise InputError(description = 'Message character number invalid')
    
    # ACTUAL FUNCTION

    # Delete message if it is empty
    if len(message) == 0:
        message_remove_v1(token, message_id)
    
    # Edit message if not empty
    chat_id = None
    in_channel = False
    in_dm = False
    for channel in store['channels']:
        for messages in channel['messages']:
            if int(message_id) == int(messages['message_id']):
                chat_id = channel['channel_id']
                in_channel = True
                messages['message'] = message
                break
                
    for dm in store['dms']:
        for messages in dm['messages']:
            if int(message_id) == int(messages['message_id']):
                chat_id = dm['dm_id']
                in_dm = True
                messages['message'] = message
                break
    
    # Update notication for tagged
    update_notification_tagged(decode['u_id'], chat_id, message, in_channel, in_dm)

    data_store.set(store)

    return {}

def message_remove_v1(token, message_id):
    '''
    Given a user's token, valid message id, removes the message

    Arguments:
        - token,
        - message_id,

    Exceptions:
        InputError - message_id does not exist in the channel or DM
        AccessError - message was not sent by requesting user
        AccessError - authorised user does not have owner permissions

    Return value:
        {}
    '''

    store = data_store.get()
    decode = check_valid_token(token)
    # ERROR VALIDATIONS 

    in_channel, in_dm = check_messageid_valid(decode['u_id'], message_id)
    
    user_own_message = check_user_own_message(decode['u_id'], message_id, in_channel, in_dm)
    user_is_owner = check_user_is_owner(decode['u_id'], in_channel, in_dm)
        
    if user_own_message == False and user_is_owner == False:
        raise AccessError(description = 'Message not sent by requested user')
    
    # FUNCTION TO DELETE MESSAGE
    for channel in store['channels']:
        for messages in channel['messages']:
            if int(message_id) == int(messages['message_id']):
                channel['messages'].remove(messages)
                break
    
    for dm in store['dms']:
        for message in dm['messages']:
            if int(message_id) == int(message['message_id']):
                dm['messages'].remove(message)
                break
    
    data_store.set(store)
    
    decrease_msgs_exist(1)

    return {}

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Given a user's token, channel_id, message, and time, sends message at specified time

    Arguments:
        - token,
        - channel_id,
        - message,
        - time_sent

    Exceptions:
        InputError - invalid channel_id
        InputError - length of message is over 1000 characters
        InputError - time_sent is in the past
        AccessError - valid channel_id but user is not a member
    
    Return value:
        { message_id }
    '''

    decode = check_valid_token(token)
    # ERROR VALIDATIONS 

    # Check if channel id is valid
    check_valid_channel(channel_id)

    # Check if message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description = 'Message character count over 1000')

    # Check if time_sent is in the past
    if int(time_sent) < int(datetime.now().timestamp()):
        raise InputError(description = 'Scheduled time cannot be in the past')

    # Check if user has access to the channel
    check_channel_access(decode, channel_id)

    # FUNCTION IMPLEMENTATION

    wait = time_sent - datetime.now().timestamp()
    sleep(wait)

    message_id = message_send_v1(token, channel_id, message)

    return {
        'message_id': message_id
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Given a user's token, dm_id, message, and time, sends message at specified time

    Arguments:
        - token,
        - dm_id,
        - message,
        - time_sent

    Exceptions:
        InputError - invalid dm_id
        InputError - length of message is over 1000 characters
        InputError - time_sent is in the past
        AccessError - valid dm_id but user is not a member
    
    Return value:
        { message_id }
    '''

    decode = check_valid_token(token)
    # ERROR VALIDATIONS

    # Check if channel id is valid
    check_valid_dm(dm_id)

    # Check if message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description = 'Message character count over 1000')

    # Check if time_sent is in the past
    if int(time_sent) < int(datetime.now().timestamp()):
        raise InputError(description = 'Scheduled time cannot be in the past')

    # Check if user has access to the channel
    check_dm_access(decode, dm_id)

    # FUNCTION IMPLEMENTATION

    wait = time_sent - datetime.now().timestamp()
    sleep(wait)

    message_id = message_senddm_v1(token, dm_id, message)

    return {
        'message_id': message_id
    }

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Given a user's token, dm_id, message, and time, sends message at specified time

    Arguments:
        - token,
        - og_message_id,
        - message,
        - channel_id,
        - dm_id

    Exceptions:
        InputError - both channel_id and dm_id are invalid
        InputError - neither channel_id nor dm_id are -1
        InputError - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        InputError - length of message is more than 1000 characters
        AccessError - channel_id and dm_id are valid and the authorised user is not a member of channel/DM message is being shared to
    
    Return value:
        { shared_message_id }
    '''
    store = data_store.get()
    decode = check_valid_token(token)
    
    # ERROR VALIDATIONS 
    # Check if token is valid
    #check_valid_token(token)

    # Check if neither ids are valid
    valid_channel = False
    valid_dm = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            valid_dm = True
            break

    if valid_channel == False and valid_dm == False:
        raise InputError(description = 'Both channel_id and dm_id are invalid')

    # Check if neither ids are -1
    if channel_id != -1 and dm_id != -1:
        raise InputError(description = 'Neither channel nor dm IDs are -1')

    # Check if og_message_id is valid, and if so, find the shared message
    message_found = False
    for channel in store['channels']:
        for messages in channel['messages']:
            if og_message_id == messages['message_id']:
                shared_message = messages['message']
                message_found = True
                break
    
    if message_found == False:
        for dms in store['dms']:
            for messages in dms['messages']:
                if og_message_id == messages['message_id']:
                    shared_message = messages['message']
                    message_found = True
                    break

    if message_found == False:
        raise InputError(description = 'Invalid og_message_id in channel/DM')
    
    # Check if message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description = 'Message character count over 1000')

    # Check if authorised user is not a member of channel/dm sharing the message to
    if dm_id == -1:
        check_channel_access(decode, channel_id)

    if channel_id == -1:
        check_dm_access(decode, dm_id)

    # Concatenate two messages
    if len(message) > 0:
        final_message = shared_message + " " + message
    else:
        final_message = shared_message

    # Share to channel
    if dm_id == -1:
        message_id = message_send_v1(token, channel_id, final_message)
    # Share to DM
    elif channel_id == -1:
        message_id = message_senddm_v1(token, dm_id, final_message)

    return {
        'message_id': message_id
        }
 

# Helper functions to check validations ================================================================

def check_valid_channel(channel_id):
    # Check if channel ID is valid
    store = data_store.get()
    valid_channel = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break
    if valid_channel == False:
        raise InputError(description = "Channel id does not exist")
    return valid_channel

def check_valid_dm(dm_id):
    # Check if channel ID is valid
    store = data_store.get()
    valid_dm = False
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            valid_dm = True
            break
    if valid_dm == False:
        raise InputError(description = "DM id does not exist")
    return valid_dm

def check_channel_access(decode, channel_id):
    # Check if user has access to the channel
    store = data_store.get()
    user_access = False
    for channel in store['channels']:
        for member in channel['all_members']:
            if member['u_id'] == decode['u_id']:
                user_access = True
                break
    if user_access == False and check_valid_channel(channel_id) == True:
            raise AccessError(description = "User does not have access to the channel")

def check_dm_access(decode, dm_id):
    # Check if user has access to the channel
    store = data_store.get()
    user_access = False
    for dm in store['dms']:
        for member in dm['members']:
            if member['u_id'] == decode['u_id']:
                user_access = True
                break
    if user_access == False and check_valid_dm(dm_id) == True:
            raise AccessError(description = "User does not have access to the dm")

def check_messageid_valid(u_id, message_id):
    store = data_store.get()
    message_valid = False
    in_channel = False
    in_dm = False
    for channel in store['channels']:
        for member in channel['all_members']:
            if u_id == member['u_id']:
                for message in channel['messages']:
                    if message_id == message['message_id']:
                        message_valid = True
                        in_channel = True
    
    for dm in store['dms']:
        for member in dm['members']:
            if u_id == member['u_id']:
                for message in dm['messages']:
                    if message_id == message['message_id']:
                        message_valid = True
                        in_dm = True
    
    if message_valid == False:
        raise InputError(description = 'Invalid message_id in channel/DM')
        
    return (in_channel, in_dm)

def check_user_is_owner(u_id, in_channel, in_dm):
    store = data_store.get()
    user_is_owner = False
    if in_channel:
        for channel in store['channels']:
            for owner in channel['owner_members']:
                if u_id == owner['u_id']:
                    user_is_owner = True
    if in_dm:
        for dm in store['dms']:
            if u_id == dm['owner']['u_id']:
                user_is_owner = True
    
    return user_is_owner
    
def check_user_own_message(u_id, message_id, in_channel, in_dm):
    store = data_store.get()
    user_own_message = False
    if in_channel:
        for channel in store['channels']:
            for message in channel['messages']:
                if u_id == message['u_id'] and message_id == message['message_id']:
                    user_own_message = True
    if in_dm:
        for dm in store['dms']:
            for message in dm['messages']:
                if u_id == message['u_id'] and message_id == message['message_id']:
                    user_own_message = True
                    
    return user_own_message
