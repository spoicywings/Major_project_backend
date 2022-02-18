import pytest
import requests

from src import config
from src.error import InputError

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

# test that function works properly
def test_messages_working(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    assert channel_messages.json() == {'end': -1, 'messages': [], 'start': 0}

def test_working_with_message(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })
    response = channel_messages.json()

    assert response['messages'][0]['message'] == 'hello'

# if channel_id does not refer to a valid channel
def test_invalid_channel_id(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': -1,
        'start': 0
    })

    assert channel_messages.status_code == InputError.code

# if start is > total number of messages in channel
def test_start_bigger_messages(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 9999999999999
    })

    assert channel_messages.status_code == InputError.code

# if channel_id is valid but auth_user is not a member
def test_nonmember_user(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password2',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user_2_data = user_2_reg.json()

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_2_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    assert channel_messages.status_code == AccessError.code
    
def test_end_more_fifty_messages(clear_data):
    user1_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password2',
        'name_first' : 'John', 'name_last' : 'Smith',
    }).json()
    
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'],
        'name': 'General',
        'is_public': True
    }).json()
    
    i = 0
    while i < 51:
        requests.post(BASE_URL + 'message/send/v1', json = {
            'token': user1_data['token'],
            'channel_id': channel_data['channel_id'],
            'message': 'hello'
        })
        i += 1
        
    response_data = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user1_data['token'],
        'channel_id': channel_data['channel_id'],
        'start': 0
    }).json()
    
    assert response_data['end'] == 50
    
def test_end_fifty_messages(clear_data):
    user1_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password2',
        'name_first' : 'John', 'name_last' : 'Smith',
    }).json()
    
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'],
        'name': 'General',
        'is_public': True
    }).json()
    
    i = 0
    while i < 50:
        requests.post(BASE_URL + 'message/send/v1', json = {
            'token': user1_data['token'],
            'channel_id': channel_data['channel_id'],
            'message': 'hello'
        })
        i += 1
        
    response_data = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user1_data['token'],
        'channel_id': channel_data['channel_id'],
        'start': 0
    }).json()
    
    assert response_data['end'] == -1
    
def test_start_not_zero(clear_data):
    user1_data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password2',
        'name_first' : 'John', 'name_last' : 'Smith',
    }).json()
    
    channel_data = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'],
        'name': 'General',
        'is_public': True
    }).json()
    
    i = 0
    while i < 60:
        requests.post(BASE_URL + 'message/send/v1', json = {
            'token': user1_data['token'],
            'channel_id': channel_data['channel_id'],
            'message': 'hello'
        })
        i += 1
        
    response_data = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user1_data['token'],
        'channel_id': channel_data['channel_id'],
        'start': 4
    }).json()
    
    assert response_data['end'] == 54
        
    
