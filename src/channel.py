from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token
from src.stats import increase_num_channels_joined, decrease_num_channels_joined
from src.other import hashing, generate_session_id, create_jwt, decode_jwt, check_global_owner 
from src.other import check_is_member, check_is_member_token, check_valid_id, check_valid_channel_id, check_get_channel
from src.notifications import update_notification_added_channel

import hashlib
import jwt
import re


def channel_invite_v1(token, channel_id, u_id):
    '''
    Given a user's token, valid channel id and valid user_id, invites user with user_id to the channel

    Arguments:
        - token,
        - channel_id,
        - u_id

    Exceptions:
        InputError - channel_id is invalid
        InputError - u_id is invalid
        InputError - user with u_id is already a member of channel
        AccessError - channel_id is valid but authorised user is not a member

    Return value:
        { }
    '''

    # Check if user exists
    check_valid_token(token)
    get_channel = data_store.get()
    decode = decode_jwt(token)

    valid_user = False
    for user in get_channel['users']:
        if u_id == user['u_id']:
            valid_user = True
            break    
    if valid_user == False:
        raise InputError("Invalid User Id")
    
    # Check if channel ID is valid
    valid_channel = False
    for channel in get_channel['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break
    if valid_channel == False:
        raise InputError(description = "Channel id does not exist")

    # Check if user is already in the channel
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            raise InputError(description = "User already a member of channel")

    # Check if user has access to the channel
    user_access = False
    for channel in get_channel['channels']:
        for member in channel['all_members']:
            if member['u_id'] == decode['u_id']:
                user_access = True
                break
    if user_access == False and valid_channel == True:
            raise AccessError(description = "User does not have access to the channel")

    # getting the user details (newly added)
    for user in get_channel['users']:
        if user['u_id'] == u_id:
            user_details = user 

    # Adding user to channel
    get_channel['channels'][channel_id - 1]['all_members'].append(user_details)
    data_store.set(get_channel)
    
    increase_num_channels_joined(u_id)
    
    # Add notification to user
    update_notification_added_channel(decode['u_id'], u_id, channel_id)
    
    return {}


def channel_details_v1(token, channel_id):
    '''
    Returns a dictionary containing info about a given channel_id
    
    Arguments:
        - token (string)
        - chann_id (integer)
        
    Exceptions:
        InputError - invalid token or channel_id is invalid
        AccessError - User is not part of that channel
        
    Return value:
        {
            'name' : ,
            'is_public' : ,
            'owner_member': ,
            'all_members': ,
        }
    
    '''
    get_channel = data_store.get()
    decode = check_valid_token(token)

    # Check if valid channel_id exists
    valid_channel = False
    for channel in get_channel['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True
            break

    if valid_channel == False:
        raise InputError(description="Channel id does not exist")
        
    # Gets the details of the channel
    channel_data = {}
    for channel in get_channel['channels']:
        if channel_id == channel['channel_id']:
            channel_data = channel
            
    # Check if user is part of that channel
    valid_user = False
    
    for users in channel['all_members']:
        if users['u_id'] == decode['u_id']:
            valid_user = True

    if valid_user == False:
        raise AccessError(description="User not authorised access to channel")

    # Searches for the channel and return its details
    return {
            'name': channel_data['name'],
            'is_public': channel_data['is_public'],
            'owner_members': channel_data['owner_members'],
            'all_members' : channel_data['all_members'],
    }


def channel_messages_v1(token, channel_id, start):
    '''
    Given a user's token, valid channel id and start, returns a list of up to 50 messages

    Arguments:
        - token,
        - channel_id,
        - start

    Exceptions:
        InputError - channel_id is invalid
        InputError - start > number of messages in channel
        AccessError - channel_id is valid but authorised user is not a member

    Return value:
        { messages, start, end}
    '''

    store = data_store.get()
    decode = check_valid_token(token)

    # Check if channel ID is valid
    valid_channel = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break
            
    if valid_channel == False:
        raise InputError(description = "Channel id does not exist")

    # Check if user has access to the channel
    user_access = False
    for member in channel['all_members']:
        if member['u_id'] == decode['u_id']:
            user_access = True
            break
            
    if user_access == False and valid_channel == True:
            raise AccessError(description = "User does not have access to the channel")

    # Check if number of messages is valid      
    if start > len(channel['messages']):
        raise InputError(description = "Start is greater than total number of messages in channel")

    # Function implementation
    messages = []
    end = 0
    
    for message in channel['messages']:
        if end < start:
            end += 1
        elif end == start + 50: 
            break
        else:
            messages.append(message)
            end += 1
    
    if end == len(channel['messages']):
        end = -1
    
    return {
        'messages': messages,
        'start': start,
        'end': end
    }


def channel_join_v1(token, channel_id):
    
    # Check if user exists
    decode = check_valid_token(token)
   
    get_channel = data_store.get()
      
    # Check if valid channel_id exists
    valid_channel = False
    for channel in get_channel['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break

    if valid_channel == False:
        raise InputError(description="Channel id does not exist")
      
    # Check if user is part of that channel
    for member in channel['all_members']:
        if member['u_id'] == decode['u_id']:
            raise InputError(description="User already a member of channel")
                    
    # Get user details
    for user in get_channel['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user    
                    
    
    if channel['is_public'] == False and user_details['global_owner'] == False:
        raise AccessError(description="Channel is private")

    get_channel['channels'][channel_id - 1]['all_members'].append(user_details)
    data_store.set(get_channel)
       
    increase_num_channels_joined(decode['u_id'])    
   
    return {
    }

def channel_leave_v1(token, channel_id):
    
    # Check if user exists
    decode = check_valid_token(token)
       
    get_channel = data_store.get()
    
    # Check if valid channel_id exists
    valid_channel = False
    for channel in get_channel['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            break

    if valid_channel == False:
        raise InputError(description="Channel id does not exist") 
  
      
    # Check if user is part of that channel
    is_member = False
    for member in channel['all_members']:
        if member['u_id'] == decode['u_id']:
            is_member = True
            break
            
    if is_member == False:        
        raise AccessError(description="User is not a member of the channel")
    
    owner_member = False
    
    # Check if user is a owner
    owner_member = False
    for member in channel['owner_members']:
        if member['u_id'] == decode['u_id']:
            owner_member = True
    
    # Get user details
    for user in get_channel['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user  
    
    if owner_member == True:
        get_channel['channels'][channel_id - 1]['owner_members'].remove(user_details)
    
    get_channel['channels'][channel_id - 1]['all_members'].remove(user_details)
    
    data_store.set(get_channel)
    
    decrease_num_channels_joined(decode['u_id'])
    
    return {    
    }

def channel_addowner_v1(token, channel_id, u_id):
    get_channel = data_store.get()
    
    # check valid token
    decode = check_valid_token(token)
    
    # check_valid_uid
    valid_user = check_valid_id(u_id)    
    if valid_user == False:
        raise InputError(description="Invalid User Id")   
    
    # Check if valid channel_id exists
    valid_channel = check_valid_channel_id(channel_id)
    if valid_channel == False:
        raise InputError(description="Channel id does not exist") 
        
    # Check if u_id is part of that channel
    is_member = check_is_member(u_id, channel_id)            
    if is_member == False:        
        raise InputError(description="User is not a member of the channel")
        
    # Check if token is part of channel
    is_member = check_is_member_token(token, channel_id)
    if is_member == False:        
        raise AccessError(description="User does not have owner permissions")
    
    # Check if u_id is already an owner
    owner_member = False
    channel = check_get_channel(channel_id)
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            owner_member = True  
            
    if owner_member == True:        
        raise InputError(description="User is already a owner")       
                   
    # Check if token has owner permissions
    owner_member = check_global_owner(token)
    for member in channel['owner_members']:
        if member['u_id'] == decode['u_id']:
            owner_member = True
    
    if owner_member == False:
        raise AccessError(description="User does not have owner permissions")
    
    # add u_id as owner   
    for user in get_channel['users']:
        if user['u_id'] == u_id:
            user_details = user
             
     
    get_channel['channels'][channel_id - 1]['owner_members'].append(user_details)  
    
    return {
    }
    
def channel_removeowner_v1(token, channel_id, u_id):
    get_channel = data_store.get()
    
    # check valid token
    decode = check_valid_token(token)
    
    # check_valid_uid
    valid_user = check_valid_id(u_id)    
    if valid_user == False:
        raise InputError(description="Invalid User Id")   
    
    # Check if valid channel_id exists
    valid_channel = check_valid_channel_id(channel_id)
    if valid_channel == False:
        raise InputError(description="Channel id does not exist") 
        
    # Check if u_id is part of that channel
    is_member = check_is_member(u_id, channel_id)            
    if is_member == False:        
        raise InputError(description="User is not a member of the channel")
        
    # Check if token is part of channel
    is_member = check_is_member_token(token, channel_id)
    if is_member == False:        
        raise AccessError(description="User does not have owner permissions")
    
    # Check if channel only has one owner
    channel = check_get_channel(channel_id)    
    if len(channel['owner_members']) == 1:
        raise InputError(description="User is currently only owner")  
        
    # Check if token has owner permissions
    owner_member = check_global_owner(token)
    for member in channel['owner_members']:
        if member['u_id'] == decode['u_id']:
            owner_member = True
    
    if owner_member == False:
        raise AccessError(description="User does not have owner permissions")
    
    # add u_id as owner   
    for user in get_channel['users']:
        if user['u_id'] == u_id:
            user_details = user  
     
    get_channel['channels'][channel_id - 1]['owner_members'].remove(user_details)  
    
    return {
    }      
                
