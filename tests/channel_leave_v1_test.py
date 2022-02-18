import pytest
import requests
from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_invalid_user_token(clear_data):
    ''' test passing a token that doesnt exist '''
    
    # Invalid user tries to leave
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': 5, 'channel_id': 1
    })
    
    assert join_response.status_code == AccessError.code
    
def test_invalid_channel_id(clear_data):
    ''' test trying to join non existent channel '''

    # Register user
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': 'abc', 
        'is_public': True
    })
        
    # Try to join non_existent channel
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': register_response_data['token'], 'channel_id': 2
    })
    
    assert join_response.status_code == InputError.code   

def test_non_member(clear_data):
    ''' test trying to leave when not a member of a channel '''
    
    # Register User 1
    register_response_1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    # Register User 2
    register_response_2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'micheal@gmail.com', 'password': 'password',
        'name_first': 'micheal', 'name_last': 'smith'
    })
    
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()
    
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_1['token'], 'name': 'abc', 
        'is_public': True
    })
    
    # User 2 tries to leave channel
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': register_response_data_2['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == AccessError.code 
    
def test_non_owner_leaves(clear_data):
    ''' test a non owner member leaving channel '''
    
    # Register User 1
    register_response_1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    # Register User 2
    register_response_2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'micheal@gmail.com', 'password': 'password',
        'name_first': 'micheal', 'name_last': 'smith'
    })
    
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()
    
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_1['token'], 'name': 'abc', 
        'is_public': True
    })
    
    # User 2 joins channel
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_2['token'], 'channel_id': 1
    })
    
    # User 2 tries to leave channel
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': register_response_data_2['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == 200    
    
def test_leave_twice(clear_data):
    ''' test succesfully leaving then trying to leave again when not member '''
    
    # Register User 1
    register_response_1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
       
    register_response_data_1 = register_response_1.json()   
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_1['token'], 'name': 'abc', 
        'is_public': True
    })
    
    # User 1 leaves channel
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == 200
    
    # User 1 tries to leave again
    join_response = requests.post(BASE_URL + 'channel/leave/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == AccessError.code    
    
  
