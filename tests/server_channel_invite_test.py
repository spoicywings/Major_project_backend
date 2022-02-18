import pytest
import requests
import sys
import signal

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError

BASE_URL = config.url

from src.error import InputError, AccessError
SUCCESS = 200

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

# This tests if channel_invite is working properly 
def test_invite_working(clear_data):

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

    requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': user_2_data['auth_user_id']
    })

    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token" : user_1_data['token'],
        "channel_id" : channel_make_response['channel_id']
    })
    channel_info_response = channel_info.json()

    # First owner member's name
    assert channel_info_response['all_members'][1]['name_first'] == "Jane" 



# This tests if the channel_id is invalid
def test_invalid_channel_id(clear_data):

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

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })

    response = requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_1_data['token'],
        'channel_id': -1,
        'u_id': user_2_data['auth_user_id'],
    })
    assert response.status_code == InputError.code

# This tests if the user id is invalid
def test_invalid_user_id(clear_data):

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
    response = requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': -1,
    })
    assert response.status_code == InputError.code

# This tests if the user is already a member of the channel
def test_existing_member(clear_data):

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

    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user_2_data['token'], 'channel_id': channel_make_response['channel_id']
    })

    response = requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': user_2_data['auth_user_id']
    })
    
    assert response.status_code == InputError.code

# This tests if the user is trying to add themselves
def test_self_invite(clear_data):
    
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
    response = requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': user_1_data['auth_user_id'],
    })
    assert response.status_code == InputError.code

# This tests if the channel id is valid but authorised user is not a member
def test_auth_user_not_member(clear_data):
    
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

    response = requests.post(BASE_URL + 'channel/invite/v2', json = {
        'token': user_2_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'u_id': user_2_data['auth_user_id'],
    })
    assert response.status_code == AccessError.code 

