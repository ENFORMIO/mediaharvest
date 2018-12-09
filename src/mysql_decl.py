import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, DateTime, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func, desc

Base = declarative_base()

class MediaSite(Base):
    __tablename__ = 'media_site'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(250), nullable=False)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(MediaSite.id)).scalar()
        return maxId if not maxId is None else 1


class RawDataUrl(Base):
    __tablename__ = 'raw_data_url'
    id = Column(BigInteger, primary_key=True)
    url = Column(String(250), nullable=False)
    media_site_id = Column(BigInteger, ForeignKey('media_site.id'))
    mediaSite = relationship(MediaSite)

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


class ArticleExtract(Base):
    __tablename__ = 'article_extract'
    id = Column(BigInteger, primary_key=True)
    version = Column(Integer, default=0)
    rawDataUrl_id = Column(BigInteger, ForeignKey('raw_data_url.id'))
    rawDataUrl = relationship(RawDataUrl)
    rawDataArticle_id = Column(BigInteger, ForeignKey('raw_data_article.id'))
    rawDataArticle = relationship(RawDataArticle)
    title = Column(String(250), nullable=True)
    author = Column(String(250), nullable=True)
    ogTitle = Column(String(250), nullable=True)
    ogDescription = Column(Text, nullable=True)
    teaser = Column(Text, nullable=True)
    text = Column(Text(4294000000), nullable=True)
    topics = Column(String(250), nullable=True)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(ArticleExtract.id)).scalar()
        return maxId if not maxId is None else 1
"""

class TopicDimension(Base):
    __tablename__ = 'topic_dimension'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(250), nullable=True)
    media_site_id = Column(BigInteger, ForeignKey('media_site.id'))
    mediaSite = relationship(MediaSite)

class Topic(Base):
    __tablename__ = 'topic'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(250), nullable=True)
    topic_dimesion_id = Column(BigInteger, ForeignKey('topic_dimension.id'))
    topicDimension = relationship(TopicDimension)


topic_article_extract_association = Table('topic_article_association', Base.metadata,
    Column('topic_id', BigInteger, ForeignKey('topic.id')),
    Column('article_extract_id', BigInteger, ForeignKey('article_extract.id'))
)
"""


#engine = create_engine('sqlite:///../data/datacollection.db')
engine = create_engine('mysql+pymysql://mediaharvest:pwd12@localhost/mediaharvest')
Base.metadata.create_all(engine)
