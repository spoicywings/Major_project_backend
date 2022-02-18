from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token
from src.messages import message_send_v1
from src.stats import increase_num_msgs_sent
from datetime import datetime

import threading
import time

def standup_start_v1(token, channel_id, length):
    '''
    Starts a standup for "length" seconds in a given channel

    Arguments:
        - token,
        - channel_id,
        - length

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError - length is a negative integer
        inputError - an active standup is currently running in the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        AccessError - when token is invalid

    Return value:
        { time_finish }
    '''
    
    store = data_store.get()

    # If token is invalid, AccessError is raised
    # else the payload is returned
    decode = check_valid_token(token)
    
    # Check if valid channel_id exists
    valid_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True
            break
    
    if valid_channel == False:
        raise InputError(description="Channel id does not exist")
    
    # Check if user is part of that channel
    valid_user = False
    
    for users in channel['all_members']:
        if users['u_id'] == decode['u_id']:
            valid_user = True

    if valid_user == False:
        raise AccessError(description="User not authorised access to channel")
    
    # Check if length is a negative number
    if length < 0:
        raise InputError(description="Length is a negative integer")
    
    # Check if an active standup is currently running in the channel
    if channel['standup'] != {}:
        raise InputError(description="An active standup is currently running in the channel")
    
    standup = threading.Timer(length, standup_end_v1, [token, channel, channel_id])
    standup.start()
    
    # Get current datatime, convert to Unix timestamp
    timestamp = int(datetime.now().timestamp() + length)
    
    channel['standup']['time_finish'] = timestamp
    channel['standup']['messages'] = []
    
    data_store.set(store)
    
    return {
        'time_finish': timestamp
    }
    
def standup_end_v1(token, channel, channel_id):
    store = data_store.get()

    standup_msg = channel['standup']['messages']
    buffered_messages(channel, token, channel_id, standup_msg)
    channel['standup'] = {}        
    
    data_store.set(store)

def buffered_messages(channel, token, channel_id, standup_msg):
    store = data_store.get()
    packaged_msg = []
    
    for message in standup_msg:
        for user in store['users']:
            if user['u_id'] == message['u_id']:
                packaged_msg.append(f"{user['handle_str']}: {message['message']}")
   
    packaged_msg = "\n".join(packaged_msg)
    
    if standup_msg == []:
        channel['messages'].insert(0, "\n")
    else:
        message_send_v1(token, channel_id, packaged_msg)
        
def standup_active_v1(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it

    Arguments:
        - token,
        - channel_id

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        AccessError - when token is invalid

    Return value:
        { time_finish }
    '''
    
    store = data_store.get()
    
    # If token is invalid, AccessError is raised
    # else the payload is returned
    decode = check_valid_token(token)
    
    # Check if valid channel_id exists
    valid_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True
            break
    
    if valid_channel == False:
        raise InputError(description="Channel id does not exist")
    
    # Check if user is part of that channel
    valid_user = False
    
    for users in channel['all_members']:
        if users['u_id'] == decode['u_id']:
            valid_user = True

    if valid_user == False:
        raise AccessError(description="User not authorised access to channel")
        
    if channel['standup'] == {}:
        active_status = False
        timestamp = None
    else:
        active_status = True
        timestamp = channel['standup']['time_finish']
    
    return {
        'is_active': active_status,
        'time_finish': timestamp
    }
    
def standup_send_v1(token, channel_id, message):
    '''
    Sending a message to get buffered in the standup queue

    Arguments:
        - token,
        - channel_id,
        - length

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError - length of message is over 1000 characters
        inputError - an active standup is currently running in the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        AccessError - when token is invalid

    Return value:
        { time_finish }
    '''
    
    store = data_store.get()
    standup_messages_dict = {}

    # If token is invalid, AccessError is raised
    # else the payload is returned
    decode = check_valid_token(token)
    
    # Check if valid channel_id exists
    valid_channel = False
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True
            break
    
    if valid_channel == False:
        raise InputError(description="Channel id does not exist")
    
    # Check if user is part of that channel
    valid_user = False
    
    for users in channel['all_members']:
        if users['u_id'] == decode['u_id']:
            valid_user = True
            break

    if valid_user == False:
        raise AccessError(description="User not authorised access to channel")
    
    # Check if message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="Length of message is over 1000 characters")
    
    # Check if an active standup is currently running in the channel
    if channel['standup'] == {}:
        raise InputError(description="An active standup is not currently running in the channel")
    
    standup_messages_dict['u_id'] = decode['u_id']
    standup_messages_dict['message'] = message
    
    channel['standup']['messages'].append(standup_messages_dict)
    
    data_store.set(store)
    
    return {
    }
