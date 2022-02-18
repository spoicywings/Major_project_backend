import pytest
import requests

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError
from datetime import datetime

BASE_URL = config.url

from src.error import InputError, AccessError
SUCCESS = 200

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

# Test that function works properly for sharing to DM
def test_share_to_dm(clear_data):
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

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp())
    })
    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': dm_make_response['dm_id']
    })

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'start': 0
    })

    response_data = response.json()

    assert response_data['messages'][0]['message'] == 'hello'

# Test that function works properly for sharing to DM with additional message
def test_share_to_dm_with_message(clear_data):
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

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()

    requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'first'
        })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp())
    })
    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': 'world',
        'channel_id': -1,
        'dm_id': dm_make_response['dm_id']
    })

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'start': 0
    })

    response_data = response.json()

    assert response_data['messages'][0]['message'] == 'hello world'


# Test that function works properly for sharing to channel
def test_share_to_channel(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': channel_make_response['channel_id'],
        'dm_id': -1
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    response_data = channel_messages.json()

    assert response_data['messages'][0]['message'] == 'hello'

# Test that function works properly for sharing to channel with additional message
def test_share_to_channel_with_message(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'first',
        'time_sent': int(datetime.now().timestamp())
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': 'world',
        'channel_id': channel_make_response['channel_id'],
        'dm_id': -1
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    response_data = channel_messages.json()

    assert response_data['messages'][0]['message'] == 'hello world'

# neither channel_id nor dm_id are -1
def test_neither_channel_dm_id_minus1(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': 1,
        'dm_id': 1
    })

    assert message_share.status_code == InputError.code

# both ids provided are -1
def test_both_ids_minus1(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': -1
    })

    assert message_share.status_code == InputError.code

# both channel_id and dm_id are invalid
def test_both_channel_dm_id_invalid(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': 10,
        'dm_id': 10
    })

    assert message_share.status_code == InputError.code

# og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_invalid_og_message_id(clear_data):
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

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()

    requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': -1,
        'message': '',
        'channel_id': -1,
        'dm_id': dm_make_response['dm_id']
    })

    assert message_share.status_code == InputError.code

# length of message is more than 1000 characters
def test_too_many_characters(clear_data):
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

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_1_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': 'WUccdEY2CBEijbE17fnUNTDzYJfTKVxwnUij9vh93sa9e4nGxytlllMjwkRWQOTXbLo7xBdi3wbzxKlM6RgF1a8DjuMVjsbXHdTkxsZNAStR7Fs0NdRQFkOEGmdI2X3WW0I6BOIVbYyQuoyYuDlFbTEP7kBzWMSlbDNxwMBwOaeVEttiGmQCtCicICXEGCwFkAUCsI4nR4j463R6ziIiaAEuOwMrldUikIjKpNBCl7wIs0LzYMHAFqcGEIRzuuZsLwSa1bHKL52Md4jnC4kFtVgCHgQBn8wRAUp6m22a2myfbKdx10l3WqrJO3VrXwfxN1r6hL5uBxyvuoNEcMoHTzUHAjIaalIsF4IKRmp3wt8lPmghPbzz8xmGLXUXiNxQpU8rGRRhC0syjppICDVFbUEVdL7eVZOtRLndmtWnPlPBmyUyTKgDmfSFuHg9n1lgHBz3eq0l6Gyw43zOA6CxCWH3QMpdUyltsL0noif7HSMBUXOUUeYFFk9a8TlAXMLRFljdJVT57LAUxOHvjh1EBKp3BIR2dz8X2K9xv3Wx78p9cSNV68NNaDcp30HNgdFSQ85NIoylI1sC1p0zZd8fjsdoBnYS1tXtJV1ZihkeU9gnqLLvev5MGfZc6T0nLmjj7sdxmHeAfHTtqDuf4nEB9VuOZoxDBHRNxwYpDyj2rpKY02dcpXzJmr3sP5MlC5RDiVOxqmAJrd3k8ana5OQb6bDalzdAsXNJ7L9yASxTfZffgOsi2XBzY3LhIrGf5d0OsBf9nnPHCNIFFBbuxQXZN7Ua7v7Gszc2vX9ws34itDoScoYatPXf7VQVp7l72vkMGIBtoZYPI7dEba0rQmxjlUmFNYOQvrTGQsczeBfp098riCBxnDwekm8ppGozYGPjPbGBmWfwRmz3R0GhzxFXZKZWZV0t7sOjh9PPTvfHs88yWOXTZkRqpcQsHjqZtxRWk8FHwJcx1b13TcKWpxKKz0Ul6N2S1A547v0XGnoAKe8',
        'channel_id': -1,
        'dm_id': dm_make_response['dm_id']
    })

    assert message_share.status_code == InputError.code

# authorised user has not joined the channel or DM they are trying to share the message to
def test_user_not_member(clear_data):
    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password3',
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

    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user_2_data['token'], 
        'channel_id': channel_make_response['channel_id']
    })

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': user_1_data['token'],
            'dm_id': 1,
            'message': 'hello'
        })
    message_send_response = message_send.json()

    message_share = requests.post(BASE_URL + 'message/share/v1', json = {
        'token': user_2_data['token'],
        'og_message_id': message_send_response['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': dm_make_response['dm_id']
    })

    assert message_share.status_code == AccessError.code
