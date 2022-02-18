import pytest
import requests

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError
from datetime import datetime
from datetime import timezone

BASE_URL = config.url

from src.error import InputError, AccessError
SUCCESS = 200

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

# Test that function works properly
def test_sendlaterdm_working(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()
    
    requests.post(BASE_URL + 'message/sendlaterdm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp() + 10)
    })

    dm_messages = requests.get(BASE_URL + 'dm/messages/v1', params = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'start': 0
    })

    response = dm_messages.json()

    assert int(response['messages'][0]['time_created']) == int(datetime.now().timestamp())

# dm_id does not refer to a valid DM
def test_invalid_dm(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    
    response = requests.post(BASE_URL + 'message/sendlaterdm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': -1,
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp() + 10)
    })

    assert response.status_code == InputError.code

# length of message is over 1000 characters
def test_dm_message_too_long(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()
    
    dm_send = requests.post(BASE_URL + 'message/sendlaterdm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'message': 'WUccdEY2CBEijbE17fnUNTDzYJfTKVxwnUij9vh93sa9e4nGxytlllMjwkRWQOTXbLo7xBdi3wbzxKlM6RgF1a8DjuMVjsbXHdTkxsZNAStR7Fs0NdRQFkOEGmdI2X3WW0I6BOIVbYyQuoyYuDlFbTEP7kBzWMSlbDNxwMBwOaeVEttiGmQCtCicICXEGCwFkAUCsI4nR4j463R6ziIiaAEuOwMrldUikIjKpNBCl7wIs0LzYMHAFqcGEIRzuuZsLwSa1bHKL52Md4jnC4kFtVgCHgQBn8wRAUp6m22a2myfbKdx10l3WqrJO3VrXwfxN1r6hL5uBxyvuoNEcMoHTzUHAjIaalIsF4IKRmp3wt8lPmghPbzz8xmGLXUXiNxQpU8rGRRhC0syjppICDVFbUEVdL7eVZOtRLndmtWnPlPBmyUyTKgDmfSFuHg9n1lgHBz3eq0l6Gyw43zOA6CxCWH3QMpdUyltsL0noif7HSMBUXOUUeYFFk9a8TlAXMLRFljdJVT57LAUxOHvjh1EBKp3BIR2dz8X2K9xv3Wx78p9cSNV68NNaDcp30HNgdFSQ85NIoylI1sC1p0zZd8fjsdoBnYS1tXtJV1ZihkeU9gnqLLvev5MGfZc6T0nLmjj7sdxmHeAfHTtqDuf4nEB9VuOZoxDBHRNxwYpDyj2rpKY02dcpXzJmr3sP5MlC5RDiVOxqmAJrd3k8ana5OQb6bDalzdAsXNJ7L9yASxTfZffgOsi2XBzY3LhIrGf5d0OsBf9nnPHCNIFFBbuxQXZN7Ua7v7Gszc2vX9ws34itDoScoYatPXf7VQVp7l72vkMGIBtoZYPI7dEba0rQmxjlUmFNYOQvrTGQsczeBfp098riCBxnDwekm8ppGozYGPjPbGBmWfwRmz3R0GhzxFXZKZWZV0t7sOjh9PPTvfHs88yWOXTZkRqpcQsHjqZtxRWk8FHwJcx1b13TcKWpxKKz0Ul6N2S1A547v0XGnoAKe8',
        'time_sent': int(datetime.now().timestamp() + 10)
    })

    assert dm_send.status_code == InputError.code

# time_sent is a time in the past
def test_dm_time_in_past(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()
    
    dm_send = requests.post(BASE_URL + 'message/sendlaterdm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp() - 60)
    })

    assert dm_send.status_code == InputError.code

# dm_id is valid and the authorised user is not a member of the DM they are trying to post to
def test_user_not_dm_member(clear_data):

    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    user_1_data = user_1_reg.json()

    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password3',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user_2_data = user_2_reg.json()

    dm_make = requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_1_data['token'],
        'u_ids': [1]
    })
    dm_make_response = dm_make.json()
    
    dm_send = requests.post(BASE_URL + 'message/sendlaterdm/v1', json = {
        'token': user_2_data['token'],
        'dm_id': dm_make_response['dm_id'],
        'message': 'hello',
        'time_sent': int(datetime.now().timestamp() + 10)
    })

    assert dm_send.status_code == AccessError.code

    
