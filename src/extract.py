from sqlalchemy_declarative import Base, RawDataUrl, RawDataArticle, ArticleCategory
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import zip

engine = create_engine('sqlite:///../data/datacollection.db')
Base.metadata.bind = engine

from sqlalchemy.orm import sessionmaker

DBSession = sessionmaker()
session = DBSession()

counter = 0

urls = session.query(RawDataUrl).all()
for url in urls:
    articles = session.query(RawDataArticle).filter(RawDataArticle.rawDataUrl == url).all()
    for article in articles:
        unzipped = zip.unzipped(article.content)
        for name in unzipped:
            htmlContent = unzipped[name]
            soup = BeautifulSoup(htmlContent, 'html.parser')
            title = soup.head.title.getText()
            author = None
            publishedDate = None
            copyrightImage = None
            facebookTitle = None
            facebookDescription = None
            teaser = None
            text = None
            commenturl = None
            for authorline_name in soup.select('div.authorline__name'):
                author = authorline_name.getText()
            for ctime in soup.select('div.c_time'):
                publishedDate = ctime.getText()
            for ccopyright in soup.select('div.c_copyright'):
                copyrightImage = ccopyright.getText()
            for tag in soup.select('meta[property=og:title]'):
                facebookTitle = tag.get('content')
            for tag in soup.select('meta[property=og:description]'):
                facebookDescription = tag.get('content')
            for tag in soup.select('div.c_lead div.c_outer > p'):
                teaser = tag.getText()
            for tag in soup.select('div.c_content'):
                text = tag.getText()

            print (url.url)

            break

        counter += 1
        if counter > 15:
            exit()
