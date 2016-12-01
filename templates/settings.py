from cherrypy import expose
import dominate
from dominate.tags import *
import core
from core import config
from header import Header
import os

class Settings():

    def __init__(self):
        self.config = config.Config()

    @expose
    def index(self):
        # make some shorthand
        c = self.config.sections()

        # converts comma delimited values into lists
        for section in c:
            if section != 'Filters':
                for key in c[section]:
                    value = c[section][key]
                    if ',' in value:
                        c[section][key] = value.split(',')
            elif section == 'Filters':
                for key in c[section]:
                    value = c[section][key]
                    if ',' in value:
                        c[section][key] = value.replace(',', ', ')

        doc = dominate.document(title='Watcher')

        with doc.head:
            base(href="/static/")

            link(rel='stylesheet', href='css/style.css')
            link(rel='stylesheet', href='css/settings.css')
            link(rel='stylesheet', href='//fonts.googleapis.com/css?family=Raleway')
            link(rel='stylesheet', href='font-awesome/css/font-awesome.css')
            link(rel='stylesheet', href='js/sweetalert-master/dist/sweetalert.css')

            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js')
            script(type='text/javascript', src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.0/jquery-ui.min.js')
            script(type='text/javascript', src='js/settings/main.js')
            script(type='text/javascript', src='js/sweetalert-master/dist/sweetalert-dev.js')
            script(type='text/javascript', src='js/settings/save_settings.js')


        with doc:
            Header.insert_header(current="settings")
            with div(id='content'):

                p('Search', id='searchform')
                # set the config section at each new section. Just makes everything a little shorter and easier to write.
                c_s = 'Search'
                with ul(id='search', cls='wide'):
                    with li(cls='bbord'):
                        i(id='searchafteradd', cls='fa fa-square-o checkbox', value=c[c_s]['searchafteradd'])
                        span('Search immediately after adding movie.')
                        span('Skips wait until next scheduled search.', cls='tip')
                    with li(cls='bbord'):
                        i(id='autograb', cls='fa fa-square-o checkbox', value=c[c_s]['autograb'])
                        span('Automatically grab best result.')
                        span('Will still wait X days if set.', cls='tip')
                    with li(cls='bbord'):
                        span('Search time:')
                        input(type='number', min='0', max='23', id='searchtimehr', style='width: 2.5em', value=c[c_s]['searchtimehr'])
                        span(':')
                        input(type='number', min='0', max='59', id='searchtimemin', style='width: 2.5em', value=c[c_s]['searchtimemin'])
                        span('What time of day to begin searches (24h time). Requires Restart.', cls='tip')
                    with li(cls='bbord'):
                        span('Search every ')
                        input(type='number', min='1', id='searchfrequency', style='width: 2.5em', value=c[c_s]['searchfrequency'] )
                        span('hours.')
                        span('Once releases are available according to predb.me. Requires Restart.', cls='tip')
                    with li(cls='bbord'):
                        span('Wait ')
                        input(type='number', min='0', max='14', id='waitdays', style='width: 2.0em', value=c[c_s]['waitdays'])
                        span(' days for best release.')
                        span('After results are found, wait to snatch in case better match is found.', cls='tip')
                    with li():
                        span('Retention: ')
                        input(type='number', min='0', id='retention', value=c[c_s]['retention'])
                        span(' days.')
                        span('Use 0 for no limit.', cls='tip')

                p('Indexers')
                c_s = 'Indexers'
                with ul(id='indexers', cls='wide'):
                    with li():
                        with ul(id='newznab_list'):
                            with li(cls='sub_cat'):
                                span('NewzNab Indexers')

                            for n in c[c_s]:
                                if n != '__name__':
                                    with li(cls='newznab_indexer'):
                                        i(cls='newznab_check fa fa-square-o checkbox', value=c[c_s][n][2])
                                        input(type='text', cls='newznab_url', value=c[c_s][n][0], placeholder=" URL" )
                                        input(type='text', cls='newznab_api', value=c[c_s][n][1], placeholder=" Api Key")
                            with li(id='add_newznab_row'):
                                i(cls='fa fa-plus-square', id='add_row')
                p('Quality')
                c_s = 'Quality'
                resolutions = ['4K','1080P','720P','SD']
                br()
                span('Quality and Filters may be set separately for each movie, this is the default setting.')
                with ul(id='quality', cls='wide'):
                    # Resolution Block
                    with ul(id='resolution', cls='sortable'):
                        span('Resolutions', cls='sub_cat not_sortable')

                        for res in resolutions:
                            prior = '{}priority'.format(res)
                            with li(cls='rbord', id=prior, sort=c[c_s][res][1]):
                                i(cls='fa fa-bars')
                                i(id=res, cls='fa fa-square-o checkbox', value=c[c_s][res][0])
                                span(res)

                    # Size restriction block
                    with ul(id='resolution_size'):
                        with li('Size Restrictions', cls='sub_cat'):
                            span('In MB.', cls='tip')

                        for res in resolutions:
                            min = '{}min'.format(res)
                            max = '{}max'.format(res)
                            with li():
                                span(res)
                                input(type='number', id=min, value=c[c_s][res][2], min='0', style='width: 7.5em')
                                input(type='number', id=max, value=c[c_s][res][3], min='0', style='width: 7.5em')

                div(','.join(resolutions), cls='hidden_data')

                p('Filters', id='filter_form')
                # set the config section at each new section. Just makes everything a little shorter and easier to write.
                c_s = 'Filters'
                with ul(id='filters', cls='wide'):
                    with li(cls='bbord'):
                        span('Required words:')
                        input(type='text', id='requiredwords', value=c[c_s]['requiredwords'], style='width: 16em')
                        span('Releases must contain these words.', cls='tip')
                    with li(cls='bbord'):
                        span('Preferred words:')
                        input(type='text', id='preferredwords', value=c[c_s]['preferredwords'], style='width: 16em')
                        span('Releases with these words score higher.', cls='tip')
                    with li():
                        span('Ignored words:')
                        input(type='text', id='ignoredwords', value=c[c_s]['ignoredwords'], style='width: 16em')
                        span('Releases with these words are ignored.', cls='tip')

                p('Downloader')
                with ul(id='downloader'):
                    c_s = 'Sabnzbd'
                    with li(cls='bbord'):
                        i(id='sabenabled', cls='fa fa-circle-o radio', tog='sabnzbd', value=c[c_s]['sabenabled'])
                        span('Sabnzbd', cls='sub_cat')
                    # I'm not 100% sure it is valid to do a ul>ul, but it only work this way so deal with it.
                    with ul(id='sabnzbd'):
                        with li('Host & Port: ', cls='bbord'):
                            input(type='text', id='sabhost', value=c[c_s]['sabhost'], style='width: 25%')
                            span(' : ')
                            input(type='text', id='sabport', value=c[c_s]['sabport'], style='width: 25%')
                        with li('Api Key: ', cls='bbord'):
                            input(type='text', id='sabapi', value=c[c_s]['sabapi'], style='width: 50%')
                            span('Please use full api key.', cls='tip')
                        with li('Category: ', cls='bbord'):
                            input(type='text', id='sabcategory', value=c[c_s]['sabcategory'], style='width: 50%')
                            span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                        with li('Priority: ', cls='bbord'):
                            with select(id='sabpriority', value=c[c_s]['sabpriority'], style='width: 50%'):
                                pl = ['Paused','Low','Normal','High','Forced']
                                for o in pl:
                                    if o == c[c_s]['sabpriority']:
                                        option(o, value=o, selected="selected")
                                    else:
                                        option(o, value=o)

                        with li():
                            with button(cls='test_connection', mode='sabnzbd'):
                                span('Test Connection')
                    c_s = 'NzbGet'
                    with li():
                        i(id='nzbgenabled', cls='fa fa-circle-o radio', tog='nzbget', value=c[c_s]['nzbgenabled'])
                        span('NZBGet', cls='sub_cat')
                    with ul(id='nzbget'):
                        with li('Host & Port: ', cls='bbord'):
                            input(type='text', id='nzbghost', value=c[c_s]['nzbghost'], style='width: 25%')
                            span(' : ')
                            input(type='text', id='nzbgport', value=c[c_s]['nzbgport'], style='width: 25%')
                        with li('User Name: ', cls='bbord'):
                            input(type='text', id='nzbguser', value=c[c_s]['nzbguser'], style='width: 50%')
                            span('Default: nzbget.', cls='tip')
                        with li('Password: ', cls='bbord'):
                            input(type='text', id='nzbgpass', value=c[c_s]['nzbgpass'], style='width: 50%')
                            span('Default: tegbzn6789.', cls='tip')
                        with li('Category: ', cls='bbord'):
                            input(type='text', id='nzbgcategory', value=c[c_s]['nzbgcategory'], style='width: 50%')
                            span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                        with li('Priority: ', cls='bbord'):
                            with select(id='nzbgpriority', style='width: 50%'):
                                pl = ['Very Low','Low','Normal','High','Forced']
                                for o in pl:
                                    if o == c[c_s]['nzbgpriority']:
                                        option(o, value=o, selected="selected")
                                    else:
                                        option(o, value=o)
                        with li(cls='bbord'):
                            i(id='nzbgaddpaused', cls='fa fa-square-o checkbox', value=c[c_s]['nzbgaddpaused'])
                            span('Add Paused')

                        with li():
                            with button(cls='test_connection', mode='nzbget'):
                                span('Test Connection')

                p('Post-Processing')
                c_s = 'Postprocessing'
                with ul(id='postprocessing'):
                    with li():
                        i(id='cleanupfailed', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupfailed'])
                        span('Delete leftover files after a failed download.')
                    with li():
                        i(id='renamerenabled', cls='fa fa-square-o checkbox', value=c[c_s]['renamerenabled'])
                        span('Enable Renamer')
                    with ul(id='renamer'):
                        with li():
                            input(id='renamerstring', type='text', style='width: 80%', value=c[c_s]['renamerstring'])
                        with li('Available tags:'):
                            br()
                            span('{title} {year} {resolution} {rated} {imdbid} {videocodec} {audiocodec} {releasegroup}', cls='taglist')
                            br()
                            span('Example: ')
                            br()
                            span('{title} {year} - {videocodec} = How to Train Your Dragon 2010 - x264.mkv',  cls='taglist')

                    with li():
                        i(id='moverenabled', cls='fa fa-square-o checkbox', value=c[c_s]['moverenabled'])
                        span('Enable Mover')
                    with ul(id='mover'):
                        with li():
                            span('Move movie file to: ')
                            input(type='text', style='width: 18em', id='moverpath', value=c[c_s]['moverpath'])
                            span('Use absolute path.', cls='tip')
                            br()
                            span('Example: ')
                            br()
                            span('/home/user/movies/{title} {year} = /home/user/movies/Black Swan 2010/',  cls='taglist')
                            br()
                            i(id='cleanupenabled', cls='fa fa-square-o checkbox', value=c[c_s]['cleanupenabled'])
                            span('Clean up after move.')
                p('Server')
                c_s = 'Server'
                with ul(id='server', cls='wide'):
                    with li('Host: ', cls='bbord'):
                        input(type='text', id='serverhost', value=c[c_s]['serverhost'], style='width: 50%')
                        span('Typically localhost or 0.0.0.0.', cls='tip')
                    with li('Port: ', cls='bbord'):
                        input(type='number', id='serverport', value=c[c_s]['serverport'], style='width: 50%')
                    with li('API Key: ', cls='bbord'):
                        input(type='text', id='apikey', value=c[c_s]['apikey'], style='width: 50%')
                        with span(cls='tip'):
                            i(id='generate_new_key', cls='fa fa-refresh')
                            span('Generate new key.')
                    with li(cls='bbord'):
                        i(id='launchbrowser', cls='fa fa-square-o checkbox', value=c[c_s]['launchbrowser'])
                        span('Open browser on launch.')
                    with li(cls='bbord'):
                        i(id='checkupdates', cls='fa fa-square-o checkbox', value=c[c_s]['checkupdates'])
                        span('Check for updates every ')
                        input(type='number', id='checkupdatefrequency', value=c[c_s]['checkupdatefrequency'], style='width: 3em')
                        span(' hours.')
                        with span('Current version hash: ', cls='tip'):
                            a(core.CURRENT_HASH[0:7], href='{}/commits'.format(core.GIT_URL))
                    with li(cls='bbord'):
                        span('Keep ')
                        input(type='text', id='keeplog', value=c[c_s]['keeplog'], style='width: 3em')
                        span(' days of logs.')
                    with li():
                        with span(cls='tip'):
                            button('Restart', id='restart')
                            button('Shut Down', id='shutdown')

            with div(id='footer'):
                with button(id='save_settings'):
                    span('Save Changes')
        return doc.render()
