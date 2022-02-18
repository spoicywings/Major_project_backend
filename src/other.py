from src.data_store import data_store
from src.error import AccessError, InputError

import hashlib
import jwt
import json
SESSION_ID_TRACKER = 0
SECRET = 'F13BCAMEL'

def clear_v1():
    store = data_store.get()
    
    store['users'].clear()
    store['channels'].clear()
    store['dms'].clear()
    store['stats'].clear()
    store['codes'].clear()
    
    data_store.set(store)

    return {
    }

def check_global_owner(token):
    data = data_store.get()
    decode = decode_jwt(token)
    
    global_owner = False
    for user in data['users']:
        if user['u_id'] == decode['u_id']:
            if user['global_owner'] == True:
                global_owner = True
            else:
                global_owner = False
     
    return global_owner           
            
def check_is_member(u_id, channel_id):
    data = data_store.get()
    
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            break
    
    is_member = False
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            is_member = True
                
    return is_member   

def check_is_member_token(token, channel_id):
    data = data_store.get()
    decode = decode_jwt(token)
    
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            break
    
    is_member = False
    for member in channel['all_members']:
        if member['u_id'] == decode['u_id']:
            is_member = True
                
    return is_member        
    

def check_valid_token(token):
    
    if type(token) != str:
        raise AccessError("Invalid User Token") 
    
    data = data_store.get()
    decode = decode_jwt(token)
    
    valid_user = False
    for user in data['users']:
        for sess_id in user['session_id']:
            if decode['u_id'] == user['u_id'] and decode['session_id'] == sess_id:
                valid_user = True
                break
    
    if valid_user == False:
        raise AccessError("Invalid User Token")
    
    return decode

def check_valid_id(u_id):
    data = data_store.get()
    valid_user = False
    for user in data['users']:
        if u_id == user['u_id']:
            valid_user = True
            
    return valid_user

def check_valid_channel_id(channel_id):
    data = data_store.get()
    valid_channel = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
    return valid_channel    

def check_get_channel(channel_id): 
    data = data_store.get()
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            break
            
    return channel
        
def hashing(string):
    # Hashes the input string with sha256, used to encrypt password
    return hashlib.sha256(string.encode()).hexdigest()
    
def generate_session_id():
    global SESSION_ID_TRACKER
    SESSION_ID_TRACKER += 1
    return SESSION_ID_TRACKER
    
def create_jwt(u_id, session_id):
    # Generate a JWT 
    return jwt.encode({'u_id': u_id, 'session_id': session_id}, SECRET, algorithm='HS256')

def decode_jwt(encoded_jwt):
    # Decode a given JWT
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])

def generate_message_id():
    store = data_store.get()

    message_id = 1
    
    for channel in store['channels']:
        message_id += len(channel['messages'])
        
    for dm in store['dms']:
        message_id += len(dm['messages'])
    
    return message_id

def search_message(message_id):
    # Finds a message given an message_id
    # Returns the message , index of the dm or channel in channel_list
    # or dm_list and whether it is a channel or dm
    # 0 = channel, 1 = dm
    
    store = data_store.get()
    index = 0
    for channel in store['channels']:
        index += 1
        m_index = 0
        for message in channel['messages']:
            m_index += 1
            if message_id == message['message_id']:
                return True, index, 0, m_index           
    index = 0      
    for dm in store['dms']:
        index += 1
        m_index = 0
        for message in dm['messages']:
            m_index += 1
            if message_id == message['message_id']:
                return True, index, 1, m_index
    # Returns false if there exist no message with id
    return False, 0, 0, 0      
    
def reaction_current_user(user_id):
    # When user signs in or registers update what the react button would
    # look like for them ie unlit when they havent react yet or lit when they
    # have
    store = data_store.get()
    for channel in store['channels']:
        for message in channel['messages']:
                if user_id in message['reacts'][0]['u_ids']:
                    message['reacts'][0]['is_this_user_reacted'] = True
                else:
                    message['reacts'][0]['is_this_user_reacted'] = False
    for dm in store['dms']:
        for message in dm['messages']:
                if user_id in message['reacts'][0]['u_ids']:
                    message['reacts'][0]['is_this_user_reacted'] = True
                else:
                    message['reacts'][0]['is_this_user_reacted'] = False
    data_store.set(store)
    
    return True
