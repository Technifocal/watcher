import json
import logging
import urllib2

import core

logging = logging.getLogger(__name__)

test_url = 'http://mxq:5060/torrentpotato/thepiratebay?passkey=135fdfdfd895c1ef9ceba603d2dd8ba1&t=movie&imdbid=tt3748528'


class TorrentPotato(object):

    def __init__(self):
        return

    def search_all(self, imdbid):
        ''' Search all TorrentPotato providers
        imdbid: str imdb id #

        Returns list of dicts with movie info
        '''

        indexers = core.CONFIG['TorIndexers'].values()
        results = []
        self.imdbid = imdbid

        for indexer in indexers:
            if indexer[2] == u'false':
                continue
            url = indexer[0]
            if url[-1] == u'/':
                url = url[:-1]
            passkey = indexer[1]

            search_string = u'{}?passkey={}&t=movie&imdbid={}'.format(url, passkey, imdbid)
            logging.info(u'SEARCHING: {}?passkey=PASSKEY&t=movie&imdbid={}'.format(url, imdbid))

            request = urllib2.Request(search_string, headers={'User-Agent': 'Mozilla/5.0'})

            try:
                torrent_results = json.loads(urllib2.urlopen(request, timeout=60).read())['results']
                for i in torrent_results:
                    results.append(i)

            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e: # noqa
                logging.error(u'TorrentPotato search_all.', exc_info=True)

        if results:
            return self.parse_torrent_potato(results)
        else:
            return []

    def parse_torrent_potato(self, results):
        ''' Sorts and correct keys in results.
        results: list of dicts of results

        Renames, corrects, and adds missing keys

        Returns list of dicts of results
        '''
        item_keep = ('size', 'category', 'pubdate', 'title', 'indexer', 'info_link', 'guid', 'torrentfile', 'resolution', 'type')

        for result in results:
            result['size'] = result['size'] * 1024 * 1024
            result['category'] = result['type']
            result['pubdate'] = None
            result['title'] = result['release_name']
            result['indexer'] = result['torrent_id'].split('/')[2]
            result['info_link'] = result['details_url']
            if result['download_url'].startswith('magnet'):
                guid = result['download_url']
                result['guid'] = guid
                result['type'] = 'magnet'

            else:
                result['guid'] = result['torrentfile'] = result['download_url']
                result['type'] = 'torrent'
            result['resolution'] = self.get_resolution(result)

            for i in result.keys():
                if i not in item_keep:
                    del result[i]

            result['status'] = u'Available'
            result['score'] = 0
            result['downloadid'] = None

        return results

    def get_resolution(self, result):
        ''' Parses release resolution from newznab category or title.
        :param result: dict of individual search result info

        Helper function for make_item_dict()

        Returns str resolution.
        '''

        title = result['title']
        if '4K' in title or 'UHD' in title or '2160P' in title:
            resolution = u'4K'
        elif '1080' in title:
            resolution = u'1080P'
        elif '720' in title:
            resolution = u'720P'
        elif 'dvd' in title.lower():
            resolution = u'SD'
        else:
            resolution = u'Unknown'
        return resolution


'''
Required Key:
size, category, pubdate, title, indexer, info_link, guid, torrentfile, resolution, type(magnet, torrent)

'''


'''
{u'torrent_id': u'https://thepiratebay.org/torrent/6744588/Cars_(2006)_720p_BrRip_x264_-_600MB_-_YIFY',
u'seeders': 381
u'freeleech': False,
u'details_url': u'https://thepiratebay.org/torrent/6744588/Cars_(2006)_720p_BrRip_x264_-_600MB_-_YIFY',
u'download_url': u'magnet:?xt=urn:btih:532a821cd3e4a31594b661de2c9e8622546c4655&dn=Cars+%282006%29+720p+BrRip+x264+-+600MB+-+YIFY&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Fzer0day.ch%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fpublic.popcorn-tracker.org%3A6969',
u'imdb_id': u'',
u'leechers': 50,
u'release_name': u'Cars (2006) 720p BrRip x264 - 600MB - YIFY',
u'type': u'movie',
u'size': 601}
'''


'''
{
  "results": [
    {
      "release_name": "John Wick Chapter 2 2017 1080p BluRay AC3 x264--English",
      "torrent_id": "http://www.dnoid.me/files/download/3528456/",
      "details_url": "http://www.dnoid.me/files/details/3528456/9936912/",
      "download_url": "http://mxq:5060/download/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsIjoiaHR0cDovL3d3dy5kbm9pZC5tZS9maWxlcy9kb3dubG9hZC8zNTI4NDU2LyIsIm5iZiI6MTQ4NDU5Mzg0MiwicyI6ImRlbW9ub2lkIn0.l9-9GTbzoASi9G9IRY-IZ_j9d01ySYzLGcu51HW5U6w/John+Wick+Chapter+2+2017+1080p+BluRay+AC3+x264--English.torrent",
      "imdb_id": "",
      "freeleech": false,
      "type": "movie",
      "size": 963,
      "leechers": 0,
      "seeders": 1
    },
    {
      "release_name": "68 latest trailers 2017 720p",
      "torrent_id": "http://www.dnoid.me/files/download/3506006/",
      "details_url": "http://www.dnoid.me/files/details/3506006/9936912/",
      "download_url": "http://mxq:5060/download/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsIjoiaHR0cDovL3d3dy5kbm9pZC5tZS9maWxlcy9kb3dubG9hZC8zNTA2MDA2LyIsIm5iZiI6MTQ4NDU5Mzg0MiwicyI6ImRlbW9ub2lkIn0.KgS2IznzqKCLux2ay8-HUGxkDRdy_kFFv6mD-4DTLKQ/68+latest+trailers+2017+720p.torrent",
      "imdb_id": "",
      "freeleech": false,
      "type": "movie",
      "size": 1401,
      "leechers": 2,
      "seeders": 3
    }
  ],
  "total_results": 2
}

'''
