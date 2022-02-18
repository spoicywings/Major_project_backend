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
    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw',
        'dm_id': 1,
        'start': 0
    })
    
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
    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': response_data['token'],
        'u_ids': [1]
    })

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 2,
        'start': 0
    })

    assert response.status_code == InputError.code

# Raises an InputError.code when start is greater than len(messages)
def test_invalid_start(clear_data):
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

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 1,
        'start': 999999999999
    })

    assert response.status_code == InputError.code

# Raises an AccessError.code when valid user is not member of DM
def test_not_member(clear_data, dm_create_single):
    data = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    
    not_member = data.json()
    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': not_member['token'],
        'dm_id': 1,
        'start': 0
    })

    assert response.status_code == AccessError.code

# Case when function reaches the end of the list
def test_end_no_more_messages(clear_data):
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

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': response_data['token'],
        'dm_id': 1,
        'message': "hi"
    })

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 1,
        'start': 0
    })

    response_data = response.json()

    assert response_data['end'] == -1

# Case when function does not reach the end of the list
def test_end_more_fifty_messages(clear_data):
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

    i = 0
    while i < 51:
        requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': response_data['token'],
            'dm_id': 1,
            'message': "hi"
        })
        i += 1

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 1,
        'start': 0
    })

    response_data = response.json()

    assert response_data['end'] == 50

# Edge case when function reaches the end of the list and fifty messages only 
def test_end_fifty_messages(clear_data):
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

    i = 0
    while i < 50:
        requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': response_data['token'],
            'dm_id': 1,
            'message': "hi"
        })
        i += 1

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 1,
        'start': 0
    })

    response_data = response.json()

    assert response_data['end'] == -1

# Test that checks function works at any index
def test_start_not_zero(clear_data):
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

    i = 0
    while i < 60:
        requests.post(BASE_URL + 'message/senddm/v1', json = {
            'token': response_data['token'],
            'dm_id': 1,
            'message': "hi"
        })
        i += 1

    response = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': response_data['token'],
        'dm_id': 1,
        'start': 4
    })

    response_data = response.json()

    assert response_data['end'] == 54
