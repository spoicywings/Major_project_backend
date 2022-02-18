import pytest
import requests
from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
    
def test_invalid_token(clear_data):    
    ''' test using token that does not exist '''
    
    # Invalid token
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': 5, 'channel_id': 1, 'u_id': 1
    })
    
    assert add_response.status_code == AccessError.code

def test_invalid_user_id(clear_data):   
    ''' test using u_id that does not exist ''' 
    
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
    
    # User 1 tries to remove invalid user_id
    remove_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': 3
    }) 
    
    assert remove_response.status_code == InputError.code

def test_invalid_channel_id(clear_data):
    ''' tests for channel_id that does not exist '''
    
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
       
    
    # User 1 tries to addowner to invalid channel
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 3, 'u_id': 1
    })
     
    assert add_response.status_code == InputError.code
    
def test_non_member(clear_data):
    ''' test using a u_id which is not part of the channel '''
    
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
    
    # User 1 tries to make User 2 an owner 
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    assert add_response.status_code == InputError.code
    
def test_already_owner(clear_data):
    ''' test that tries to add ownership to a user who is already an owner'''

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
    
    # User 1 tries to make User 2 an owner 
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_1['auth_user_id']
    }) 
    
    assert add_response.status_code == InputError.code

def test_non_owner(clear_data):
    ''' test which is given the token of a user that does not have owner permissions '''
    
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
    
    # User 2 tries to make User 2 an owner 
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_2['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    assert add_response.status_code == AccessError.code
    
def test_add_owner_twice(clear_data):   
    ''' adds an owner succesfully then tries to add an already owner as an owner '''

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
    
    # User 1 makes User 2 an owner 
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    assert add_response.status_code == 200 
    
    # User 1 tries to make User 2 an owner again 
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    assert add_response.status_code == InputError.code

def test_token_is_non_member(clear_data):
    ''' non member tries to remove member '''
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
    
    # Register User 3
    register_response_3 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'michealdd@gmail.com', 'password': 'password',
        'name_first': 'micheal', 'name_last': 'smith'
    })
    
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()
    register_response_data_3 = register_response_3.json()
    
    
    # User 2 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_2['token'], 'name': 'abc', 
        'is_public': True
    })   
    
    # User 3 joins channel
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_3['token'], 'channel_id': 1
    })
    
    # User 1 tries to add user 3 as owner
    add_response = requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_3['auth_user_id']
    })
    
    assert add_response.status_code == AccessError.code  
