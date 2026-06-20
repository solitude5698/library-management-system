import requests

BASE_URL = 'http://localhost:5000/api'

def test_register():
    print('测试注册...')
    resp = requests.post(f'{BASE_URL}/register', json={
        'user_id': 'admin',
        'password': 'admin123',
        'role': 'admin'
    })
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()

def test_login():
    print('测试登录...')
    resp = requests.post(f'{BASE_URL}/login', json={
        'user_id': 'admin',
        'password': 'admin123'
    })
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    result = resp.json()
    return result.get('data', {}).get('token') if result.get('code') == 200 else None

def test_add_reader(token):
    print('测试添加读者...')
    resp = requests.post(f'{BASE_URL}/readers', json={
        'reader_id': 'R001',
        'reader_name': '张三',
        'gender': '男',
        'category_code': 'undergrad',
        'department': '计算机学院',
        'phone': '13800138000'
    }, headers={'Authorization': token})
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()

def test_add_book(token):
    print('测试添加图书...')
    resp = requests.post(f'{BASE_URL}/books', json={
        'book_id': 'B001',
        'book_name': 'Python编程',
        'author': '张三',
        'publisher': '出版社',
        'category': '编程',
        'total_num': 5
    }, headers={'Authorization': token})
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()

def test_borrow(token):
    print('测试借书...')
    resp = requests.post(f'{BASE_URL}/borrow', json={
        'reader_id': 'R001',
        'book_id': 'B001'
    }, headers={'Authorization': token})
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()

def test_list(token):
    print('测试查询读者列表...')
    resp = requests.get(f'{BASE_URL}/readers', headers={'Authorization': token})
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()
    
    print('测试查询图书列表...')
    resp = requests.get(f'{BASE_URL}/books', headers={'Authorization': token})
    print(f'状态码: {resp.status_code}, 响应: {resp.json()}')
    print()

if __name__ == '__main__':
    print('='*50)
    print('API测试')
    print('='*50)
    print()
    
    test_register()
    token = test_login()
    
    if token:
        test_add_reader(token)
        test_add_book(token)
        test_borrow(token)
        test_list(token)
    
    print('='*50)
    print('测试完成')
    print('='*50)
