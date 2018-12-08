import zip
from bs4 import BeautifulSoup
import urllib
import json
from kroneExtractor import KroneExtractor

url = 'https://www.krone.at/1813319'
localfile = '/Users/gzukrigl/projects/mediaharvest/data/article.%s.html'

content = urllib.request.urlopen(url)

topics = []

#try:
extractor = KroneExtractor(content)
title = extractor.getTitle()
topics.extend(extractor.getTopics())
author = extractor.getAuthor()
publishedDate = extractor.getPublishedDate()
copyrightImage = extractor.getCopyrightImage()
facebookTitle = extractor.getOgTitle()
facebookDescription = extractor.getOgDescription()
teaser = extractor.getTeaser()
text = extractor.getText()
ressorts = extractor.getRessorts()
parentRessorts = extractor.getMainRessorts()
#except:
    #print ("Error Parsing %s (%s)" % (url, 4711))

print ('"%s"|"%s"|"%s"|"%s"|"%s"|"%s"|"%s"' % (url,
                     title,
                     author,
                     publishedDate,
                     str(topics),
                     str(ressorts),
                     str(parentRessorts)
                     ))
exit()
soup = BeautifulSoup(content, 'html.parser')
content = soup.prettify()

file = open(localfile % 1, 'w')
file.write(content)
file.close()

zipped = zip.zipped(content, 'article.html')

file = open((localfile % 3) + '.zip', 'wb')
file.write(zipped)
file.close()

unzipped = zip.unzipped(zipped)
htmlContent = unzipped['article.html'].decode('utf-8')
file = open(localfile % 2, 'w')
file.write(htmlContent)
file.close()

soup2 = BeautifulSoup(htmlContent, 'html.parser')
#for tag in soup2.select('div.c_retresco-story-tags div.retresco-story-tags__taggroup > a'):
#    print ("%s: %s" % (tag.getText().strip(), tag.get('href')))
#    #print (tag)


ressortIds = []
ressortNames = []
parentRessortIds = []
parentRessortNames = []

for line in soup2.prettify().splitlines():
    if "window.kmmObjectRessorts = " in line: # and "function" not in line:
        startPos = line.find('[')
        endPos = line.rfind(']') + 1
        jsonTxt = line[startPos : endPos]
        print(jsonTxt)
        jsonArr = json.loads(jsonTxt)
        for jsonObj in jsonArr:
            ressortId = jsonObj['id']
            if ressortId not in ressortIds:
                ressortIds.append(ressortId)
            parentRessortId = jsonObj['parent']
            if parentRessortId not in parentRessortIds and parentRessortId != 0:
                parentRessortIds.append(parentRessortId)

print (ressortIds)
print (parentRessortIds)


for ressortId in ressortIds:
    for tag in soup2.select('div.c_navi-link div[data-ressort_id=%s] > a' % ressortId):
        ressortName = tag.getText().strip()
        if ressortName not in ressortNames:
            ressortNames.append(tag.getText().strip())

for ressortId in parentRessortIds:
    for tag in soup2.select('div.c_navi-link div[data-ressort_id=%s] > a' % ressortId):
        ressortName = tag.getText().strip()
        if ressortName not in parentRessortNames:
            parentRessortNames.append(tag.getText().strip())

print (ressortNames)
print (parentRessortNames)


#for tag in soup2.select('div.c_navbar div.c_navi-link div.c_active'):
#    print (tag)
