from fuzzywuzzy import fuzz, process
from core import sqldb
import urllib2
import ssl
import xml.etree.cElementTree as ET

import logging
logging = logging.getLogger(__name__)

class PreDB(object):

    def __init__(self):
        self.sql = sqldb.SQL()


    def check_all(self):
        logging.info('Checking predb.me for new available releases.')

        TABLE_NAME = 'MOVIES'
        movies = self.sql.get_user_movies()

        for movie in movies:
            if movie['predb'] != 'found':
                self.check_one(movie)


    def check_one(self, data):
        title = data['title']
        year = data['year']
        title_year = '{} {}'.format(title, year)
        imdbid = data['imdbid']

        logging.info('Checking predb.me for new available releases for {}.'.format(title))

        rss_titles = self.search_rss(title_year)

        test = title_year.replace(' ', '.').lower()

        if self.fuzzy_match(rss_titles, test):
            logging.info('{} {} found on predb.me.'.format(title, year))
            TABLE_NAME = 'MOVIES'
            self.sql.update(TABLE_NAME, 'predb', 'found', imdbid=imdbid)

    def search_rss(self, title_year):
        search_term = title_year.replace(' ', '+').lower()

        search_string = 'https://predb.me/?cats=movies&search={}&rss=1'.format(search_term)
        request = urllib2.Request( search_string, headers={'User-Agent' : 'Mozilla/5.0'})
        results_xml = urllib2.urlopen(request).read()

        items = self.parse_predb_xml(results_xml)
        return items

    def parse_predb_xml(self, feed):

        root = ET.fromstring(feed)

        # This is so ugly, but some newznab sites don't output json. I don't want to include a huge xml parsing module, so here we are. I'm not happy about it either.
        items =[]
        for item in root.iter('item'):
            for i_c in item:
                if i_c.tag == 'title':
                    items.append(i_c.text)
        return items



    # keeps checking release titles until one matches or all are checked
    def fuzzy_match(self, items, test):
        for item in items:
            match = fuzz.partial_ratio(item, test)
            if match > 50:
                return True
        return False

