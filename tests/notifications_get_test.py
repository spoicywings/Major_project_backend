import pytest
import requests

from src import config
from src.error import InputError, AccessError

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def channel_create_single():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password2',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user2_data = user2.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2_data['token'],
        'channel_id': channel_make_response['channel_id']
    })

    return (user1_data['token'], user2_data['token'], channel_make_response['channel_id'])

def dm_create_single():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password2',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user2_data = user2.json()

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user1_data['token'],
        'u_ids': [user2_data['auth_user_id']]
    })
    dm_make_response = dm_make.json()

    return (user1_data['token'], user2_data['token'], dm_make_response['dm_id'])

# Raises an AccessError when token is invalid
def test_invalid_token(clear_data):
    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'
    })
    
    assert response.status_code == AccessError.code

# Empty list when notification is empty
def test_empty_notification(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': 'hello'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == []

# When someone tags you in a message in channel
def test_tagged_channel(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': '@janeapple hey'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith tagged you in General: @janeapple hey"} ]
    
# When someone tags you in a message in dm
def test_tagged_dm(clear_data):
    user1_token, user2_token, dm_id = dm_create_single()
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user1_token,
        'dm_id': dm_id,
        'message': '@janeapple hey'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'][0] == {'channel_id': -1, 'dm_id': dm_id, 'notification_message': "johnsmith tagged you in janeapple, johnsmith: @janeapple hey"}

# When someone tags you in a message and message is less than 20 characters
def test_tagged_less_than_20(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': '@janeapple hello'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith tagged you in General: @janeapple hello"} ]
    
# When someone tags you in a message and message is longer than 20 characters
def test_tagged_over_20(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': '@janeapple how are you'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith tagged you in General: @janeapple how are y"} ]

# When someone tags you in an editted message
def test_tagged_editted(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': 'hi'
    })

    message_send_response = message_send.json()

    requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user1_token,
        'message_id': message_send_response['message_id'],
        'message': '@janeapple hello'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith tagged you in General: @janeapple hello"} ]

# When tag is the end of message in channel
def test_tagged_end_of_message_channel(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': '@janeapple'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith tagged you in General: @janeapple"} ]

# When tag contains an invalid handle in channel
def test_tagged_invalid_handle_channel(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': '@janeapplehi'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == []

# When tag is the end of message in dm
def test_tagged_end_of_message_dm(clear_data):
    user1_token, user2_token, dm_id = dm_create_single()
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user1_token,
        'dm_id': dm_id,
        'message': '@janeapple'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'][0] == {'channel_id': -1, 'dm_id': dm_id, 'notification_message': "johnsmith tagged you in janeapple, johnsmith: @janeapple"}

# When tag contains an invalid handle in dm
def test_tagged_invalid_handle_dm(clear_data):
    user1_token, user2_token, dm_id = dm_create_single()
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user1_token,
        'dm_id': dm_id,
        'message': '@janeapplehi'
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert len(response_data['notifications']) == 1

# When someone reacts to your message
def test_react(clear_data):
    user1_token, user2_token, channel_id = channel_create_single()
    
    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2_token,
        'channel_id': channel_id,
        'message': 'hi'
    })
    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': user1_token,
        'message_id': message_send_response['message_id'],
        'react_id': 1
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_token
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': channel_id, 'dm_id': -1, 'notification_message': "johnsmith reacted to your message in General"} ]

# When someone adds you to a channel
def test_added_channel(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password2',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user2_data = user2.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()
    
    requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': user2_data['auth_user_id']
    })
    
    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_data['token']
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': 1, 'dm_id': -1, 'notification_message': "johnsmith added you to General"} ]

# When someone adds you to a dm
def test_added_dm(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password2',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user1_data['token'],
        'u_ids': [user2_data['auth_user_id']]
    })

    response = requests.get(BASE_URL + 'notifications/get/v1', params = {
        'token': user2_data['token']
    })
    response_data = response.json()
    
    assert response_data['notifications'] == [ {'channel_id': -1, 'dm_id': 1, 'notification_message': "johnsmith added you to janeapple, johnsmith"} ]
