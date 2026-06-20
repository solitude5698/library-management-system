from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from db_util import init_db

from auth_service import register_user, login_user, decode_token
from reader_service import add_reader, get_reader, update_reader, delete_reader, list_readers
from book_service import add_book, get_book, update_book, delete_book, list_books
from borrow_service import borrow_book, get_borrow_record, get_reader_borrow_records
from return_service import return_book, get_overdue_records
from query_service import get_hot_books, get_category_stats, get_borrow_trend, search_books

app = Flask(__name__)
CORS(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'code': 401, 'msg': '请先登录'})
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'token无效或已过期'})
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'code': 401, 'msg': '请先登录'})
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'token无效或已过期'})
        if payload.get('role') != 'admin':
            return jsonify({'code': 403, 'msg': '需要管理员权限'})
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    
    if not user_id or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'})
    
    result = login_user(user_id, password)
    
    if result.get('success'):
        return jsonify({
            'code': 200,
            'msg': result.get('message'),
            'data': {
                'token': result.get('token'),
                'user_id': result.get('user', {}).get('user_id'),
                'role': result.get('user', {}).get('role'),
                'reader_id': result.get('user', {}).get('reader_id')
            }
        })
    else:
        return jsonify({'code': 401, 'msg': result.get('message')})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    role = data.get('role', 'reader')
    
    if not user_id or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'})
    
    result = register_user(user_id, password, role)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/readers', methods=['GET'])
@login_required
def get_readers():
    keyword = request.args.get('keyword', '')
    result = list_readers(keyword=keyword)
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/readers/<reader_id>', methods=['GET'])
@login_required
def get_reader_info(reader_id):
    result = get_reader(reader_id)
    return jsonify({'code': 200 if result.get('success') else 404, 'msg': result.get('message'), 'data': result.get('data')})

@app.route('/api/readers', methods=['POST'])
@admin_required
def add_reader_api():
    data = request.json
    result = add_reader(data)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/readers/<reader_id>', methods=['PUT'])
@admin_required
def update_reader_api(reader_id):
    data = request.json
    result = update_reader(reader_id, data)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/readers/<reader_id>', methods=['DELETE'])
@admin_required
def delete_reader_api(reader_id):
    result = delete_reader(reader_id)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/books', methods=['GET'])
@login_required
def get_books():
    keyword = request.args.get('keyword', '')
    result = list_books(keyword=keyword)
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/books/<book_id>', methods=['GET'])
@login_required
def get_book_info(book_id):
    result = get_book(book_id)
    return jsonify({'code': 200 if result.get('success') else 404, 'msg': result.get('message'), 'data': result.get('data')})

@app.route('/api/books', methods=['POST'])
@admin_required
def add_book_api():
    data = request.json
    result = add_book(data)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/books/<book_id>', methods=['PUT'])
@admin_required
def update_book_api(book_id):
    data = request.json
    result = update_book(book_id, data)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/books/<book_id>', methods=['DELETE'])
@admin_required
def delete_book_api(book_id):
    result = delete_book(book_id)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/borrow', methods=['POST'])
@login_required
def borrow_book_api():
    data = request.json
    reader_id = data.get('reader_id')
    book_id = data.get('book_id')
    
    if not reader_id or not book_id:
        return jsonify({'code': 400, 'msg': '读者ID和图书ID不能为空'})
    
    token = request.headers.get('Authorization')
    payload = decode_token(token)
    operator_id = payload.get('user_id') if payload else None
    
    result = borrow_book(reader_id, book_id, operator_id)
    return jsonify({
        'code': 200 if result.get('success') else 400,
        'msg': result.get('message'),
        'data': {
            'borrow_id': result.get('borrow_id'),
            'borrow_date': result.get('borrow_date'),
            'due_date': result.get('due_date')
        }
    })

@app.route('/api/borrow/reader/<reader_id>', methods=['GET'])
@login_required
def get_reader_borrows_api(reader_id):
    result = get_reader_borrow_records(reader_id)
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/return', methods=['POST'])
@login_required
def return_book_api():
    data = request.json
    borrow_id = data.get('borrow_id')
    
    if not borrow_id:
        return jsonify({'code': 400, 'msg': '借阅流水号不能为空'})
    
    result = return_book(borrow_id)
    return jsonify({'code': 200 if result.get('success') else 400, 'msg': result.get('message')})

@app.route('/api/return/overdue', methods=['GET'])
@admin_required
def get_overdue_api():
    result = get_overdue_records()
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/stats/hot-books', methods=['GET'])
@login_required
def get_hot_books_api():
    top = int(request.args.get('top', 5))
    result = get_hot_books(top)
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/stats/borrow-trend', methods=['GET'])
@login_required
def get_borrow_trend_api():
    days = int(request.args.get('days', 30))
    result = get_borrow_trend(days)
    return jsonify({'code': 200, 'data': result.get('data', [])})

@app.route('/api/stats/category', methods=['GET'])
@login_required
def get_category_stats_api():
    result = get_category_stats()
    return jsonify({'code': 200, 'data': result.get('data', [])})
# ==================== 首页 ====================

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <h1>📚 图书管理系统</h1>
        <p>index.html 文件未找到，请确保它与 app.py 在同一目录下。</p>
        <hr>
        <p>可用的 API 接口：</p>
        <ul>
            <li><a href="/api/books">/api/books</a> - 查看所有图书</li>
            <li><a href="/api/readers">/api/readers</a> - 查看所有读者</li>
            <li><a href="/api/stats/hot-books">/api/stats/hot-books</a> - 热门图书</li>
        </ul>
        '''


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
