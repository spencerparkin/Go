# go_app.py

import os
import cherrypy
import pymongo

from go_game import GoGame
from go_board import GoBoard

webroot = os.getcwd() + '/webroot'

class GoApp( object ):
    def __init__( self ):
        try:
            # Run "heroku config:get MONGO_URI" to acquire this URI.  Being in plain text here, anyone could find it and corrupt our database.
            database_uri = 'mongodb://heroku_fq88qpck:jrte31rm6nsn87qkennbt02vuk@ds147304.mlab.com:47304/heroku_fq88qpck'
            self.mongo_client = pymongo.MongoClient( database_uri )
            self.go_database = self.mongo_client[ 'heroku_fq88qpck' ]
            collection_names = self.go_database.collection_names()
            if not 'game_collection' in collection_names:
                self.go_database.create_collection( 'game_collection' )
            self.game_collection = self.go_database[ 'game_collection' ]
        except:
            self.mongo_client = None
    
    def MakeErrorPage( self, error ):
        return '''
        <!DOCTYPE HTML>
        <html lang="en-US">
            <head>
                <title>Error!</title>
            </head>
            <body>
                <center><b>Error:</b> %s</center>
            </body>
        </html>
        ''' % error
    
    @cherrypy.expose
    def default( self, **kwargs ):
        if not self.mongo_client:
            return self.MakeErrorPage( 'Failed to connect to MongoDB back-end.' )
        key = {
            '$or' : [
                { 'white' : '' },
                { 'black' : '' }
            ]
        }
        cursor = self.game_collection.find( key )
        if cursor.count() == 0:
            html_game_table = '<p>The game collection is empty.  Create a new game.</p>'
        else:
            html_game_table = '<p>Following is a list of joinable games, if any.</p>\n'
            html_game_table += '<table>\n<tr><th>Game Name</th><th>White Player</th><th>Black Player</th></tr>\n'
            for game_doc in cursor:
                html_game_table += '<tr>\n'
                html_game_table += '<td>%s</td>' % game_doc[ 'name' ]
                if game_doc[ 'white' ]:
                    html_game_table += '<td>%s</td>' % game_doc[ 'white' ]
                else:
                    html_game_table += '<td><input type="button" value="Join as White" onclick="OnJoinGameClicked( \'%s\', \'white\' )"></input></td>\n' % game_doc[ 'name' ]
                if game_doc[ 'black' ]:
                    html_game_table += '<td>%s</td>' % game_doc[ 'black' ]
                else:
                    html_game_table += '<td><input type="button" value="Join as Black" onclick="OnJoinGameClicked( \'%s\', \'black\' )"></input></td>\n' % game_doc[ 'name' ]
                html_game_table += '</tr>\n'
            html_game_table += '</table>\n'
        html_doc = '''
        <!DOCTYPE HTML>
        <html lang="en-US">
            <head>
                <meta charset="UTF-8">
                <title>The game of Go!</title>
                <script src="https://code.jquery.com/jquery.js"></script>
                <script src="scripts/go.js"></script>
            </head>
            <body>
                %s
                <input type="button" value="New Game" onclick="OnNewGameClicked()"></input>
            </body>
        </html>
        ''' % html_game_table
        return html_doc
    
    @cherrypy.expose
    def error_page( self, **kwargs ):
        error = kwargs[ 'error' ]
        return self.MakeErrorPage( error )
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def new_game( self, **kwargs ):
        name = kwargs[ 'name' ]
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if game_doc:
            return { 'error' : 'A game by the name "%s" already exists.' % name }
        size = kwargs[ 'size' ] if 'size' in kwargs else 7
        go_game = GoGame( size )
        data = go_game.Serialize()
        game_doc = {
            'name' : name,
            'black' : '',
            'white' : '',
            'data' : data,
        }
        result = self.game_collection.insert_one( game_doc )
        return {}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def join_game( self, **kwargs ):
        name = kwargs[ 'name' ]
        color = kwargs[ 'color' ]
        player_name = kwargs[ 'player_name' ]
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if not game_doc:
            return { 'error' : 'A game by the name "%s" was not found.' % name }
        if game_doc[ color ]:
            return { 'error' : 'Someone (%s) has already joined as color %s.' % ( game_doc[ color ], color ) }
        result = self.game_collection.update_one( { 'name' : name }, { '$set' : { color : player_name } } )
        return {}
    
    # TODO: We will display whose turn it is here, but the user will have to refresh the page to
    #       find out when it becomes their turn again.  Is there a way to be notified and then auto-refresh?
    @cherrypy.expose
    def game( self, **kwargs ):
        name = kwargs[ 'name' ]
        color = kwargs[ 'color' ] # TODO: When making the "onclick" call, this specifies what stone color is being placed.
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if not game_doc:
            return self.MakeErrorPage( 'Failed to find game: %s', name )
        go_game = GoGame()
        go_game.Deserialize( game_doc[ 'data' ] )
        # TODO: The idea here is to dynamically generate an HTML page that shows the board state.
        #       I'm thinking of just tiling a bunch of textures.  Can I overlay one texture on top
        #       of another, the one on top having some alpha?  Can CSS help with all this?
        #       Can I also make sure that each tile has an "onclick" event associated with it that
        #       will call a JS function with the appropriate tile coordinates?
        return '''
        <!DOCTYPE HTML>
        <html lang="en-US">
            <head>
            </head>
            <body>
            </body>
        </html>
        '''
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def place_stone( self, **kwargs ):
        name = kwargs[ 'name' ]
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if not game_doc:
            return { 'error' : 'A game by the name "%s" was not found.' % name }
        color = kwargs[ 'color' ]
        if color == 'white':
            color = GoBoard.WHITE
        elif color == 'black':
            color = GoBoard.BLACK
        else:
            return { 'error' : 'Bogus color given.' }
        row = kwargs[ 'row' ]
        col = kwargs[ 'col' ]
        go_game = GoGame( game_doc[ 'data' ][ 'size' ] )
        go_game.Deserialize( game_doc[ 'data' ] )
        if go_game.whose_turn != color:
            return { 'error' : 'It is not yet your turn.' }
        try:
            go_game.PlaceStone( row, col )
        except Exception as ex:
            return { 'error' : str(ex) }
        return {}

if __name__ == '__main__':
    go_app = GoApp()

    root_dir = os.path.dirname( os.path.abspath( __file__ ) )
    port = int( os.environ.get( 'PORT', 5090 ) )

    app_config = {
        'global' : {
            'server.socket_host' : '0.0.0.0',
            'server.socket_port' : port,
        },
        '/' : {
            'tools.staticdir.root': root_dir,
        },
        '/scripts' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : 'scripts',
        },
        '/images' : {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'images',
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css',
        }
    }
    
    cherrypy.quickstart( go_app, '/', config = app_config )