import sys
import xmlrpclib
import logging
import settings

from google.appengine.api import urlfetch

class GAEXMLRPCTransport(object):
    """Handles an HTTP transaction to an XML-RPC server."""

    def __init__(self):
        pass

    def request(self, host, handler, request_body, verbose=0):
        result = None
        url = 'http://%s%s' % (host, handler)
        try:
            response = urlfetch.fetch(url,
                                      payload=request_body,
                                      method=urlfetch.POST,
                                      headers={'Content-Type': 'text/xml'})
        except:
            msg = 'Failed to fetch %s' % url
            logging.error(msg)
            raise xmlrpclib.ProtocolError(host + handler, 500, msg, {})

        if response.status_code != 200:
            logging.error('%s returned status code %s' %
                          (url, response.status_code))
            raise xmlrpclib.ProtocolError(host + handler,
                                          response.status_code,
                                          "",
                                          response.headers)
        else:
            result = self.__parse_response(response.content)

        return result

    def __parse_response(self, response_body):
        p, u = xmlrpclib.getparser(use_datetime=False)
        p.feed(response_body)
        return u.close()

def ping():
    for url in settings.PING_LIST:
        try:
            transport = GAEXMLRPCTransport()
            rpc_server = xmlrpclib.ServerProxy(url, transport=transport)
            result = rpc_server.weblogUpdates.ping(settings.SITE_NAME, settings.SITE_DOMAIN)
            if result.get('flerror', False) == True:
                logging.error('Ping error from server: %s' % result.get('message', '(No message in RPC result)'))
            else:
                logging.debug('Ping successful. url:%s'%url)
        except:
            logging.error("Can't ping: %s" % sys.exc_info()[1])