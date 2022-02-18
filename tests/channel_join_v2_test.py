import pytest
import requests
from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_invalid_user_token(clear_data):
    ''' test given a token that does not exist'''
    
    # Invalid user tries to join
    join_response = requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': 5, 'channel_id': 1
    })
    
    assert join_response.status_code == AccessError.code
    

def test_invalid_channel_id(clear_data):
    ''' test given a channel_id that does not exist '''
    
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
    join_response = requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data['token'], 'channel_id': 2
    })
    
    assert join_response.status_code == InputError.code
    
def test_already_member(clear_data):
    ''' test for trying to join a channel already as a member '''
    
    # Register user1
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    # Try to join channel when already member
    join_response = requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == InputError.code
    
def test_private_channel(clear_data):
    ''' test for a non global owner, trying to join a private channel '''
    
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
        'is_public': False
    })
    
    # User 2 tries to join private channel
    join_response = requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_2['token'], 'channel_id': 1
    })
    
    assert join_response.status_code == AccessError.code          
  

def test_global_owner(clear_data):
    ''' test for a non error execution where the a global owner joins a private channel '''
    
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
    
    
    # User 2 creates private channel
    create_response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_2['token'], 'name': 'abc', 
        'is_public': False
    })
    
    create_response_data = create_response.json()
    
    # User 1 (global owner) joins private channel
    join_response = requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_1['token'], 'channel_id': create_response_data['channel_id']
    })
    
    assert join_response.status_code == 200 


