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
    # Tests for unauthorised unreact in channels
    dummy_user_channels()
    outsider = new_user("user1@email.com", "password", "abc", "def").json()
    
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': outsider['token'],
        'message_id': 1,
        'react_id': 1
    })
    assert unreact_response.status_code == 400
    
def test_invalid_message_id_dm(clear_data):
    # Tests for unauthorised unreact in dms
    dummy_user_dms()
    outsider = new_user("outside@gmail.com", "outside", "Hacker", "Man").json()
    
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': outsider['token'],
        'message_id': 1,
        'react_id': 1
    })
    assert unreact_response.status_code == 400

def test_invalid_react_id_channel(clear_data):
    # Tests for invalid react_id in channels
    get_token = dummy_user_channels()
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 23
    })
    assert unreact_response.status_code == 400
    
def test_invalid_react_id_dms(clear_data):
    # Tests for invalid react_id in dms
    people = dummy_user_dms()
    
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 23
    })
    assert unreact_response.status_code == 400

def test_unreact_no_reaction_channel(clear_data):
    # Tests for unreact when message has no reaction in channel
    get_token = dummy_user_channels()
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    assert unreact_response.status_code == 400

def test_unreact_no_reaction_dms(clear_data):
    # Tests for unreact when message has no reaction in dms
    people = dummy_user_dms()
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    assert unreact_response.status_code == 400

def test_non_existent_message(clear_data):
    # Tests for a message id that does not exist
    get_token = dummy_user_channels()
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': get_token,
        'message_id': 999,
        'react_id': 1
    })
    assert unreact_response.status_code == 400
    
def test_valid_unreact_channel(clear_data):
    # Simple successful case for unreact in channels
    get_token = dummy_user_channels()
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    })
    assert unreact_response.status_code == 200

def test_valid_unreact_dms(clear_data):
    # Simple successful case for unreact in dms
    people = dummy_user_dms()
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': people[1]['token'],
        'message_id': 1,
        'react_id': 1
    })
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    
    assert unreact_response.status_code == 200
    
def test_unreact_channel_invalid_unreact(clear_data):
    # Tests if user unreacts to a message in a channel with react from another
    # user
    get_token = dummy_user_channels()
    user2 = new_user("user1@email.com", "password", "abc", "def").json()
    
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': user2['token'],
        'message_id': 1,
        'react_id': 1
    })
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': get_token,
        'message_id': 1,
        'react_id': 1
    }) 
    assert unreact_response.status_code == 400

def test_unreact_dms_invalid_unreact(clear_data):
    # Tests if user unreacts to a message in a dm with react from another
    # user   
    people = dummy_user_dms()
    requests.post(BASE_URL + 'message/react/v1', json = {
        'token': people[0]['token'],
        'message_id': 1,
        'react_id': 1
    })
    unreact_response = requests.post(BASE_URL + 'message/unreact/v1', json = {
        'token': people[1]['token'],
        'message_id': 1,
        'react_id': 1
    }) 
    assert unreact_response.status_code == 400
    
           
