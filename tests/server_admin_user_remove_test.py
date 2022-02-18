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


def test_invalid_token(clear_data):
    new_user("user1@email.com", "password", "abc", "def")
   
    response = requests.get(BASE_URL + 'users/all/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'
    })
    
    assert response.status_code == AccessError.code


def test_invalid_uid(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
    new_user("Tony@gmail.com", "1password", "Tony", "Stark")
    new_user("Stan@gmail.com", "2password", "Stan", "Lee")
    new_user("Peter@gmail.com", "3password", "Peter", "Park")
    
    user_remove = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1['token'],
        'u_id': 6,
    })
    
    assert user_remove.status_code == InputError.code

def test_only_global_owner(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
    new_user("Tony@gmail.com", "1password", "Tony", "Stark")
    new_user("Stan@gmail.com", "2password", "Stan", "Lee")
    
    user_remove = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1['token'],
        'u_id': 1,
    })
    assert user_remove.status_code == InputError.code

def test_only_global_owner_after_promotion(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()
    
    # User1 promotes user2
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 2,
        'permission_id': 1,
    })
    
    # User2 demotes user1
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 1,
        'permission_id': 2,
    })
    # User2 is now the only global owner
    user_remove = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user2['token'],
        'u_id': 2,
    })
    assert user_remove.status_code == InputError.code

def test_not_global_owner(clear_data):
    new_user("John@gmail.com", "password", "John", "Smith")
    user2 = new_user("Tony@gmail.com", "1password", "Tony", "Stark").json()
    
    # User2 tries to remove user1 but is not authorised to
    user_remove = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user2['token'],
        'u_id': 1,
    })
    assert user_remove.status_code == AccessError.code

def test_remove_user_channel(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()

    # User1 promotes user2 to global
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 2,
        'permission_id': 1,
    })
    
    # User1 creates a channel
    new_channel("Memes", True, user1['token'])
    
    # User2 removes User1
    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user2['token'],
        'u_id': 1,
    })
    
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token": user1['token'],
        "channel_id": 1,
    })  
    assert channel_info.status_code == 403

def test_remove_user(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()

    # User1 promotes user2 to global
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 2,
        'permission_id': 1,
    })

    # User2 removes User1
    user_rem = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user2['token'],
        'u_id': 1,
    })
    
    
    assert user_rem.status_code == 200

def test_dm_remove_user(clear_data):
    member = new_user("John@gmail.com", "1password", "John", "Smith").json()
    owner = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()

    
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': member['token'],
        'u_id': 2,
        'permission_id': 1,
    })
    
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': owner['token'],
        'u_ids': [1]
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': member['token'],
        'dm_id': 1,
        'message': "hey"
    })
    
    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': owner['token'],
        'dm_id': 1,
        'message': "hello there"
    })
    
    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': owner['token'],
        'u_id': 1,
    })

    data = requests.get(BASE_URL + 'dm/details/v1', params = {
        'token': owner['token'], 
        'dm_id': 1
    }).json()
    assert len(data['members']) == 1

def test_remove_user_channel_messages(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()
    
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 2,
        'permission_id': 1,
    })
    
    new_channel("General", True, user1['token'])
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2['token'],
        'channel_id' : 1
    })
    
    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user2['token'],
        'u_id': 1,
    })
    
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        'token': user2['token'],
        'channel_id': 1,
    }).json()
    
    assert channel_info['all_members'][0]['name_first'] == "Tony"

def test_remove_member_user(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()
   
    repsone = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1['token'],
        'u_id': 2,
    })
    
    assert repsone.status_code == 200
    
def test_remove_member_do_actions(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2['token'],
        'name': 'General',
        'is_public': True
    })

    requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1['token'],
        'u_id': 2,
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2['token'],
        'channel_id': 1,
        'message': 'hello'
    })
    
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token" : user2['token'],
        "channel_id" : 1,
    })

    # A removed user trying to send a message
    assert message_send.status_code == 403
    assert channel_info.status_code == 403

def test_remove_from_dm_and_channels(clear_data):
    user1 = new_user("John@gmail.com", "1password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "2password", "Tony", "Stark").json()
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user2['token'],
        'name': 'General',
        'is_public': True
    })
    
    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user2['token'],
        'channel_id': 1,
        'message': 'hello'
    })
    
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': user2['token'], 'u_ids': [1]})

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user2['token'],
        'dm_id': 1,
        'message': "hi"
    })

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user1,
        'dm_id': 1,
        'message': "hey"
    })
    
    user_remove = requests.delete(BASE_URL + 'admin/user/remove/v1', json = {
        'token': user1['token'],
        'u_id': 2,
    })
    assert user_remove.status_code == 200
