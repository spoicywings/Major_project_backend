from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token

def notifications_get_v1(token):
    '''
    Return the user's most recent 20 notifications, ordered from most recent to least recent

    Arguments:
        - token

    Exceptions:
        AccessError - when token is invalid

    Return value:
        { notifications }
    '''
    
    store = data_store.get()
    
    decode = check_valid_token(token)
    notifications = []
    
    for user in store['users']:
        if decode['u_id'] == user['u_id']:
            notifications = user['notifications'][:20]
    
    return {
        'notifications': notifications
    }
    
def find_user_handle(u_id):
    store = data_store.get()
    
    for user in store['users']:
        if u_id == user['u_id']:
            user_handle = user['handle_str']
    
    return user_handle

def update_notification_added_channel(sender_id, receiver_id, channel_id):
    store = data_store.get()
    notification_dict = {}
    sender_handle = find_user_handle(sender_id)
    
    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            break
    
    for user in store['users']:
        if receiver_id == user['u_id']:
            notification_dict['channel_id'] = channel_id
            notification_dict['dm_id'] = -1
            notification_dict['notification_message'] = f"{sender_handle} added you to {channel['name']}"
            user['notifications'].insert(0, notification_dict)

def update_notification_added_dm(sender_id, receiver_id, dm_id):
    store = data_store.get()
    notification_dict = {}
    sender_handle = find_user_handle(sender_id)
    
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            break
    
    for user in store['users']:
        if receiver_id == user['u_id']:
            notification_dict['channel_id'] = -1
            notification_dict['dm_id'] = dm_id
            notification_dict['notification_message'] = f"{sender_handle} added you to {dm['name']}"
            user['notifications'].insert(0, notification_dict)

def update_notification_react(sender_id, message_id):
    store = data_store.get()
    notification_dict = {}
    sender_handle = find_user_handle(sender_id)
    
    for channel in store['channels']:
        for message in channel['messages']:
            if message_id == message['message_id']:
                for user in store['users']:
                    if message['u_id'] == user['u_id']:
                        notification_dict['channel_id'] = channel['channel_id']
                        notification_dict['dm_id'] = -1
                        notification_dict['notification_message'] = f"{sender_handle} reacted to your message in {channel['name']}"
                        user['notifications'].insert(0, notification_dict)
    
    for dm in store['dms']:
        for message in dm['messages']:
            if message_id == message['message_id']:
                for user in store['users']:
                    if message['u_id'] == user['u_id']:
                        notification_dict['channel_id'] = -1
                        notification_dict['dm_id'] = dm['dm_id']
                        notification_dict['notification_message'] = f"{sender_handle} reacted to your message in {dm['name']}"
                        user['notifications'].insert(0, notification_dict)

def update_notification_tagged(sender_id, chat_id, message, in_channel, in_dm):
    store = data_store.get()
    notification_dict = {}
    sender_handle = find_user_handle(sender_id)
    
    index = message.find(f"@") + 1
    receiver_handle = ""   
    if index != 0:
        while message[index].isalnum():
            receiver_handle += message[index]
            index += 1
            if index == len(message):
                break
        # When end of the handle is signified by the end of the message
        if index == len(message):
            if in_channel:
                for channel in store['channels']:
                    for member in channel['all_members']:
                        if chat_id == channel['channel_id'] and receiver_handle == member['handle_str']:
                            notification_dict['channel_id'] = chat_id
                            notification_dict['dm_id'] = -1
                            notification_dict['notification_message'] = f"{sender_handle} tagged you in {channel['name']}: {message[:20]}"
                            # Finding who receiver_handle belongs to
                            for user in store['users']:
                                if receiver_handle == user['handle_str']:
                                    user['notifications'].insert(0, notification_dict)
            elif in_dm:
                for dm in store['dms']:
                    for member in dm['members']:
                        if chat_id == dm['dm_id'] and receiver_handle == member['handle_str']:
                            notification_dict['channel_id'] = -1
                            notification_dict['dm_id'] = chat_id
                            notification_dict['notification_message'] = f"{sender_handle} tagged you in {dm['name']}: {message[:20]}"
                            # Finding who receiver_handle belongs to
                            for user in store['users']:
                                if receiver_handle == user['handle_str']:
                                    user['notifications'].insert(0, notification_dict)
        # When end of the handle is signified by a non-alphanumeric character
        elif message[index].isalnum() == False:
            if in_channel:
                for channel in store['channels']:
                    for member in channel['all_members']:
                        if chat_id == channel['channel_id'] and receiver_handle == member['handle_str']:
                            notification_dict['channel_id'] = chat_id
                            notification_dict['dm_id'] = -1
                            notification_dict['notification_message'] = f"{sender_handle} tagged you in {channel['name']}: {message[:20]}"
                            # Finding who receiver_handle belongs to
                            for user in store['users']:
                                if receiver_handle == user['handle_str']:
                                    user['notifications'].insert(0, notification_dict)
            elif in_dm:
                for dm in store['dms']:
                    for member in dm['members']:
                        if chat_id == dm['dm_id'] and receiver_handle == member['handle_str']:
                            notification_dict['channel_id'] = -1
                            notification_dict['dm_id'] = chat_id
                            notification_dict['notification_message'] = f"{sender_handle} tagged you in {dm['name']}: {message[:20]}"
                            # Finding who receiver_handle belongs to
                            for user in store['users']:
                                if receiver_handle == user['handle_str']:
                                    user['notifications'].insert(0, notification_dict)
