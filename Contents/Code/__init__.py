####################################################################################################
#                                                                                                  #
#                                   TestURL (Plex Channel)                                         #
#                                                                                                  #
####################################################################################################

TITLE = 'URL Test'
PREFIX = '/applications/testurl'

ICON = 'icon-default.png'
SEARCH_ICON = 'icon-search.png'

####################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = R(ICON)
    PopupDirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

    Log('*' * 80)
    Log(u'* Platform.OS               = {0}'.format(Platform.OS))
    Log(u'* Platform.OSVersion        = {0}'.format(Platform.OSVersion))
    Log(u'* Platform.CPU              = {0}'.format(Platform.CPU))
    Log(u'* Platform.ServerVersion    = {0}'.format(Platform.ServerVersion))
    Log('*' * 80)


####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON)
def MainMenu():

    Log(u'* Client.Product            = {0}'.format(Client.Product))
    Log(u'* Client.Platform           = {0}'.format(Client.Platform))
    Log(u'* Client.Version            = {0}'.format(Client.Version))
    Log('*' * 80)

    oc = ObjectContainer(no_cache=True)

    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', summary='Test input URL',
        prompt='Input Test URL:', thumb=R('icon-search.png')
        ))
    oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):

    url = query.strip().replace(' ', '%20')
    if url.startswith('uss/'):
        pass
    elif not url.startswith('http'):
        url = 'http://' + url
    elif url.startswith('//'):
        url = 'http:' + url
    elif url.startswith('/'):
        url = 'http:/' + url

    oc = ObjectContainer(title2=u"TEST URL = {0}".format(url))
    oc.add(PopupDirectoryObject(
        key=Callback(FrameworkTest, url=url), title='URL Framework Test',
        tagline=u"Test open '{0}' within Plex's Framework".format(url),
        summary=u"Open '{0}' within Plex's Framework. Will return 'Pass/Fail' message. Option from Prefs to dump page contents into Log file.".format(url),
        ))
    oc.add(PopupDirectoryObject(
        key=Callback(ServiceCodeTest, url=url), title='URL Video Test',
        tagline=u"Return '{0}' Service Code".format(url),
        summary=u"Return playable video stream for '{0}' if available.".format(url)
        ))

    return oc

####################################################################################################
@route(PREFIX + '/framework')
def FrameworkTest(url):
    """Try opening input url within Plex's Framework. Return 'Pass/Fail' status."""

    try:
        r = HTTP.Request(url, immediate=True, cacheTime=0)
        if Prefs['add_page']:
            try:
                Log(u"Headers for '{0}' >>>\n{1}".format(url, r.headers))
                Log(r.content)
            except:
                Log.Exception(u"Error logging page info for '{0}'".format(url))
        message = u"PASS: URL can open within Plex's Framework. {0}".format(url)
    except:
        Log.Exception(u"Cannot access '{0}' >>>".format(url))
        message = u"FAIL: URL cannot open within Plex's Framework. {0}".format(url)

    return ObjectContainer(header="Framework Test", message=message)

####################################################################################################
@route(PREFIX + '/servicecodetest')
def ServiceCodeTest(url):
    """
    Return input url's Service Code if available (can play video from here),
    or return error status.
    """

    oc = ObjectContainer(title2="URL ServiceCode Test")
    header = "ServiceCode Test"
    if URLService.ServiceIdentifierForURL(url):
        try:
            oc.add(URLService.MetadataObjectForURL(url))
        except:
            Log.Exception(u"Error accessing '{0}' >>>".format(url))
            oc.header = header
            oc.message = "Warning: ServiceCode exists, but Media may be offline."
    else:
        oc.header = header
        oc.message = u"Error: No URL ServiceCode exists for '{0}'".format(url)
    return oc
