import pytest
import requests

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError

BASE_URL = config.url

ACCESS_ERROR = 403
INPUT_ERROR = 400
SUCCESS = 200

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

# Test that function works properly
def test_remove_working(clear_data):
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

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })
    message_send_response = message_send.json()

    requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    assert channel_messages.json() == {'end': -1, 'messages': [], 'start': 0}

# Test for multiple messages for coverage
def test_multiple_messages(clear_data):
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
        'message': 'first'
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'second'
    })

    message_send_response = message_send.json()
    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == SUCCESS

# Test for multiple messages with different indexes for coverage
def test_multiple_messages_index_0(clear_data):
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

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'first'
    })

    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'second'
    })

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == SUCCESS

# Test for when message id is invalid
def test_invalid_message_id(clear_data):
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

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': -1
    })

    assert message_removed.status_code == INPUT_ERROR

# Test for when the requesting user is not the original message author
def test_user_non_author_message(clear_data):
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
        'token': user_2_data['token'], 'channel_id': channel_make_response['channel_id']
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })
    message_send_response = message_send.json()

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_2_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == ACCESS_ERROR

# Test for when the requesting user is not the original message author
def test_user_non_author_dm_message(clear_data):
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

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_2_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_2_data['token'],
        'dm_id': 1,
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == ACCESS_ERROR

# Test for when user is owner of the channel
def test_user_is_channel_owner(clear_data):
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
        'token': user_2_data['token'], 'channel_id': channel_make_response['channel_id']
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_2_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })
    message_send_response = message_send.json()

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == SUCCESS

# Test for when the requesting user is a dm owner
def test_user_is_dm_owner(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })

    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password3',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user_2_data = user_2_reg.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_2_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_2_data['token'],
        'dm_id': 1,
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_2_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == SUCCESS

# Test for multiple dm messages for coverage
def test_multiple_dms(clear_data):
    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })

    user_1_data = user_1_reg.json()

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

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': 1,
        'message': 'second'
    })

    message_removed = requests.delete(BASE_URL + 'message/remove/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id']
    })

    assert message_removed.status_code == SUCCESS
