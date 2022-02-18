import pytest
import requests
import sys
import signal

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
import json

BASE_URL = config.url
from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def new_user(email, password, fname, lname):
    user = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email' : email,
        'password' : password,
        'name_first': fname,
        'name_last': lname,
    })
    return user

def new_channel(name, is_public, token):
    channel = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': token,
        'name': name,
        'is_public': is_public,
    
    })
    return channel


def dummy_user_channels():
    user1 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1['token'],
        'name': 'General',
        'is_public': True
    })

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user1['token'],
        'channel_id': 1,
        'message': 'hello'
    })
    return user1['token']   

def dummy_user_dms():
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    return [member, owner]
# Tests

def test_invalid_react_id(clear_data):
    get_token = dummy_user_channels()

    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 3
    })
    
    assert message_react.status_code == 400

def test_invalid_message_id(clear_data):
    get_token = dummy_user_channels()

    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 2,
        'react_id': 1
    })   
    assert message_react.status_code == 400

def test_invalid_user_access(clear_data):
    dummy_user_channels()
    user2 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': user2['token'],
        'message_id': 1,
        'react_id': 1
    })
    assert message_react.status_code == 400

def test_dm_react(clear_data):
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': owner['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    assert message_react.status_code == 200

def test_channel_react(clear_data):
    get_token = dummy_user_channels()
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })

    assert message_react.status_code == 200

def test_not_in_dm_react(clear_data):
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("user1@email.com", "password", "abc", "def").json()
    
    outside = new_user("What@gmail.com", "password123", "Mike", "Smith").json()
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': outside['token'],
        'message_id': 1,
        'react_id': 1
    })

    assert message_react.status_code == 400

def test_react_dm_and_channel(clear_data):
    get_token = dummy_user_channels()
    owner = new_user("user1@gmail.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': get_token,
        'dm_id': 1,
        'message': "hey"
    })
    # User 1 reacts to messages in dms and in a channel
    message_react1 = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    message_react2 = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 3,
        'react_id': 1
    })
    assert message_react1.status_code == 200
    assert message_react2.status_code == 200

def test_multiple_react_dm(clear_data):
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': owner['token'],
        'message_id': 1,
        'react_id': 1
    })
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': member['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    assert message_react.status_code == 200

def test_multiple_react_channel(clear_data):
    get_token = dummy_user_channels()
    user2 = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': user2['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    assert message_react.status_code == 200

def test_already_react_channel(clear_data):
    get_token = dummy_user_channels()
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    
    assert message_react.status_code == 400

def test_already_react_dms(clear_data):
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': owner['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': member['token'],
        'message_id': 1,
        'react_id': 1
    })
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': member['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    assert message_react.status_code == 400

def test_react_login_channel(clear_data):
    get_token = dummy_user_channels()
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    
    requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': get_token
    })
    
    relog = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'Tony@gmail.com', 'password': '2password'
    }).json()
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': relog['token'],
        'message_id': 1,
        'react_id': 1
    })
    assert message_react.status_code == 400

def test_react_login_dm(clear_data):
    people = dummy_user_dms()
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    requests.post(BASE_URL + 'auth/logout/v1', json = {
        'token': people[0]['token']
    })
    
    relog = requests.post(BASE_URL + 'auth/login/v2', json = {
        'email': 'John@gmail.com', 'password': '1password'
    }).json()
    message_react = requests.post(BASE_URL + 'message/react/v1', json = {
        'token': relog['token'],
        'message_id': 1,
        'react_id': 1
    })  
    assert message_react.status_code == 400
    
