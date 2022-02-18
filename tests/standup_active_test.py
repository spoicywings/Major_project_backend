import pytest
import requests
import json
import time

from src import config
from src.error import InputError, AccessError

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

@pytest.fixture
def channel_create_single():
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

# Raises an AccessError when token is invalid
def test_invalid_token(clear_data, channel_create_single):
    response = requests.get(BASE_URL + 'standup/active/v1', params = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMjAiLCJzZXNzaW9uX2lkIjoiMSJ9.JJ0SDEJEJJfyDbPd8UQ1gWaweIvaP63Wv4SC9gWq1zw', 
        'channel_id': 1
    })
    
    assert response.status_code == AccessError.code

# Raises an InputError when channel_id is invalid
def test_invalid_channel_id(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    response = requests.get(BASE_URL + 'standup/active/v1', params = {
        'token': user1_data['token'], 
        'channel_id': 2
    })
    
    assert response.status_code == InputError.code

# Raises an AccessError when channel_id is valid but not member of channel
def test_not_channel_member(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    user2 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'new@gmail.com', 'password': 'password', 
        'name_first': 'John', 'name_last': 'Smith'
    })
    user2_data = user2.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })

    response = requests.get(BASE_URL + 'standup/active/v1', params = {
        'token': user2_data['token'], 
        'channel_id': 1
    })
    
    assert response.status_code == AccessError.code
    
# When standup is active
def test_standup_active(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    timestamp = requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 5
    })
    timestamp_data = timestamp.json()
    
    response = requests.get(BASE_URL + 'standup/active/v1', params = {
        'token': user1_data['token'], 
        'channel_id': 1
    })
    response_data = response.json()
    
    assert response_data['is_active'] == True
    assert response_data['time_finish'] == timestamp_data['time_finish']

# When standup is inactive
def test_standup_inactive(clear_data):
    user1 = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'joebrown@gmail.com', 'password': 'password', 
        'name_first': 'Joe', 'name_last': 'Brown'
    })
    user1_data = user1.json()

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user1_data['token'], 'name': 'abc', 
        'is_public': 'True'
    })
    
    requests.post(BASE_URL + 'standup/start/v1', json = {
        'token': user1_data['token'], 
        'channel_id': 1,
        'length': 3
    })
    
    time.sleep(3)
    
    response = requests.get(BASE_URL + 'standup/active/v1', params = {
        'token': user1_data['token'], 
        'channel_id': 1
    })
    response_data = response.json()
    
    assert response_data['is_active'] == False
    assert response_data['time_finish'] == None
