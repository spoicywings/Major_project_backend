from src.data_store import data_store
from src.other import check_valid_token
from datetime import datetime, timezone

def user_stats_v1(token):
    ''' 
    Fetches the required statistics about this user's use of UNSW Streams
    
    Arguments:
        token (string)
        
    Exceptions:
        N/A
        
    Return value:
        { user_stats }  
    '''

    # Check the token is valid
    user_token_data = check_valid_token(token)
    
    store = data_store.get()
    
    # Get the user stats of the user
    for user in store['users']:
        if user['u_id'] == user_token_data['u_id']:
            user_stats = user['user_stats']
            
    num_channels_joined = user_stats['channels_joined'][-1]['num_channels_joined']
    num_dms_joined = user_stats['dms_joined'][-1]['num_dms_joined']
    num_msgs_sent = user_stats['messages_sent'][-1]['num_messages_sent']
    
    # Store the new involvement rate
    user_stats['involvement_rate'] = update_involvement_rate(num_channels_joined, num_dms_joined, num_msgs_sent)
    
    # Return user stats
    return {
        'user_stats': user_stats
    }

def users_stats_v1(token):
    '''
    Fetches the required statistics about the use of UNSW Streams.
    
    Arguments:
        token (string)
    
    Exceptions:
        N/A
        
    Return value:
        { workplace_stats }
    '''
    
    # Check the token is valid
    check_valid_token(token)
    
    store = data_store.get()
    
    # Get the current workplace_stats
    workspace_stats = store['stats'][0]
    workspace_stats['utilization_rate'] = update_utilization_rate()
    
    # Return workplace_stats
    return {
        'workspace_stats': workspace_stats
    }
    
############################ STATS HELPER FUNCTIONS ############################
# Count the total number of channels
def count_num_channels():
    store = data_store.get()
    
    return len(store['channels'])

# Count the total number of dms
def count_num_dms():
    store = data_store.get()

    return len(store['dms'])
    
# Count the total number of msgs
def count_num_msgs():
    store = data_store.get()

    counter = 0
    for channel in store['channels']:
        counter += len(channel['messages'])
  
    for dm in store['dms']:
	    counter += len(dm['messages'])

    return counter

# Get the current timestamp
def get_timestamp():
    timestamp = int(datetime.now(timezone.utc).timestamp())
   
    return timestamp

# Update the involvement rate for user_stats
def update_involvement_rate(num_channels_joined, num_dms_joined, num_msgs_sent):
    # Count the number of channels, dms and messages
    num_channels = count_num_channels()
    num_dms = count_num_dms()
    num_msgs = count_num_msgs()
    
    # Calculate numerator
    numerator = num_channels_joined + num_dms_joined + num_msgs_sent
    
    # Calculate denominator
    denominator = num_channels + num_dms + num_msgs
    
    # If the denominator is 0, the involvement rate is 0
    if denominator == 0:
        rate = 0
    else:
        # Calculate the involvement rate, if the involvement rate is > 1, cap it at 1
        rate = numerator/denominator
        if rate > 1:
	        rate = 1

    return rate

# Update the utilization rate for workplace_stats
def update_utilization_rate():
    store = data_store.get()
    
    # Get total number of users
    num_users_counter = 0
    for user in store['users']:
        if user['name_first'] != 'Removed' and user['name_last'] != 'user':
            num_users_counter += 1
    
    counter = 0
    
    # Get num users who have joined at least one channel or dm
    for user in store['users']:
        u_id = user['u_id']
        user_has_joined_channel = False
        for channel in store['channels']:
            for member in channel['all_members']:
                if u_id == member['u_id'] and user_has_joined_channel == False:
                    user_has_joined_channel = True
                    counter += 1
                
        # If they haven't joined a channel, check if they have joined a dm
        user_has_joined_dm = False
        if user_has_joined_channel == False:
            for dm in store['dms']:
                for dm_member in dm['members']:
                    if u_id == dm_member['u_id'] and user_has_joined_dm == False:
                        user_has_joined_dm = True
                        counter += 1
    
    rate = counter / num_users_counter
    
    return rate        
        
################## Increment num_channels_joined in user stat ##################
# (when channel/create, channel/invite, channel/join is called)
def increase_num_channels_joined(u_id):
    store = data_store.get()
    
    # Find the number of channels the user has already joined
    for user in store['users']:
        if u_id == user['u_id']:
            num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined']
    
    # Increment num_channels_joined
    num_channels_joined += 1

    timestamp = get_timestamp() 
    
    # Make a new user stats dictionary for channels joined
    user_stats = {'num_channels_joined': num_channels_joined, 'time_stamp': timestamp}

    # Append the new user_stats to the list of channels joined
    for user in store['users']:
        if u_id == user['u_id']:
            user['user_stats']['channels_joined'].append(user_stats)
    
    data_store.set(store)

    return {
    }   

#################### Increment num_dms_joined in user stat #####################
# (when dm/create is called)
def increase_num_dms_joined(u_id):  
    store = data_store.get() 
    
    # Find the number of dms the user has already joined
    for user in store['users']:
        if u_id == user['u_id']:
            num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            
    # Increment num_dms_joined
    num_dms_joined += 1
    
    timestamp = get_timestamp()
    
    # Make a new user stats dictionary for dms joined
    user_stats = {'num_dms_joined': num_dms_joined, 'time_stamp': timestamp}
    
    # Append the new user_stats to the list of channels joined
    for user in store['users']:
        if u_id == user['u_id']:   
            user['user_stats']['dms_joined'].append(user_stats)
    
    data_store.set(store)

    return {
    }  

