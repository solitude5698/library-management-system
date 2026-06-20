from db_util import get_session, close_session
from models import Book, BorrowRecord, Reader, ReaderCategory
from datetime import date, timedelta
from sqlalchemy import func
from collections import Counter

def search_books(keyword):
    session = get_session()
    try:
        query = session.query(Book).filter(
            Book.book_name.like(f'%{keyword}%') |
            Book.author.like(f'%{keyword}%') |
            Book.book_id.like(f'%{keyword}%')
        )
        books = query.order_by(Book.book_name).all()

        data = [{
            'book_id': b.book_id,
            'book_name': b.book_name,
            'author': b.author,
            'publisher': b.publisher,
            'category': b.category,
            'total_num': b.total_num,
            'remain_num': b.remain_num
        } for b in books]

        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_hot_books(top=5):
    session = get_session()
    try:
        results = session.query(
            Book.book_id,
            Book.book_name,
            Book.author,
            func.count(BorrowRecord.borrow_id).label('borrow_times')
        ).join(BorrowRecord, Book.book_id == BorrowRecord.book_id
        ).group_by(Book.book_id, Book.book_name, Book.author
        ).order_by(func.count(BorrowRecord.borrow_id).desc()
        ).limit(top).all()

        data = [{
            'book_id': r.book_id,
            'book_name': r.book_name,
            'author': r.author,
            'borrow_times': r.borrow_times
        } for r in results]

        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_borrow_trend(days=30):
    session = get_session()
    try:
        start_date = date.today() - timedelta(days=days)
        results = session.query(BorrowRecord.borrow_date).filter(
            BorrowRecord.borrow_date >= start_date
        ).all()

        date_counts = Counter([str(r[0]) for r in results])
        data = [{'date': d, 'borrow_count': c} for d, c in sorted(date_counts.items())]

        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_category_stats():
    session = get_session()
    try:
        results = session.query(
            Book.category,
            func.count(Book.book_id).label('book_count'),
            func.sum(Book.total_num).label('total_copy_count')
        ).outerjoin(BorrowRecord, Book.book_id == BorrowRecord.book_id
        ).group_by(Book.category).all()

        data = [{
            'category': r.category or '未分类',
            'book_count': r.book_count,
            'total_copy_count': r.total_copy_count or 0
        } for r in results]

        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)
