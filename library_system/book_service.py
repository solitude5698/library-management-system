from db_util import get_session, close_session
from models import Book
from datetime import date

def add_book(data):
    session = get_session()
    try:
        if session.query(Book).filter_by(book_id=data['book_id']).first():
            return {'success': False, 'message': '图书ID已存在', 'code': 200}
        
        book = Book(
            book_id=data['book_id'],
            book_name=data['book_name'],
            author=data.get('author'),
            publisher=data.get('publisher'),
            pub_date=date.today(),
            category=data.get('category'),
            total_num=data.get('total_num', 1),
            remain_num=data.get('total_num', 1),
            location=data.get('location'),
            price=data.get('price')
        )
        session.add(book)
        session.commit()
        return {'success': True, 'message': '图书添加成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_book(book_id):
    session = get_session()
    try:
        book = session.query(Book).filter_by(book_id=book_id).first()
        if not book:
            return {'success': False, 'message': '图书不存在', 'code': 200}
        
        return {'success': True, 'data': {
            'book_id': book.book_id,
            'book_name': book.book_name,
            'author': book.author,
            'publisher': book.publisher,
            'category': book.category,
            'total_num': book.total_num,
            'remain_num': book.remain_num,
            'location': book.location,
            'price': book.price,
            'status': book.status if hasattr(book, 'status') else ('在库' if book.remain_num > 0 else '已借出')
        }, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def update_book(book_id, data):
    session = get_session()
    try:
        book = session.query(Book).filter_by(book_id=book_id).first()
        if not book:
            return {'success': False, 'message': '图书不存在', 'code': 200}
        
        if 'book_name' in data:
            book.book_name = data['book_name']
        if 'author' in data:
            book.author = data['author']
        if 'publisher' in data:
            book.publisher = data['publisher']
        if 'category' in data:
            book.category = data['category']
        if 'total_num' in data:
            diff = data['total_num'] - book.total_num
            book.total_num = data['total_num']
            book.remain_num += diff
        if 'location' in data:
            book.location = data['location']
        if 'price' in data:
            book.price = data['price']
        
        session.commit()
        return {'success': True, 'message': '图书信息更新成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def delete_book(book_id):
    session = get_session()
    try:
        book = session.query(Book).filter_by(book_id=book_id).first()
        if not book:
            return {'success': False, 'message': '图书不存在', 'code': 200}
        
        session.delete(book)
        session.commit()
        return {'success': True, 'message': '图书删除成功', 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def list_books(page=1, page_size=100, keyword='', category=''):
    session = get_session()
    try:
        query = session.query(Book)
        if keyword:
            query = query.filter(Book.book_name.like(f'%{keyword}%') | Book.author.like(f'%{keyword}%') | Book.book_id.like(f'%{keyword}%'))
        if category:
            query = query.filter(Book.category == category)
        
        total = query.count()
        books = query.order_by(Book.book_id).offset((page - 1) * page_size).limit(page_size).all()
        
        data = [{
            'book_id': b.book_id,
            'book_name': b.book_name,
            'author': b.author,
            'publisher': b.publisher,
            'category': b.category,
            'total_num': b.total_num,
            'remain_num': b.remain_num,
            'location': b.location
        } for b in books]
        
        return {'success': True, 'data': data, 'total': total, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)
