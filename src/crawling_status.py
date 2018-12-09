from sqlite_decl import Base, RawDataUrl, RawDataArticle, ArticleCategory
from sqlalchemy import create_engine

import zip

#engine = create_engine('sqlite:///../data/datacollection.db')
engine = create_engine('sqlite:///../data/2018-12-08-enformio.db')
Base.metadata.bind = engine

from sqlalchemy.orm import sessionmaker

DBSession = sessionmaker()
session = DBSession()

cats = session.query(ArticleCategory).all()
print ("%s category pages" % len(cats))
urls = session.query(RawDataUrl).all()
print ("%s urls" % len(urls))
articles = session.query(RawDataArticle).all()
print ("%s articles" % len(articles))

#for article in articles:
#    f = open('../data/krone.at/%s.zip' % article.id, 'wb')
#    f.write(article.content)
#    f.close()



#for article in articles:
#    zipped = zip.zipped(article.content, str(article.id) + '.html')
#    article.content = zipped
#    session.commit()
