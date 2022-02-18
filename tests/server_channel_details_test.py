import pytest
import requests

from src import config
from src.error import InputError

BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')
 
def test_valid_channel_details(clear_data):
    
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
        'is_public': True,
    })
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'Gaming',
        'is_public': True,
    })
    
    channel_make_response = channel_make.json()
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token" : user_1_data['token'],
        "channel_id" : channel_make_response['channel_id'],
    })
    channel_info_response = channel_info.json()
    # First owner member's name
    assert channel_info_response['owner_members'][0]['name_first'] == "John" 


def test_invalid_user_access(clear_data):
    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()
    
    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'interesting@gmail.com',
        'password': 'magicpassword',
        'name_first' : 'Tony',
        'name_last' : 'Stark',
    })
    user_2_data = user_2_reg.json()
    
    
    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True,
    })
    channel_make_response = channel_make.json()
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token" : user_2_data['token'],
        "channel_id" : channel_make_response['channel_id'],
    })
    
    assert channel_info.status_code == 403

def test_invalid_channel_id(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json() 
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True,
    })
    
    channel_info = requests.get(BASE_URL + 'channel/details/v2', params = {
        "token" : user_1_data['token'],
        "channel_id" : 2,
    })
    
    assert channel_info.status_code == 400