##################### Increment num_msgs_sent in user stat #####################
# (when message/send, message/senddm, message/sendlater, message/share is called)
def increase_num_msgs_sent(u_id): 
    store = data_store.get() 
    
    # Find the number of messages the user has sent
    for user in store['users']:
        if u_id == user['u_id']:
            num_msgs_sent = user['user_stats']['messages_sent'][-1]['num_messages_sent']
    
    # Increment num_msgs_sent
    num_msgs_sent += 1
    
    timestamp = get_timestamp()
    
    # Make a new user stats dictionary for messages sent
    user_stats = {'num_messages_sent': num_msgs_sent, 'time_stamp': timestamp}
    
    # Append the new user_stats to the list of messages sent
    for user in store['users']:
        if u_id == user['u_id']:
            user['user_stats']['messages_sent'].append(user_stats)
    
    data_store.set(store)

    return {
    }  

################## Decrease num_channels_joined in user stat ###################
# (when channel/leave is called)
def decrease_num_channels_joined(u_id):
    store = data_store.get()
    
    # Find the number of channels the user has already joined
    for user in store['users']:
        if u_id == user['u_id']:
            num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined']
    
    # Decrease num_channels_joined
    num_channels_joined -= 1

    timestamp = get_timestamp()
    
    # Make a new user stats dictionary for channels joined
    user_stats = {'num_channels_joined': num_channels_joined, 'time_stamp': timestamp}

    # Append the new user_stats to the list of channels joined
    for user in store['users']:
        if u_id == user['u_id']:
            user['user_stats']['channels_joined'].append(user_stats)
    
    data_store.set(store)

    return {
    }   

################### Decrease num_dms_joined in user stat #######################
# (when dm/leave or dm/remove is called)
def decrease_num_dms_joined(u_id):
    store = data_store.get()
    
    # Find the number of dms the user has already joined
    for user in store['users']:
        if u_id == user['u_id']:
            num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            
    # Decrease num_dms_joined
    num_dms_joined -= 1
    
    timestamp = get_timestamp()
    
    # Make a new user stats dictionary for dms joined
    user_stats = {'num_dms_joined': num_dms_joined, 'time_stamp': timestamp}
    
    # Append the new user_stats to the list of channels joined
    for user in store['users']:
        if u_id == user['u_id']:   
            user['user_stats']['dms_joined'].append(user_stats)

    data_store.set(store)

    return {
    } 

####################### users/stats/v1 HELPER FUNCTIONS ########################
# Increase the number of channels that exist in workplace_stats
# (when channels/create is called)
def increase_channels_exist():
    store = data_store.get()
    
    # Find the previous number of channels that exist, then increment it
    num_channels_exist = store['stats'][0]['channels_exist'][-1]['num_channels_exist']
    num_channels_exist += 1
    
    timestamp = get_timestamp()
    
    # Create new dictionary with new stats
    new_stats = {'num_channels_exist': num_channels_exist, 'time_stamp': timestamp}
    store['stats'][0]['channels_exist'].append(new_stats)
    
    data_store.set(store)
    
    return {
    }
        
# Increase the number of dms that exist in workplace stats
# (when dm/create is called)
def increase_dms_exist(): 
    store = data_store.get()
    
    # Find the previous number of dms that exist, then increment it
    num_dms_exist = store['stats'][0]['dms_exist'][-1]['num_dms_exist']
    num_dms_exist += 1 
    
    timestamp = get_timestamp()
    
    # Create new dictionary with new stats
    new_stats = {'num_dms_exist': num_dms_exist, 'time_stamp': timestamp}
    store['stats'][0]['dms_exist'].append(new_stats)
    
    data_store.set(store)
    
    return {
    }

# Decrease the number of dms that exist in workplace stats
# (when dm/remove is called)
def decrease_dms_exist():
    store = data_store.get()
    
    # Find the previous number of dms that exist, then decrease it
    num_dms_exist = store['stats'][0]['dms_exist'][-1]['num_dms_exist']
    num_dms_exist -= 1 
    
    timestamp = get_timestamp()
    
    # Create new dictionary with new stats
    new_stats = {'num_dms_exist': num_dms_exist, 'time_stamp': timestamp}
    store['stats'][0]['dms_exist'].append(new_stats)
    
    data_store.set(store)
    
    return {
    }

# Increase the number of msgs that exist in workplace stats
# (when message/send, message/senddm, message/sendlater, message/share is called)
def increase_msgs_exist():  
    store = data_store.get()
    
    # Find the previous number of msg that exist, then increment it
    num_msgs_exist = store['stats'][0]['messages_exist'][-1]['num_messages_exist']
    num_msgs_exist += 1     
    
    timestamp = get_timestamp()
    
    # Create new dictionary with new stats
    new_stats = {'num_messages_exist': num_msgs_exist, 'time_stamp': timestamp}
    store['stats'][0]['messages_exist'].append(new_stats)
    
    data_store.set(store)
    
    return {
    }

# Decrease the number of msgs that exist in workplace stats
# (when message/remove or dm/remove are called)
def decrease_msgs_exist(num_msgs_removed):
    store = data_store.get()
    
    # Find the previous number of msg that exist, then increment it
    num_msgs_exist = store['stats'][0]['messages_exist'][-1]['num_messages_exist']
    num_msgs_exist -= num_msgs_removed     
    
    timestamp = get_timestamp()
    
    # Create new dictionary with new stats
    new_stats = {'num_messages_exist': num_msgs_exist, 'time_stamp': timestamp}
    store['stats'][0]['messages_exist'].append(new_stats)
    
    data_store.set(store)
    
    return {
    }
