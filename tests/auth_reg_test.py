import pytest

from src.auth import auth_register_v1, create_jwt
from src.error import InputError
from src.other import clear_v1
from src.data_store import data_store

def test_reg_invalid_email1():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('invalidemail', 'password', 'Eugene', 'Gush')
        
def test_reg_invalid_email2():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('!@gmail.com', 'password', 'Eugene', 'Gush')
     
def test_reg_duplicate_email():
    clear_v1()
    auth_register_v1('ejgush@gmail.com', 'password', 'Eugene', 'Gush')
    with pytest.raises(InputError):
        auth_register_v1('ejgush@gmail.com', 'password', 'Eugene', 'Gush')
    
def test_reg_invalid_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('ejgush@gmail.com', 'abc', 'Eugene', 'Gush')

def test_reg_invalid_firstname1():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('z5371368@ad.unsw.edu.au', 'password', '', 'Gush')
        
def test_reg_invalid_firstname2():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('z5371368@ad.unsw.edu.au', 'password', 'Thisfirstnameislongerthan50charactersandisthusinvalid', 'Gush')
    
def test_reg_invalid_lastname1():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('ejgush@gmail.com', 'password', 'Eugene', '')

def test_reg_invalid_lastname2():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('ejgush@gmail.com', 'password', 'Eugene', 'Thislastnameislongerthan50charactersandisthusinvalid')
        
def test_reg_valid_id():
    clear_v1()
    assert auth_register_v1('ejgush@gmail.com', 'password', 'Eugene', 'Gush')['auth_user_id'] == 1
    
def test_correct_handle():
    clear_v1()
    
    store = data_store.get()
    
    auth_register_v1('random@email.com', 'password', 'abc', 'def')
    user2 = auth_register_v1('anotherrandom@email.com', 'password', 'abc', 'def')['auth_user_id']
    
    for user in store['users']:
        if user['u_id'] == user2:
            assert user['handle_str'] == 'abcdef0'   
