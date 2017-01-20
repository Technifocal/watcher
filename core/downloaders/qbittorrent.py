import logging
import urllib
import urllib2
import hashlib

from lib import bencode

import core

logging = logging.getLogger(__name__)


class QBittorrent(object):

    cookie = None
    retry = False

    @staticmethod
    def test_connection(data):
        ''' Tests connectivity to qbittorrent
        data: dict of qbittorrent server information

        Return True on success or str error message on failure
        '''

        host = data['qbittorrenthost']
        port = data['qbittorrentport']
        user = data['qbittorrentuser']
        password = data['qbittorrentpass']

        url = u'{}:{}/'.format(host, port)

        return QBittorrent.login(url, user, password)

    @staticmethod
    def add_torrent(data):
        ''' Adds torrent or magnet to qbittorrent
        data: dict of torrrent/magnet information

        Returns dict {'response': 'true', 'download_id': 'id'}
                     {'response': 'false', 'error': 'exception'}

        '''

        qbit_conf = core.CONFIG['QBittorrent']

        host = qbit_conf['qbittorrenthost']
        port = qbit_conf['qbittorrentport']
        base_url = '{}:{}/'.format(host, port)

        post_data = {}
        user = qbit_conf['qbittorrentuser']
        password = qbit_conf['qbittorrentpass']

        print user
        print password

        post_data['urls'] = data['torrentfile']

        if qbit_conf['qbittorrentaddpaused'] == 'true':
            post_data['state'] = u'pausedDL'
        # bandwidthPriority = qbit_conf['qbittorrentpriority']
        post_data['category'] = qbit_conf['qbittorrentcategory']

        # priority_keys = {
        #     'Low': '0',
        #     'Normal': '1',
        #     'High': '2'
        # }

        # bandwidthPriority = priority_keys[qbit_conf['qbittorrentpriority']]
        #
        # download_dir = None
        # if category:
        #     d = client.get_session().__dict__['_fields']['download_dir'][0]
        #     d_components = d.split('/')
        #     d_components.append(category)
        #
        #     download_dir = '/'.join(d_components)

        if QBittorrent.cookie is None:
            response = QBittorrent.login(base_url, user, password)
            if response == u'Fails.':
                return {'response': 'false', 'error': 'Incorrect usename or password'}

        req_url = u'{}command/download'.format(base_url)
        post_data = urllib.urlencode(post_data)
        request = urllib2.Request(req_url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', QBittorrent.cookie)

        try:
            urllib2.urlopen(request)  # QBit returns an empty string
            downloadid = QBittorrent._get_hash(data['torrentfile'])
            QBittorrent.retry = False

            # TODO pause

            return {'response': 'true', 'downloadid': downloadid}
        except (SystemExit, KeyboardInterrupt):
            raise
        except urllib2.HTTPError as err:
            if QBittorrent.retry is True:
                QBittorrent.retry = False
                return {'response': 'false', 'error': str(err)}
            else:
                QBittorrent.cookie = None
                QBittorrent.retry = True
                return QBittorrent.add_torrent(data)
        except Exception, e:
            logging.error(u'qbittorrent test_connection', exc_info=True)
            return {'response': 'false', 'error': str(e.reason)}

    @staticmethod
    def get_torrents(base_url):
        url = u'{}query/torrents'.format(base_url)
        request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        request.add_header('cookie', QBittorrent.cookie)
        return urllib2.urlopen(request).read()

    @staticmethod
    def login(url, username, password):

        data = {'username': username,
                'password': password
                }

        post_data = urllib.urlencode(data)

        url = u'{}login'.format(url)
        request = urllib2.Request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urllib2.urlopen(request)
            QBittorrent.cookie = response.headers.get('Set-Cookie')
            response = response.read()

            if response == 'Ok.':
                return True
            elif response == 'Fails.':
                return u'Incorrect usename or password'
            else:
                return response

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logging.error(u'qbittorrent test_connection', exc_info=True)
            return u'{}.'.format(str(e.reason))

    @staticmethod
    def _get_hash(url, mode='torrent'):
        if url.startswith('magnet'):
            return url.split('&')[0].split(':')[-1]
        else:
            try:
                req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                torrent = urllib2.urlopen(req).read()
                metadata = bencode.bdecode(torrent)
                hashcontents = bencode.bencode(metadata['info'])
                return hashlib.sha1(hashcontents).hexdigest()
            except Exception, e: #noqa
                return None


'''
{
u'category': u'Watcher',
u'num_incomplete': -1,
u'num_complete': -1,
u'force_start': False,
u'hash': u'e1e8bc80e9e34547661d16f03d10756421d8278c',
u'name': u'Toy Story 3 (BDrip 1080p ENG-ITA DTS) X264 bluray (2010)',
u'completion_on': 4294967295L,
u'super_seeding': False,
u'seq_dl': False,
u'num_seeds': 0,
u'upspeed': 0,
u'priority': 1,
u'state': u'pausedDL',
u'eta': 8640000,
u'added_on': 1484858904,
u'save_path': u'C:\\Users\\Steven\\Downloads\\',
u'num_leechs': 0,
u'progress': 0,
u'size': 0,
u'dlspeed': 0,
u'ratio': 0
}
'''
