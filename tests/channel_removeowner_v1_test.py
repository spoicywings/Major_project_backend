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
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': 5, 'channel_id': 1, 'u_id': 1
    })
    
    assert remove_response.status_code == AccessError.code
    
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
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
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
    
    # User 1 tries to removeowner in invalid channel
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 2, 'u_id': 1
    })
     
    assert remove_response.status_code == InputError.code    
    
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
    
    # User 1 tries remove User 2 an owner 
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    assert remove_response.status_code == InputError.code  

def test_only_owner(clear_data):
    ''' test that tries to remove ownership from the only the owner'''

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
    
    # User 1 tries to remove themselves as owners
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_1['auth_user_id']
    }) 
    
    assert remove_response.status_code == InputError.code
    
    
def test_not_owner(clear_data):   
    ''' test which is tries to remove ownership from user without ownership'''

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
    
    # User 1 tries to remove a non owner as owner
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })  
    
    assert remove_response.status_code == InputError.code
    
def test_no_permissions(clear_data):
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
    
    # Register User 3
    register_response_3 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jack@gmail.com', 'password': 'password',
        'name_first': 'jack', 'name_last': 'jackson'
    })
    
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()
    register_response_data_3 = register_response_3.json()
    
    
    
    # User 1 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_1['token'], 'name': 'abc', 
        'is_public': True
    })   
    
    # User 2 joins channel
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_2['token'], 'channel_id': 1
    })
    
    # User 3 joins channel
    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': register_response_data_3['token'], 'channel_id': 1
    })
    
    # User 1 Makes User 2 Owner
    requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
     # User 3 tries to remove user 2
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_3['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })  
    
       
    assert remove_response.status_code == AccessError.code    

def test_remove_twice(clear_data):
    ''' succesfully removes user as owner, then tries again to user who is no longer owner '''
    
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
  
    # User 1 Makes User 2 Owner
    requests.post(BASE_URL + 'channel/addowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })
    
    # User 1 removes user 2
    
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })  
    
    assert remove_response.status_code == 200
     
    # User 1 removes user 2 again
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })      
      
    assert remove_response.status_code == InputError.code  

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
    
    
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()
    
    
    # User 2 creates channel
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data_2['token'], 'name': 'abc', 
        'is_public': True
    })   
    
    
    # User 1 tries to remove user 2 as owner
    remove_response = requests.post(BASE_URL + 'channel/removeowner/v1', json = {
        'token': register_response_data_1['token'], 'channel_id': 1,
         'u_id': register_response_data_2['auth_user_id']
    })   
    
    assert remove_response.status_code == AccessError.code   
    
