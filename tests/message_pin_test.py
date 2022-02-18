import pytest
import requests
import sys
import signal

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
import json
from src.error import InputError, AccessError

BASE_URL = config.url

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
    # Function which creates a new user with u_id 1 and new channel with
    # channel_id 1 by the new user with a message sent
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
    # Function which creates a dm between 2 people with a message sent by 
    # both users and returns necessary data from both users
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

# TESTS

def test_invalid_message_id_channel(clear_data):
    # Test for invalid message id in a channel
    get_token = dummy_user_channels()
    
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': get_token,
        'message_id': 2
    })
    assert message_pin.status_code == 400
    
def test_invalid_message_id_dm(clear_data):
    # Test for invalid message id in a dm
    people = dummy_user_dms()
    
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': people[0]['token'],
        'message_id': 3
    })
    assert message_pin.status_code == 400
    
def test_already_pinned_channel(clear_data):
    # Test for pinning a message that is already pinned in channel
    get_token = dummy_user_channels()
    requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': get_token,
        'message_id': 1
    })
    
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': get_token,
        'message_id': 1
    })
    assert message_pin.status_code == 400

def test_already_pinned_dm(clear_data):
    # Test for pinning a message that is already pinned in dms
    people = dummy_user_dms()
    requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': people[1]['token'],
        'message_id': 1
    })
    
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': people[1]['token'],
        'message_id': 1
    })
    assert message_pin.status_code == 400

def test_not_owner_pin_channel(clear_data):
    # Tests for non owner permissions to pin in channel
    dummy_user_channels()
    user2 = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': user2['token'],
        'message_id': 1
    })
    assert message_pin.status_code == 400

def test_not_owner_pin_dm(clear_data):
    # Tests for non owner permissions to pin in dm  
    people = dummy_user_dms()
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': people[0]['token'],
        'message_id': 1
    })
    assert message_pin.status_code == 400

def test_valid_pin_channel(clear_data):
    # Valid case for pinning message in a channel
    get_token = dummy_user_channels()
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': get_token,
        'message_id': 1
    })
    assert message_pin.status_code == 200

def test_valid_pin_multiple_channel(clear_data):
    # Valid case for message to be pinned by another owner
    get_token = dummy_user_channels()
    user2 = new_user("user1@email.com", "password", "abc", "def").json()
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': get_token, 
        'channel_id': 1,
        'u_id': 2
    })
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': user2['token'],
        'message_id': 1
    })
    
    assert message_pin.status_code == 200
    
def test_valid_pin_dm(clear_data):
    # Valid case for message to be pinned in dm
    people = dummy_user_dms()
    message_pin = requests.post(BASE_URL + 'message/pin/v1', json = {
        'token': people[1]['token'],
        'message_id': 1
    })
    assert message_pin.status_code == 200
