from db_util import get_session, close_session
from models import Reader
from datetime import date

def add_reader(data):
    session = get_session()
    try:
        if session.query(Reader).filter_by(reader_id=data['reader_id']).first():
            return {'success': False, 'message': '读者ID已存在', 'code': 200}
        
        reader = Reader(
            reader_id=data['reader_id'],
            reader_name=data['reader_name'],
            gender=data.get('gender', '男'),
            category_code=data.get('category_code', 'undergrad'),
            department=data.get('department'),
            phone=data.get('phone'),
            reg_date=date.today(),
            status='正常'
        )
        session.add(reader)
        session.commit()
        return {'success': True, 'message': '读者添加成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_reader(reader_id):
    session = get_session()
    try:
        reader = session.query(Reader).filter_by(reader_id=reader_id).first()
        if not reader:
            return {'success': False, 'message': '读者不存在', 'code': 200}
        
        return {'success': True, 'data': {
            'reader_id': reader.reader_id,
            'reader_name': reader.reader_name,
            'gender': reader.gender,
            'category_code': reader.category_code,
            'department': reader.department,
            'phone': reader.phone,
            'status': reader.status,
            'reg_date': reader.reg_date.strftime('%Y-%m-%d') if reader.reg_date else None
        }, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def update_reader(reader_id, data):
    session = get_session()
    try:
        reader = session.query(Reader).filter_by(reader_id=reader_id).first()
        if not reader:
            return {'success': False, 'message': '读者不存在', 'code': 200}
        
        if 'reader_name' in data:
            reader.reader_name = data['reader_name']
        if 'gender' in data:
            reader.gender = data['gender']
        if 'category_code' in data:
            reader.category_code = data['category_code']
        if 'department' in data:
            reader.department = data['department']
        if 'phone' in data:
            reader.phone = data['phone']
        if 'status' in data:
            reader.status = data['status']
        
        session.commit()
        return {'success': True, 'message': '读者信息更新成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def delete_reader(reader_id):
    session = get_session()
    try:
        reader = session.query(Reader).filter_by(reader_id=reader_id).first()
        if not reader:
            return {'success': False, 'message': '读者不存在', 'code': 200}
        
        session.delete(reader)
        session.commit()
        return {'success': True, 'message': '读者删除成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def list_readers(page=1, page_size=100, keyword=''):
    session = get_session()
    try:
        query = session.query(Reader)
        if keyword:
            query = query.filter(Reader.reader_name.like(f'%{keyword}%') | Reader.reader_id.like(f'%{keyword}%'))
        
        total = query.count()
        readers = query.order_by(Reader.reader_id).offset((page - 1) * page_size).limit(page_size).all()
        
        data = [{
            'reader_id': r.reader_id,
            'reader_name': r.reader_name,
            'gender': r.gender,
            'category_code': r.category_code,
            'department': r.department,
            'phone': r.phone,
            'status': r.status
        } for r in readers]
        
        return {'success': True, 'data': data, 'total': total, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)
