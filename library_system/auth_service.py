import hashlib
import jwt
from datetime import datetime, timedelta
from db_util import get_session, close_session
from models import User

SECRET_KEY = 'library-system-secret-key-2024'
JWT_SECRET = 'jwt-secret-key-2024'

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_token(user_id: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def register_user(user_id: str, password: str, role: str = 'reader'):
    session = get_session()
    try:
        existing = session.query(User).filter_by(user_id=user_id).first()
        if existing:
            return {'success': False, 'message': '用户名已存在'}
        
        user = User(
            user_id=user_id,
            password=hash_password(password),
            role=role
        )
        session.add(user)
        session.commit()
        return {'success': True, 'message': '注册成功'}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        close_session(session)

def login_user(user_id: str, password: str):
    session = get_session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        if not verify_password(password, user.password):
            return {'success': False, 'message': '密码错误'}
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        session.commit()
        
        token = create_token(user.user_id, user.role)
        return {
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': {'user_id': user.user_id, 'role': user.role, 'reader_id': user.reader_id}
        }
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        close_session(session)
