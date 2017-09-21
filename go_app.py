# go_app.py

import os
import cherrypy

# TODO: To make this work, we'll have to have some sort of database backend, like MongoDB,
#       unless we did something super lame like read/write to disk.

webroot = os.getcwd() + '/webroot'

class GoApp( object ):
    
    @cherrypy.expose
    def default( self ):
        cherrypy.response.headers[ 'Content-Type' ] = 'text/html'
        cherrypy.response.headers[ 'cache-control' ] = 'no-store'
        cherrypy.lib.static.serve_file( webroot + '/go_home_page.html', content_type = 'text/html' )

if __name__ == '__main__':
    go_app = GoApp()
    
    app_config = {
        'global' : {
            'server.socket_host' : '0.0.0.0',
            'server.socket_port' : int( os.environ.get( 'PORT', 5000 ) ),
        },
        '/webroot' : {
            'tools.staticdir.root' : os.path.dirname( os.path.abspath( __file__ ) ),
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : 'webroot',
        }
    }
    
    cherrypy.quickstart( go_app, '/', config = app_config )