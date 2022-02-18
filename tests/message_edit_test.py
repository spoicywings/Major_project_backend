import pytest
import requests

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError

BASE_URL = config.url

from src.error import InputError, AccessError
SUCCESS = 200

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')


# Test that function works properly
def test_edit_working(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello again'
    })
    message_send_response = message_send.json()
    
    requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    channel_messages = requests.get(BASE_URL + 'channel/messages/v2', params = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'start': 0
    })

    response = channel_messages.json()

    assert response['messages'][0]['message'] == 'edited'

# Test for multiple messages for coverage
def test_multiple_messages(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'first'
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'second'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == SUCCESS

# Test for multiple messages with different indexes for coverage
def test_multiple_messages_index_0(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'first'
    })

    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'second'
    })

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == SUCCESS

# Test that function works properly
def test_edit_empty_working(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': ''
    })

    assert message_edit.status_code == SUCCESS

# Test for edited message exceeding maximum character length allowed
def test_message_too_long(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'fsIZGSDUraO98ddk5V5P0XvN6Uzddp1moBKItuWlAdtI1RUgpGAELfHsv4OQgzuXYqj1WyvECixvpMgDw9nu1UhZDQebe3qKLXmeXe5Vu7eVGhwkB8r7AinatakMtw4gn13hXyNTjol21whfvxTFvVXV98E26qeHOSQkG9ifeV9MM9FMqJF3rJI0M0s5Pupa0BnzPnb7SaXBM3PHJrfTX6ESkkMyBNqOGD6G89oENSitmgx3T1t1JyrYlZBWuenXNGHJ7J8jjU0o1L8cWvupOaDb5aOZAf98A4i8hzgFWtfIBKZjSCSOan12QeQxIwO6VOkQppn9CTLWv5EGMKDf92BUIGzCsTMEiYHHepA7FJ0EPqPtfrshXtYQTuP1BiAeKeMFMnyMZiOsWyBmL9hGwRuC6xryMu4Kn4DE1CDeiIsvLkbkdoCtTTdl7pTncPRvI2KFaEbmqdkfhZD06oijfnLo9CobN84WZ5yq6sYEAaJtpZIXjRQpPOkvVXwyA3fSLq8kQoHwektDHrOAqEfTn654nqFe8B4vBvPydVLNz8C4Ha7i3sdNfH1MHJktXVA8dczVEwGqIWy8jhpUgcbWhr62LSs0nZKIhnRFIPGWTx1xk9NHLX1akkDEAYdNK5r1jAzaehRP6ii8sNZ5znXNnk6TsDms5flJDGfQe8UbHiv8a4xt8gfFHQ8L2rGfBO9cyas8LfOw7HHwFtltNvEfayUbPQ0iaVconlWWOehu9Dvf0AB047H8PqFD4zkJW7mUhWAAZmEBHv3Dhd2yZPfDBnX39HX7K2zVOsqg2yI74FE9DdTVpdb3LcYhNirtMo8305SqiJ20XY5lLDjP1Lj0V7HoFwSPs0TPsz64vjope5ce4yyqeVZz8BKlXWI3umG8BTdgSLKwhFlhomC0NdhtahwvalsvDMY30QfJUj3JvGF9yzTXPdv9YhdHqmngpwnNci126G468t1bfqDTmaHLsSY4LulQuMTMrPkoqFMSd'
    })

    assert message_edit.status_code == InputError.code

# Test for message id being invalid
def test_invalid_message_id(clear_data):
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
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': -1,
        'message': 'edited'
    })

    assert message_edit.status_code == InputError.code

# Test for message not created by requesting user
def test_user_non_author_message(clear_data):
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
    
    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user_2_data['token'], 'channel_id': channel_make_response['channel_id']
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_1_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_2_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == AccessError.code

# Test for when the requesting user is a channel owner
def test_user_is_channel_owner(clear_data):
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

    channel_make = requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'General',
        'is_public': True
    })
    channel_make_response = channel_make.json()

    requests.post(BASE_URL + 'channel/join/v2', json = {
        'token': user_2_data['token'], 'channel_id': channel_make_response['channel_id']
    })

    message_send = requests.post(BASE_URL + 'message/send/v1', json = {
        'token': user_2_data['token'],
        'channel_id': channel_make_response['channel_id'],
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_2_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == SUCCESS

# Test for when the requesting user is a dm owner
def test_user_is_dm_owner(clear_data):
    requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })

    user_2_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'jane@gmail.com',
        'password': 'password3',
        'name_first' : 'Jane',
        'name_last' : 'Apple',
    })
    user_2_data = user_2_reg.json()

    requests.post(BASE_URL + 'dm/create/v1', json = {
        'token': user_2_data['token'],
        'u_ids': [1]
    })

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_2_data['token'],
        'dm_id': 1,
        'message': 'hello'
    })

    message_send_response = message_send.json()

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_2_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == SUCCESS

# Test for multiple dm messages for coverage
def test_multiple_dms(clear_data):
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

    message_send = requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': 1,
        'message': 'hello'
    })

    message_send_response = message_send.json()

    requests.post(BASE_URL + 'message/senddm/v1', json = {
        'token': user_1_data['token'],
        'dm_id': 1,
        'message': 'second'
    })

    message_edit = requests.put(BASE_URL + 'message/edit/v1', json = {
        'token': user_1_data['token'],
        'message_id': message_send_response['message_id'],
        'message': 'edited'
    })

    assert message_edit.status_code == SUCCESS

