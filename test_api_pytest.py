import pytest
import requests
from datetime import datetime

BASE_URL = 'http://localhost:5000'
test_user = None
access_token = None
test_category = None

def test_register():
    global test_user
    test_user = {
        'username': f'test_user_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'password': 'test123',
        'email': f'test_{datetime.now().strftime("%Y%m%d%H%M%S")}@example.com'
    }
    
    response = requests.post(f'{BASE_URL}/register', json=test_user)
    assert response.status_code == 201
    assert 'user_id' in response.json()

def test_login():
    global access_token
    login_data = {
        'username': test_user['username'],
        'password': test_user['password']
    }
    
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    access_token = response.json()['access_token']

def test_create_category():
    global test_category
    headers = {'Authorization': f'Bearer {access_token}'}
    category_data = {
        'name': 'Market',
        'description': 'Market harcamaları'
    }
    
    response = requests.post(f'{BASE_URL}/categories/create', 
                           headers=headers, 
                           json=category_data)
    assert response.status_code == 201
    assert 'id' in response.json()
    test_category = response.json()

def test_create_transaction():
    headers = {'Authorization': f'Bearer {access_token}'}
    transaction_data = {
        'category_id': test_category['id'],
        'amount': 150.75,
        'description': 'Haftalık market alışverişi',
        'transaction_type': 'expense',
        'transaction_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    response = requests.post(f'{BASE_URL}/transactions/create', 
                           headers=headers, 
                           json=transaction_data)
    assert response.status_code == 201
    assert 'id' in response.json()

def test_list_transactions():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{BASE_URL}/transactions/list', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'transactions' in data
    assert 'categories' in data

def test_get_summary():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{BASE_URL}/transactions/summary', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'total_income' in data
    assert 'total_expense' in data
    assert 'balance' in data 