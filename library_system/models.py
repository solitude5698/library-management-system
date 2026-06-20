from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from db_util import Base

class User(Base):
    __tablename__ = 'User'
    
    user_id = Column(String(10), primary_key=True)
    password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False)
    reader_id = Column(String(10), ForeignKey('Reader.reader_id'))
    last_login = Column(DateTime)

class Reader(Base):
    __tablename__ = 'Reader'
    
    reader_id = Column(String(10), primary_key=True)
    reader_name = Column(String(20), nullable=False)
    gender = Column(String(1))
    category_code = Column(String(10), ForeignKey('ReaderCategory.category_code'), nullable=False)
    department = Column(String(50))
    phone = Column(String(15))
    reg_date = Column(Date)
    status = Column(String(10))

class Book(Base):
    __tablename__ = 'Book'
    
    book_id = Column(String(15), primary_key=True)
    book_name = Column(String(100), nullable=False)
    author = Column(String(50))
    publisher = Column(String(50))
    pub_date = Column(Date)
    category = Column(String(20))
    total_num = Column(Integer)
    remain_num = Column(Integer)
    location = Column(String(20))

class BorrowRecord(Base):
    __tablename__ = 'BorrowRecord'
    
    borrow_id = Column(String(15), primary_key=True)
    reader_id = Column(String(10), ForeignKey('Reader.reader_id'), nullable=False)
    book_id = Column(String(15), ForeignKey('Book.book_id'), nullable=False)
    borrow_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    fine_amount = Column(Numeric(8, 2))
    status = Column(String(10))

class ReaderCategory(Base):
    __tablename__ = 'ReaderCategory'
    
    category_code = Column(String(10), primary_key=True)
    category_name = Column(String(20), nullable=False)
    max_borrow_num = Column(Integer, nullable=False)
    borrow_days_limit = Column(Integer, nullable=False)
    daily_fine_rate = Column(Numeric(8, 2))

class OperationLog(Base):
    __tablename__ = 'OperationLog'
    
    log_id = Column(Integer, primary_key=True)
    operator_id = Column(String(10), nullable=False)
    operation_type = Column(String(50))
    operation_detail = Column(String(500))
    log_time = Column(DateTime)
