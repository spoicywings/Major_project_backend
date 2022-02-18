import pytest
import requests
import json

from src import config

BASE_URL = config.url

from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def dm_create_single():
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })

# Raises an AccessError.code when token is invalid
def test_invalid_token(clear_data, dm_create_single):
    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': 
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 'dm_id': 1})
    
    assert response.status_code == AccessError.code

# Raises an InputError.code when dm_id is invalid
def test_invalid_dm_id(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': response_data['token'], 'dm_id': 2})

    assert response.status_code == InputError.code

# Raises an AccessError.code when token and dm_id are invalid
def test_both_invalid_token_dm_id(clear_data, dm_create_single):
    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': 
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 'dm_id': 2})
    
    assert response.status_code == AccessError.code

# Raises an AccessError.code when valid user is not member of DM
def test_not_member(clear_data, dm_create_single):
    data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    
    not_member = data.json()
    response = requests.get(BASE_URL + 'dm/details/v1', params = {'token': not_member['token'], 'dm_id': 1})

    assert response.status_code == AccessError.code

# When route is successful check that the return values are correct
def test_return_details(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })

    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })

    response_data = response.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })

    data = requests.get(BASE_URL + 'dm/details/v1', params = {'token': response_data['token'], 'dm_id': 1})
    data_return = data.json()
    
    info = requests.get(BASE_URL + 'dm/list/v1', params = {'token': response_data['token']})
    info_data = info.json()
    
    name = None
    
    for dm in info_data['dms']:
        if dm['dm_id'] == 1:
            name = dm['name']
    
    assert data_return['name'] == name
