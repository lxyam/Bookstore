from sqlalchemy import Column, String, create_engine, Integer, Text, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import times

class user():
    # 表的名字:
    __tablename__ = 'user'
    # 表的结构:
    user_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    password = Column(String(32), nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String(16))
    terminal = Column(String(16))

class user_store():
    # 表的名字:
    __tablename__ = 'user_store'
    # 表的结构:
    user_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    store_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)

class store():
    # 表的名字:
    __tablename__ = 'store'
    # 表的结构:
    store_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    book_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    book_info = Column(String(50))
    stock_level = Column(Integer)

class new_order():
    # 表的名字:
    __tablename__ = 'new_order'
    # 表的结构:
    order_id = Column(String(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    user_id = Column(String(32))
    store_id = Column(String(32))

class new_order_detail():
    # 表的名字:
    __tablename__ = 'new_order_detail'
    # 表的结构:
    order_id = Column(Stirng(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    book_id = Column(Stirng(32), autoincrement=True, primary_key=True, unique=True, nullable=False)
    count = Column(Integer)
    price = Column(Integer)

