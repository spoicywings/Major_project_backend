from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token
from src.stats import increase_num_channels_joined, increase_channels_exist

def channels_list_v1(token):
    '''
    Returns a dictionary containing a list of channels that the user is part of
    
    Arguments:
        - token (string)
        
    Exceptions:
        InputError - invalid token 
        
    Return value:
        {
            'channels': []
        }
    
    '''
    data = data_store.get()
    
    decode = check_valid_token(token)
    user_channels = []
    for channel in data['channels']:
        # If the user is in that channel, then create a dictionary
        # with data channel_id and name and append it to the list
        for member in channel['all_members']:
            channel_info = {}
            if decode['u_id'] == member['u_id']:
                channel_info['channel_id'] = channel['channel_id']
                channel_info['name'] = channel['name']
                user_channels.append(channel_info)
            
    return {    
            'channels' : user_channels
    }
    


def channels_listall_v1(token):
    '''
    Returns a dictionary containing a list of channels that the user is part of
    
    Arguments:
        - token (string)
        
    Exceptions:
        InputError - invalid token 
        
    Return value:
        {
            'channels': []
        }
    
    '''
    
    data = data_store.get()
        
    check_valid_token(token)
    all_channel_list = []
    
    for channels in data['channels']:
        channel_info = {}
        channel_info['channel_id'] = channels['channel_id']
        channel_info['name'] = channels['name']
        all_channel_list.append(channel_info)
        
    return {
        'channels': all_channel_list
    }
    

def channels_create_v1(token, name, is_public):
    
    decode = check_valid_token(token)
    store = data_store.get()
    
    channel_dict = {}
    
    new_id = len(store['channels']) + 1
          
    if len(name) < 1 or len(name) > 20:
        raise InputError("Invalid name, must be between 1 to 20 characters")
        
    # Fetches the data of the user making the channel
    for user in store['users']:
        if user['u_id'] == decode['u_id']:
            user_details = user
            
        
    channel_dict['channel_id'] = new_id    
    channel_dict['is_public'] = is_public
    channel_dict['owner_members'] = [user_details]
    channel_dict['name'] = name
    channel_dict['all_members'] = [user_details]
    channel_dict['messages'] = []
    channel_dict['standup'] = {}
    
    store['channels'].append(channel_dict)
    data_store.set(store)
    
    increase_num_channels_joined(decode['u_id'])
    
    # Increase the number of channels that exist in workplace stats
    increase_channels_exist()
    
    return {
        'channel_id': new_id,
    }   
