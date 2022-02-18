from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages

    Arguments:
        - token (string)
        - query_str (string)

    Exceptions:
        InputError - when length of query_str is less than 1 or over 1000 characters
        AccessError - when token is invalid

    Return value:
        { messages }
    '''
    
    store = data_store.get()
    messages = []
    
    # If token is invalid, AccessError is raised
    # else the payload is returned
    decoded_token = check_valid_token(token)

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description="Length of query_str is less than 1 or over 1000 characters")
    
    # Find all the dms that user is in
    for dm in store['dms']:
        for member in dm['members']:
            if decoded_token['u_id'] == member['u_id']:
                # When user is in the dm find all the messages associated with user
                for message in dm['messages']:
                    # Find if the query_str is in the message
                    # If query_str is not in the message -1 is returned
                    if message['message'].find(query_str) != -1:
                        messages.insert(0, message)
                break
    
    # Find all the channels that user is in
    for channel in store['channels']:
        for member in channel['all_members']:
            if decoded_token['u_id'] == member['u_id']:
                # When user is in the channel find all the messages associated with user
                for message in channel['messages']:
                    # Find if the query_str is in the message
                    # If query_str is not in the message -1 is returned
                    if message['message'].find(query_str) != -1:
                        messages.insert(0, message)
                break

    return {
        'messages': messages
    }
