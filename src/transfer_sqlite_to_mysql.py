import decl
import sqlalchemy_declarative
import sqlalchemy
from sqlalchemy_declarative import ArticleCategory, Base, ArticleCategoryRelationship, RawDataUrl, RawDataArticle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


sqlite_engine = create_engine('sqlite:///../data/datacollection.db')
sqlalchemy_declarative.Base.metadata.bind = sqlite_engine
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite = SqliteSession()

mysql_engine = create_engine('mysql+pymysql://mediaharvest:pwd12@localhost/mediaharvest')
decl.Base.metadata.bind = mysql_engine
MysqlSession = sessionmaker(bind=mysql_engine)
mysql = MysqlSession()
for url in sqlite.query(sqlalchemy_declarative.RawDataUrl).all():
    raw_data_url = decl.RawDataUrl()
    raw_data_url.url = url.url
    raw_data_url.id = url.id
    mysql.add(raw_data_url)
    mysql.commit()

for article in sqlite.query(sqlalchemy_declarative.RawDataArticle).all():
    # store file into filesystem
    filename = '../data/files/%s/%s.zip' % (article.downloadTimestamp.date().isoformat(), article.id)
    ensure_dir(filename)
    file = open(filename, 'wb')
    file.write(article.content)
    file.close()
    # store dataset into database
    raw_data_article = decl.RawDataArticle()
    raw_data_article.id = article.id
    raw_data_article.rawDataUrl_id = article.rawDataUrl_id
    raw_data_article.path = filename
    raw_data_article.downloadTimestamp = article.downloadTimestamp
    mysql.add(raw_data_article)
    mysql.commit()
