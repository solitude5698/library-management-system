from db_util import get_session, close_session
from models import Reader, Book, BorrowRecord, ReaderCategory, OperationLog
from datetime import date, timedelta
import random

def borrow_book(reader_id, book_id, operator_id=None):
    session = get_session()
    try:
        reader = session.query(Reader).filter_by(reader_id=reader_id).first()
        if not reader:
            return {'success': False, 'message': '读者不存在', 'code': 200}
        
        if reader.status != '正常':
            return {'success': False, 'message': '读者已停借', 'code': 200}
        
        category = session.query(ReaderCategory).filter_by(category_code=reader.category_code).first()
        if not category:
            return {'success': False, 'message': '读者类别配置不存在', 'code': 200}
        
        current_count = session.query(BorrowRecord).filter_by(reader_id=reader_id, status='已借出').count()
        if current_count >= category.max_borrow_num:
            return {'success': False, 'message': f'借书数量已达上限（最多 {category.max_borrow_num} 本）', 'code': 200}
        
        book = session.query(Book).filter_by(book_id=book_id).first()
        if not book:
            return {'success': False, 'message': '图书不存在', 'code': 200}
        
        if book.remain_num <= 0:
            return {'success': False, 'message': '图书已全部借出', 'code': 200}
        
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=category.borrow_days_limit)
        borrow_id = f"BR{date.today().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        record = BorrowRecord(
            borrow_id=borrow_id,
            reader_id=reader_id,
            book_id=book_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status='已借出'
        )
        session.add(record)
        
        book.remain_num -= 1
        
        if operator_id:
            log = OperationLog(
                operator_id=operator_id,
                operation_type='借书',
                operation_detail=f'读者:{reader_id} 借阅图书:{book_id}'
            )
            session.add(log)
        
        session.commit()
        return {
            'success': True,
            'message': f'借书成功！应还日期：{due_date.strftime("%Y-%m-%d")}',
            'borrow_id': borrow_id,
            'borrow_date': borrow_date.strftime('%Y-%m-%d'),
            'due_date': due_date.strftime('%Y-%m-%d'),
            'code': 200
        }
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_borrow_record(borrow_id):
    session = get_session()
    try:
        record = session.query(BorrowRecord).filter_by(borrow_id=borrow_id).first()
        if not record:
            return {'success': False, 'message': '借阅记录不存在', 'code': 200}
        
        book = session.query(Book).filter_by(book_id=record.book_id).first()
        reader = session.query(Reader).filter_by(reader_id=record.reader_id).first()
        
        return {
            'success': True,
            'data': {
                'borrow_id': record.borrow_id,
                'reader_id': record.reader_id,
                'reader_name': reader.reader_name if reader else '',
                'book_id': record.book_id,
                'book_name': book.book_name if book else '',
                'borrow_date': record.borrow_date.strftime('%Y-%m-%d') if record.borrow_date else '',
                'due_date': record.due_date.strftime('%Y-%m-%d') if record.due_date else '',
                'return_date': record.return_date.strftime('%Y-%m-%d') if record.return_date else '',
                'status': record.status,
                'fine_amount': float(record.fine_amount) if record.fine_amount else 0.0
            },
            'code': 200
        }
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_reader_borrow_records(reader_id):
    session = get_session()
    try:
        records = session.query(BorrowRecord).filter_by(reader_id=reader_id).order_by(BorrowRecord.borrow_date.desc()).all()
        
        data = []
        for r in records:
            book = session.query(Book).filter_by(book_id=r.book_id).first()
            data.append({
                'borrow_id': r.borrow_id,
                'reader_id': r.reader_id,
                'book_id': r.book_id,
                'book_name': book.book_name if book else '',
                'borrow_date': r.borrow_date.strftime('%Y-%m-%d') if r.borrow_date else '',
                'due_date': r.due_date.strftime('%Y-%m-%d') if r.due_date else '',
                'status': r.status,
                'fine_amount': float(r.fine_amount) if r.fine_amount else 0.0
            })
        
        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)
