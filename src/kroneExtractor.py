from extractor import Extractor
from bs4 import BeautifulSoup
import json

class KroneExtractor(Extractor):
    def __init__(self, content):
        super(KroneExtractor,self).__init__(content)
        self._ressorts = None
        self._parentRessorts = None
        self._soup = BeautifulSoup(content, 'html.parser')

    def getTitle(self):
        if self._soup.head is None or \
           self._soup.head.title is None:
            return ''
        return self._soup.head.title.getText().strip()

    def getTopics(self):
        topics = []
        for tag in self._soup.select('div.c_retresco-story-tags div.retresco-story-tags__taggroup > a'):
            topic = tag.getText().strip()
            if (topic not in topics):
                topics.append(topic)
        return topics

    def getAuthor(self):
        author = None
        for authorline_name in self._soup.select('div.authorline__name'):
            author = authorline_name.getText()
        return author

    def getPublishedDate(self):
        publishedDate = None
        for ctime in self._soup.select('div.c_time'):
            publishedDate = ctime.getText()
        return publishedDate

    def getCopyrightImage(self):
        copyrightImage = None
        for ccopyright in self._soup.select('div.c_copyright'):
            copyrightImage = ccopyright.getText()
        return copyrightImage

    def getOgTitle(self):
        ogTitle = None
        for tag in self._soup.select('meta[property=og:title]'):
            ogTitle = tag.get('content')
        return ogTitle

    def getOgDescription(self):
        ogDescription = None
        for tag in self._soup.select('meta[property=og:description]'):
            ogDescription = tag.get('content')
        return ogDescription

    def getTeaser(self):
        teaser = None
        for tag in self._soup.select('div.c_lead div.c_outer > p'):
            teaser = tag.getText()
        return teaser

    def getText(self):
        text = None
        for tag in self._soup.select('div.c_content'):
            text = tag.getText()
        return text

    def parseRessorts(self):
        if self._ressorts is not None and \
           self._parentRessorts is not None:
           return

        ressortIds = []
        ressortNames = []
        parentRessortIds = []
        parentRessortNames = []
        for line in self._soup.prettify().splitlines():
            if "window.kmmObjectRessorts = " in line:
                startPos = line.find('[')
                endPos = line.rfind(']') + 1
                jsonTxt = line[startPos : endPos]
                jsonArr = json.loads(jsonTxt)
                for jsonObj in jsonArr:
                    ressortId = jsonObj['id']
                    if ressortId not in ressortIds:
                        ressortIds.append(ressortId)
                    parentRessortId = jsonObj['parent']
                    if parentRessortId not in parentRessortIds and parentRessortId != 0:
                        parentRessortIds.append(parentRessortId)
        for ressortId in ressortIds:
            for tag in self._soup.select('div.c_navi-link div[data-ressort_id=%s] > a' % ressortId):
                ressortName = tag.getText().strip()
                if ressortName not in ressortNames:
                    ressortNames.append(tag.getText().strip())
        for ressortId in parentRessortIds:
            for tag in self._soup.select('div.c_navi-link div[data-ressort_id=%s] > a' % ressortId):
                ressortName = tag.getText().strip()
                if ressortName not in parentRessortNames:
                    parentRessortNames.append(tag.getText().strip())
        self._ressorts = ressortNames
        self._parentRessorts = parentRessortNames

    def getRessorts(self):
        self.parseRessorts()
        return self._ressorts

    def getMainRessorts(self):
        self.parseRessorts()
        return self._parentRessorts
