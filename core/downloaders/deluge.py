import logging
import json
import urllib2

from lib.deluge_client import DelugeRPCClient

import core

logging = logging.getLogger(__name__)


class DelugeWeb(object):

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to deluge web ui
        data: dict of deluge server information

        Tests if we can get Deluge's stats using server info in 'data'

        Return True on success or str error message on failure
        '''

        host = data['delugehost']
        port = int(data['delugeport'])
        password = data['delugepass']

        url = url = u'{}:{}/json'.format(host, port)

        data = {}

        data = json.dumps({"method": "auth.login",
                           "params": [password],
                           "id": 1})

        post_data = json.dumps(data).encode('utf-8')

        print data

        try:
            print url
            request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib2.urlopen(request, timeout=60).read()

            print '=========='
            print response
            print '=========='

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            print e
            logging.error(u'Deluge test_connection', exc_info=True)
            return '{}.'.format(e)


class Deluged(object):

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to deluge
        data: dict of deluge server information

        Tests if we can get Deluge's stats using server info in 'data'

        Return True on success or str error message on failure
        '''

        host = data['delugehost']
        port = int(data['delugeport'])
        user = data['delugeuser']
        password = data['delugepass']

        try:
            client = DelugeRPCClient(host, port, user, password)
            client.connect()
            if client.connected:
                return True
            else:
                return 'Unable to connect.'
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            print e
            logging.error(u'Deluge test_connection', exc_info=True)
            return '{}.'.format(e)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to Deluge
        data: dict of torrrent/magnet information

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''

        deluge_conf = core.CONFIG['Deluge']

        host = deluge_conf['delugehost']
        port = deluge_conf['delugeport']
        user = deluge_conf['delugeuser']
        password = deluge_conf['delugepass']

        client = DelugeRPCClient(host, port, user, password)

        url = data['guid']

        options = {}
        options['add_paused'] = deluge_conf['delugeaddpaused'] == 'true'
        category = deluge_conf['delugecategory']

        print client.get_config()  # # TODO FIND DOWNLOAD DIR
        return None

        if data['type'] == 'magnet':
            try:
                download_id = client.add_torrent_magnet(url, options)
                return {'response': 'true', 'downloadid': download_id}
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                print e
                logging.error(u'deluge add_torrent', exc_info=True)
                return {'response': 'false', 'error': str(e)}
        else:
            try:
                download_id = client.add_torrent(url, options)
                return {'response': 'true', 'downloadid': download_id}
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                print e
                logging.error(u'deluge add_torrent', exc_info=True)
                return {'response': 'false', 'error': str(e)}
