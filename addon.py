# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys
import xbmcplugin, xbmcgui, xbmcaddon
import xml.etree.ElementTree as ET

def addLink(title, url, picture):
    if picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultAudio.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultAudio.png', thumbnailImage=picture)
    item.setInfo(type='Audio', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)

def addDir(title, url, mode, picture, page=None):
    if picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=picture)
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    if page != None :
        sys_url += '&page=' + str(page)
    item.setInfo(type='Audio', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def getAudios(url, page=1):
    html = getHTML(url)
    root = ET.fromstring(html)
    count = 20
    index = 0
    addDir('<< Главная', url, None, None, 1)
    for item in root.find('channel').findall('item'):
        try:
            if index >= ((int(page)-1) * count):
                image = item.find('itunes:image', namespaces={'itunes': 'http://www.itunes.com/DTDs/Podcast-1.0.dtd'}).get('href')
                link = item.find('enclosure').get('url')
                title = item.find('title').text
                addLink(title.replace('&quot;', '"'), link, image)
            index += 1
            if index >= (int(page) * count) + count:
                addDir('Вперёд >>', url, 10, None, int(page) + 1)
                break
        except:
            pass

def getChannels(url):
    html = getHTML(url)
    links = re.compile('<div class="title"><a amber="community:\d*" href="(.+?)">(.+?)</a></div>').findall(html)
    images = re.compile('<img src="(.+?)" width="100" height="100" amber="community:\d*" class="avatar">').findall(html)
    addDir('<< Главная', url, None, None, 1)
    try:
        for index in range(0, len(images)):
            addDir(links[index][1].replace('&quot;', '"'), links[index][0] + 'rss.xml', 10, images[index])
        nextLink = re.compile('href="(.+?)"  id="next_page"').findall(html)
        addDir('Следующая страница >>', 'http://rpod.ru' + nextLink[0], 5, None)
    except:
        pass

def getMainMenu():
    addDir('Каналы', 'http://rpod.ru/channels/', 5, None)
    addDir('Подкасты', 'http://rpod.ru/podcasts/?sortby=last', 5, None)

def getHTML(url):
    proxy_url = xbmcplugin.getSetting(int(sys.argv[1]), 'proxy_url')
    proxy_port = xbmcplugin.getSetting(int(sys.argv[1]), 'proxy_port')
    proxy_type = xbmcplugin.getSetting(int(sys.argv[1]), 'proxy_type')
    if proxy_url != '' and proxy_url != None:
        if proxy_type == 'HTTPS': type = 'https'
        if proxy_type == 'SOCKS': type = 'socks'
        else: type = 'http'
        us_proxy = type + "://" + proxy_url + ":" + proxy_port
        proxy_handler = urllib2.ProxyHandler({type: us_proxy})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    html = conn.read()
    conn.close()
    return html

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

params = get_params()
url = None
title = None
mode = None
page = 1

try:
    title = urllib.unquote_plus(params['title'])
except:
    pass
try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:
    page = int(params['page'])
except:
    pass

if mode == None:
    getMainMenu()
elif mode == 5:
    getChannels(url)
elif mode == 10:
    getAudios(url, page)

xbmcplugin.endOfDirectory(int(sys.argv[1]))