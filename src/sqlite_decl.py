import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, DateTime
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
    content = Column(Binary, nullable=True)
    downloadTimestamp = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(RawDataArticle.id)).scalar()
        return maxId if not maxId is None else 1


class ArticleCategory(Base):
    __tablename__ = 'article_category'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    media_id = Column(String, nullable=False)
    url = Column(String(250), nullable=False)

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(ArticleCategory.id)).scalar()
        return maxId if not maxId is None else 1


class ArticleCategoryRelationship(Base):
    __tablename__ = 'article_category_relationship'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    cat_from_id = Column(BigInteger, ForeignKey('article_category.id'))
    cat_to_id = Column(BigInteger, ForeignKey('article_category.id'))
    cat_from = relationship(ArticleCategory, foreign_keys=[cat_from_id])
    cat_to = relationship(ArticleCategory, foreign_keys=[cat_to_id])

    @staticmethod
    def getMaxId(session):
        maxId = session.query(func.max(ArticleCategoryRelationship.id)).scalar()
        return maxId if not maxId is None else 1


engine = create_engine('sqlite:///../data/datacollection.db')
Base.metadata.create_all(engine)
