import urllib.parse
import urllib.request
import urllib.error
import ssl
import xml.etree.ElementTree as ET

start_url = 'https://www.krone.at/sitemap.xml'

f = urllib.request.urlopen(start_url)
sitemap_xml = f.read()
sitemapindex = ET.fromstring(sitemap_xml)

sitemaps = []
for sitemap in sitemapindex:
    for loc in sitemap:
        if 'loc' in loc.tag:
            sitemaps.append(loc.text)

print ("found %s sitemaps in first attempt")

urls = []
for sitemap in sitemaps:
    print ("----------------------------------------")
    print ("found %s urls" % len(urls))
    print ("sitemap %s" % sitemap)
    print ("----------------------------------------")
    f = urllib.request.urlopen(sitemap)
    urlset_xml = f.read()
    urlset = ET.fromstring(urlset_xml)
    for url in urlset:
        for loc in url:
            if 'loc' in loc.tag:
                #print (loc.text)
                urls.append(loc.text)

f = open('../../data/krone-sitemap-urls.txt', 'w')
for url in urls:
    f.writeline(url)
f.close()
