import pytest
import requests
import sys
import signal

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
from src.error import InputError


BASE_URL = config.url

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def test_no_channels(clear_data):
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
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_2_data['token'],
        'name': 'User1Chann',
        'is_public': True,
    })
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_2_data['token'],
        'name': 'User2Chann',
        'is_public': False,
    })
    channel_list = requests.get(BASE_URL + 'channels/list/v2', params = {
        "token": user_1_data['token'],
    }).json()
    
    assert channel_list['channels'] == []

def test_list_multiple_channels(clear_data):
    user_1_reg = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email': 'john@gmail.com',
        'password': 'password2',
        'name_first' : 'John',
        'name_last' : 'Smith',
    })
    
    user_1_data = user_1_reg.json()
    
    #User creates multiple channels
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'Game-night',
        'is_public': True,
    })
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'Memes',
        'is_public': True,
    })

    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'Work',
        'is_public': True,
    })
    
    channel_list = requests.get(BASE_URL + 'channels/list/v2', params = {
        "token" : user_1_data['token'],
    }).json()
    assert len(channel_list['channels']) == 3
    assert channel_list['channels'][0]['name'] == "Game-night"
    assert channel_list['channels'][1]['name'] == "Memes"
    assert channel_list['channels'][2]['name'] == "Work"

def test_list_all(clear_data):
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
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_1_data['token'],
        'name': 'User1Chann',
        'is_public': True,
    })
    
    requests.post(BASE_URL + 'channels/create/v2', json = {
        'token': user_2_data['token'],
        'name': 'User2Chann',
        'is_public': False,
    })
    channel_list = requests.get(BASE_URL + 'channels/listall/v2', params = {
        "token": user_2_data['token'],
    }).json()
    assert len(channel_list['channels']) == 2
    assert channel_list['channels'][0]['name'] == "User1Chann"
    assert channel_list['channels'][1]['name'] == "User2Chann"
