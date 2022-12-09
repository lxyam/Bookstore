from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

import psycopg2

class db():
    def __init__(self):
        self.engine = create_engine("postgresql://stu10205501425:Stu10205501425@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10205501425", 
                                echo=True,
                                pool_size=8, 
                                pool_recycle=60*30
                                )
        Base = declarative_base()
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()