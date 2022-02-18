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
    response = requests.get(BASE_URL + 'dm/list/v1', params = {'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw'})
    
    assert response.status_code == AccessError.code

# When route is successful check that DM returned is correct
def test_one_dm_created(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'email@gmail.com', 'password': 'password', 
        'name_first': 'Eugene', 'name_last': 'Gush'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    
    response_data = response.json()
    create_return = requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})

    create_return_data = create_return.json()

    response = requests.get(BASE_URL + 'dm/list/v1', params = {'token': response_data['token']})
    response_data = response.json()

    assert response_data['dms'][0]['name'] == "eugenegush, johnsmith"
    assert response_data['dms'][0]['dm_id'] == create_return_data['dm_id']

# When there are two DMs but user is member of one
def test_one_dm_associated(clear_data, dm_create_single):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'tonybrown@gmail.com', 'password': 'comp1531', 
        'name_first': 'Tony', 'name_last': 'Brown'
    })
    
    response_data = response.json()
    create_return = requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1, 3]})

    create_return_data = create_return.json()    
    
    response = requests.get(BASE_URL + 'dm/list/v1', params = {'token': response_data['token']})
    response_data = response.json()
    
    assert response_data['dms'][0]['name'] == "billjackson, eugenegush, tonybrown"
    assert response_data['dms'][0]['dm_id'] == create_return_data['dm_id']

# When user is member of multiple DMs returned list of DMs
def test_multiple_dm_associated(clear_data, dm_create_single):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'billjackson@gmail.com', 'password': 'qwerty', 
        'name_first': 'Bill', 'name_last': 'Jackson'
    })
    response = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'tonybrown@gmail.com', 'password': 'comp1531', 
        'name_first': 'Tony', 'name_last': 'Brown'
    })
    response_data = response.json()
    
    create_return1 = requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1, 3]})
    create_return_data1 = create_return1.json()
    
    create_return2 = requests.post(BASE_URL + 'dm/create/v1', json = {'token': response_data['token'], 'u_ids': [1]})
    create_return_data2 = create_return2.json()

    response = requests.get(BASE_URL + 'dm/list/v1', params = {'token': response_data['token']})
    response_data = response.json()

    assert response_data['dms'][0]['name'] == "billjackson, eugenegush, tonybrown"
    assert response_data['dms'][0]['dm_id'] == create_return_data1['dm_id']
    assert response_data['dms'][1]['name'] == "eugenegush, tonybrown"
    assert response_data['dms'][1]['dm_id'] == create_return_data2['dm_id']
