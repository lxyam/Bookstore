import logging
import os
import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, Date, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import time

class Store:
    database: str

    def __init__(self, db_path):
        self.engine = create_engine("postgresql://stu10205501425:Stu10205501425@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10205501425", 
                                echo=True,
                                pool_size=8, 
                                pool_recycle=60*30
                                )
        self.init_tables()

    def init_tables(self):
        try:
            conn, Base = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id TEXT , PRIMARY KEY(store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, stock_level INTEGER, price INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, "
                "status INTEGER DEFAULT 1, total_price INTEGER, order_time INTEGER )"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS invert_index( "
                "search_key TEXT, search_id serial, book_id TEXT, "
                "book_title TEXT, book_author TEXT, "
                "PRIMARY KEY(search_key, search_id))"
            )
            conn.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):
        self.Base = declarative_base()
        self.metadata = MetaData()
        self.DBSession = sessionmaker(bind=self.engine)
        self.conn = self.DBSession()
        return self.conn, self.Base


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
