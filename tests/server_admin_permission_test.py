import pytest
import requests
import sys
import signal

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src import config
import json

BASE_URL = config.url
from src.error import InputError, AccessError

@pytest.fixture
def clear_data():
    requests.delete(BASE_URL + 'clear/v1')

def new_user(email, password, fname, lname):
    user = requests.post(BASE_URL + 'auth/register/v2', json = {
        'email' : email,
        'password' : password,
        'name_first': fname,
        'name_last': lname,
    })
    return user
    
    
def test_invalid_uid(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
        
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id': 2,
        'permission_id': 1,
    })
    assert admin.status_code == InputError.code
    
def test_demote_global_owner_unauth(clear_data):
    new_user("John@gmail.com", "password", "John", "Smith")
    user2 = new_user("Tony@gmail.com", "1password1", "Tony", "Stark").json()
    #User2 tries to demote the owner User1 but has no power to
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user2['token'],
        'u_id' : 1,
        'permission_id': 2,
    })
    assert admin.status_code == AccessError.code
    
def test_demote_global_owner_auth(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()

    #User1 tries to demote User1 but unable to as they are the only global owner
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id' : 1,
        'permission_id': 2,
    })
    assert admin.status_code == InputError.code

def test_invalid_permission_id(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
    new_user("Tony@gmail.com", "1password1", "Tony", "Stark")
    
    #User1 gives User2 an unknown permission (not 1 or 2)
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'],
        'u_id' : 2,
        'permission_id': 3,
    })
    assert admin.status_code == InputError.code
    
def test_valid_promotion(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
    new_user("Tony@gmail.com", "1password1", "Tony", "Stark")
    
    #User1 promotes user2 to global owner
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user1['token'], 
        'u_id' : 2,
        'permission_id': 1,
    })
    assert admin.status_code == 200

def test_valid_demotion(clear_data):
    user1 = new_user("John@gmail.com", "password", "John", "Smith").json()
    user2 = new_user("Tony@gmail.com", "1password1", "Tony", "Stark").json()
    
    #User2 demotes User1 after promotion
    requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token' : user1['token'],
        'u_id' : 2,
        'permission_id': 1,
    })
    
    admin = requests.post(BASE_URL + 'admin/userpermission/change/v1', json = {
        'token': user2['token'],
        'u_id' : 1,
        'permission_id': 2,
    })
    assert admin.status_code == 200      
