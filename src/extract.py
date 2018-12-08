from sqlite_decl import Base, RawDataUrl, RawDataArticle, ArticleCategory
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import zip

from kroneExtractor import KroneExtractor

"""
    Auswertung 1:
        jeweils erster Datensatz:
            * Url
            * title
            * authorline
            * publishedDate
            * commentAnzahl
            * Aehnliche Themen
            * Kategorie inkl. Haupt- und Nebenkategorie
"""

#engine = create_engine('sqlite:///../data/datacollection.db')
#engine = create_engine('sqlite:///../Users/gzukrigl/NAS/gzukrigl/projects/mediaharvest/data/datacollection.old.db')
engine = create_engine('sqlite:///../data/datacollection.old.db')
Base.metadata.bind = engine

from sqlalchemy.orm import sessionmaker

DBSession = sessionmaker()
session = DBSession()

counter = 0

urls = session.query(RawDataUrl).all()
for url in urls:
    counter = 0

    title = None
    author = None
    publishedDate = None
    copyrightImage = None
    facebookTitle = None
    facebookDescription = None
    teaser = None
    text = None
    commenturl = None
    topics = []
    ressorts = []
    parentRessorts = []

    articles = session.query(RawDataArticle).filter(RawDataArticle.rawDataUrl == url).all()
    for article in articles:
        unzipped = zip.unzipped(article.content)
        for name in unzipped:
            htmlContent = unzipped[name].decode('utf-8')

            try:
                extractor = KroneExtractor(htmlContent)
                title = extractor.getTitle()
                topics.extend(extractor.getTopics())
                author = extractor.getAuthor()
                publishedDate = extractor.getPublishedDate()
                copyrightImage = extractor.getCopyrightImage()
                facebookTitle = extractor.getOgTitle()
                facebookDescription = extractor.getOgDescription()
                teaser = extractor.getTeaser()
                text = extractor.getText()
                ressorts.extend(extractor.getRessorts())
                parentRessorts.extend(extractor.getMainRessorts())
            except:
                pass
    print ('"%s"|"%s"|"%s"|"%s"|"%s"|"%s"|"%s"' % (url.url,
                         title,
                         author,
                         publishedDate,
                         str(topics),
                         str(ressorts),
                         str(parentRessorts)
                         ))
