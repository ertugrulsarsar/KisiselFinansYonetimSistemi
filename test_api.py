import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'

def test_api():
    # 1. Kullanıcı Kaydı
    register_data = {
        'username': f'test_user_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'password': 'test123',
        'email': f'test_{datetime.now().strftime("%Y%m%d%H%M%S")}@example.com'
    }
    
    print('\n1. Kullanıcı Kaydı Testi')
    response = requests.post(f'{BASE_URL}/register', json=register_data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.json()}')
    
    # 2. Kullanıcı Girişi
    login_data = {
        'username': register_data['username'],
        'password': register_data['password']
    }
    
    print('\n2. Kullanıcı Girişi Testi')
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.json()}')
    
    if response.status_code == 200:
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 3. Kategori Oluştur
        category_data = {
            'name': 'Market',
            'description': 'Market harcamaları'
        }
        
        print('\n3. Kategori Oluşturma Testi')
        response = requests.post(f'{BASE_URL}/categories/create', 
                               headers=headers, 
                               json=category_data)
        print(f'Status: {response.status_code}')
        print(f'Response: {response.json()}')
        
        if response.status_code == 201:
            category_id = response.json()['id']
            
            # 4. İşlem Oluştur
            transaction_data = {
                'category_id': category_id,
                'amount': 150.75,
                'description': 'Haftalık market alışverişi',
                'transaction_type': 'expense',
                'transaction_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            print('\n4. İşlem Oluşturma Testi')
            response = requests.post(f'{BASE_URL}/transactions/create', 
                                   headers=headers, 
                                   json=transaction_data)
            print(f'Status: {response.status_code}')
            print(f'Response: {response.json()}')
            
            # 5. İşlemleri Listele
            print('\n5. İşlem Listeleme Testi')
            response = requests.get(f'{BASE_URL}/transactions/list', 
                                  headers=headers)
            print(f'Status: {response.status_code}')
            print(f'Response: {response.json()}')
            
            # 6. İşlem Özeti
            print('\n6. İşlem Özeti Testi')
            response = requests.get(f'{BASE_URL}/transactions/summary', 
                                  headers=headers)
            print(f'Status: {response.status_code}')
            print(f'Response: {response.json()}')

if __name__ == '__main__':
    test_api() 