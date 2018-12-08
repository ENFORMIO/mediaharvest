from bs4 import BeautifulSoup

file = open('/Users/gzukrigl/projects/mediaharvest/data/article.22.html', 'r')
content = file.read()

soup = BeautifulSoup(content, 'html.parser')

title = soup.head.title.getText() if soup.head.title is not None else ''
author = None
publishedDate = None
copyrightImage = None
facebookTitle = None
facebookDescription = None
teaser = None
text = None
commenturl = None
retresco = ""
for tag in soup.select('div.c_retresco-story-tags'): # div.retresco-story-tags__taggroup > a'):
    print (tag)
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
#print (teaser)
print ("%s: %s: %s, %s" % (title, author, copyrightImage, retresco))
#print (url.url)
soup = BeautifulSoup(content, 'html.parser')
