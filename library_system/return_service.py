from db_util import get_session, close_session
from models import BorrowRecord, Book, Reader, ReaderCategory, OperationLog
from datetime import date

def return_book(borrow_id, operator_id=None):
    session = get_session()
    try:
        record = session.query(BorrowRecord).filter_by(borrow_id=borrow_id).first()
        if not record:
            return {'success': False, 'message': '借阅记录不存在', 'code': 200}
        
        if record.status == '已归还':
            return {'success': False, 'message': '该图书已归还', 'code': 200}
        
        # 获取读者类别的罚款费率
        reader = session.query(Reader).filter_by(reader_id=record.reader_id).first()
        daily_fine_rate = 1.0  # 默认罚款费率
        if reader and reader.category_code:
            category = session.query(ReaderCategory).filter_by(category_code=reader.category_code).first()
            if category and category.daily_fine_rate:
                daily_fine_rate = float(category.daily_fine_rate)
        
        return_date = date.today()
        fine = 0.0
        message = '还书成功！'
        
        if return_date > record.due_date:
            overdue_days = (return_date - record.due_date).days
            fine = overdue_days * daily_fine_rate
            message = f'还书成功！超期 {overdue_days} 天，罚款 {fine:.2f} 元'
        
        record.return_date = return_date
        record.fine_amount = fine
        record.status = '超期' if fine > 0 else '已归还'
        
        book = session.query(Book).filter_by(book_id=record.book_id).first()
        if book:
            book.remain_num += 1
        
        if operator_id:
            log = OperationLog(
                operator_id=operator_id,
                operation_type='还书',
                operation_detail=f'流水号:{borrow_id} 罚款:{fine:.2f}元'
            )
            session.add(log)
        
        session.commit()
        return {'success': True, 'message': message, 'code': 200}
    except Exception as e:
        session.rollback()
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def calculate_fine(borrow_id):
    session = get_session()
    try:
        record = session.query(BorrowRecord).filter_by(borrow_id=borrow_id).first()
        if not record:
            return {'success': False, 'message': '借阅记录不存在', 'code': 200}
        
        return_date = date.today()
        fine = 0.0
        overdue_days = 0
        
        if return_date > record.due_date:
            overdue_days = (return_date - record.due_date).days
            fine = overdue_days * 1.0
        
        return {
            'success': True,
            'data': {
                'borrow_id': record.borrow_id,
                'due_date': record.due_date.strftime('%Y-%m-%d') if record.due_date else '',
                'overdue_days': overdue_days,
                'fine_amount': fine
            },
            'code': 200
        }
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)

def get_overdue_records():
    session = get_session()
    try:
        today = date.today()
        records = session.query(BorrowRecord).filter(
            BorrowRecord.status == '已借出',
            BorrowRecord.due_date < today
        ).all()
        
        data = []
        for r in records:
            book = session.query(Book).filter_by(book_id=r.book_id).first()
            reader = session.query(Reader).filter_by(reader_id=r.reader_id).first()
            overdue_days = (today - r.due_date).days
            data.append({
                'borrow_id': r.borrow_id,
                'reader_id': r.reader_id,
                'reader_name': reader.reader_name if reader else '',
                'book_id': r.book_id,
                'book_name': book.book_name if book else '',
                'due_date': r.due_date.strftime('%Y-%m-%d') if r.due_date else '',
                'overdue_days': overdue_days
            })
        
        return {'success': True, 'data': data, 'code': 200}
    except Exception as e:
        return {'success': False, 'message': str(e), 'code': 200}
    finally:
        close_session(session)
