import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func, desc

Base = declarative_base()

class RawDataUrl(Base):
    __tablename__ = 'raw_data_url'
    id = Column(BigInteger, primary_key=True)
    url = Column(String(250), nullable=False)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(RawDataUrl.id)).scalar()
        return maxId if not maxId is None else 1

class RawDataArticle(Base):
    __tablename__ = 'raw_data_article'
    id = Column(BigInteger, primary_key=True)
    rawDataUrl_id = Column(BigInteger, ForeignKey('raw_data_url.id'))
    rawDataUrl = relationship(RawDataUrl)
    path = Column(String(250), nullable=True)
    downloadTimestamp = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(RawDataArticle.id)).scalar()
        return maxId if not maxId is None else 1

#engine = create_engine('sqlite:///../data/datacollection.db')
engine = create_engine('mysql+pymysql://mediaharvest:pwd12@localhost/mediaharvest')
Base.metadata.create_all(engine)
