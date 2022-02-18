import pytest
import requests
from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_invalid_name_short(clear_data):
    ''' test for creating a channel with too short a name (<1) '''

    # register user
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    # Create channel with short name
    response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': '', 
        'is_public': 'True'
    })
    
    assert response.status_code == InputError.code
    
def test_invalid_name_long(clear_data):
    ''' test for creating a channel with too short a name (>20) '''
    # Register user
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    # Create channel with long name
    response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 
        'name': '123456789012345678901', 'is_public': 'True'
    })
    
    assert response.status_code == InputError.code
    
def test_non_string_token(clear_data):
    ''' test given a non string token '''
    
    
    # Create channel with incorrect token
    response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': 1, 'name': 'name', 'is_public': 'True'
    })
    
    assert response.status_code == AccessError.code

def test_valid_create(clear_data):
    ''' test that given valid input the function returns a correct channel_id '''    
    
    # Register user
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    # Create valid channel
    create_response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    create_response_data = create_response.json()
    
    assert create_response_data['channel_id'] == 1
    
def test_valid_create_2(clear_data):
    ''' test with valid inputs the creation of two channels and assert they
     return correct channel_id '''

    # Register user
    register_response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com', 'password': 'password',
        'name_first': 'abc', 'name_last': 'def'
    })
    
    register_response_data = register_response.json()
    
    # Create valid channel
    create_response = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    # Create second valid channel
    create_response_2 = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': register_response_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    create_response_data = create_response.json()
    create_response_data_2 = create_response_2.json()
    
    assert create_response_data['channel_id'] == 1
    assert create_response_data_2['channel_id'] == 2
    
    
    
