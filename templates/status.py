import core
import dominate
from cherrypy import expose
from core import sqldb
from dominate.tags import *
from header import Header
from head import Head


class Status():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/status.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/status.css'.format(core.CONFIG['Server']['theme']))
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/movie_status_popup.css')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/movie_status_popup.css'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/status/main.js?v=01.11')

        with doc:
            Header.insert_header(current="status")
            with div(id='content'):
                with div(id='view_config'):
                    span('Display: ')
                    with select(id='list_style'):
                        options = ['Posters', 'List']
                        for opt in options:
                            option(opt, value=opt.lower())
                    span('Order By: ')
                    with select(id='list_sort'):
                        options = ['Status', 'Title', 'Year']
                        for opt in options:
                            option(opt, value=opt.lower())
                self.movie_list()
            div(id='overlay')
            div(id='status_pop_up')

        return doc.render()

    @staticmethod
    def movie_list():
        movies = sqldb.SQL().get_user_movies()

        if movies == []:
            return None
        elif not movies:
            html = 'Error retrieving list of user\'s movies. Check logs for more information'
            return html

        movie_list = ul(id='movie_list')
        with movie_list:
            for data in movies:
                poster_path = core.URL_BASE + '/static/images/posters/{}.jpg'.format(data['imdbid'])
                with li(cls='movie', imdbid=data['imdbid']):
                    with div():
                        status = data['status']
                        if status == 'Wanted':
                            span(u'Wanted', cls='status wanted')
                        elif status == 'Found':
                            span(u'Found', cls='status found')
                        elif status == 'Snatched':
                            span(u'Snatched', cls='status snatched')
                        elif status == 'Downloading':
                            span(u'Downloading', cls='status downloading')
                        elif status == 'Finished':
                            span(u'Finished', cls='status finished')
                        else:
                            span(u'Status Unknown', cls='status wanted')

                        img(src=poster_path, alt='Poster for {}'.format(data['imdbid']))

                        with span(data['title'], cls='title', title=data['title']):
                            br()
                            span(data['year'], cls='year')
                            with span(cls='tomatorating'):
                                score = int(data['tomatorating'][0])
                                count = 0
                                for star in range(score / 2):
                                    count += 1
                                    i(cls='fa fa-star')
                                if score % 2 == 1:
                                    count += 1
                                    i(cls='fa fa-star-half-o')
                                for nostar in range(5 - count):
                                    i(cls='fa fa-star-o')

                            span(data['rated'], cls='rated')

        return unicode(movie_list)

# pylama:ignore=W0401
