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
        cursor = self.game_collection.find( {} )
        if cursor.count() == 0:
            html_game_table = '<p>The game collection is empty.  Create a new game.</p>'
        else:
            html_game_table = '<p>Following is a list of current games.</p>\n'
            html_game_table += '<table border="3">\n<tr><th>Game Name</th><th>Size</th></tr>\n'
            for game_doc in cursor:
                html_game_table += '<tr>\n'
                html_game_table += '<td>%s</td>\n' % game_doc[ 'name' ]
                html_game_table += '<td>%d x %d</td>\n' % ( game_doc[ 'data' ][ 'size' ], game_doc[ 'data' ][ 'size' ] )
                html_game_table += '<td><a href="game?name=%s&color=white">Join as White</a></td>\n' % game_doc[ 'name' ]
                html_game_table += '<td><a href="game?name=%s&color=black">Join as Black</a></td>\n' % game_doc[ 'name' ]
                html_game_table += '<td><input type="button" value="Delete Game" onclick="OnDeleteGameClicked( \'%s\' )"></input></td>\n' % game_doc[ 'name' ]
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
                <link rel="stylesheet" href="css/go.css">
            </head>
            <body>
                %s
                <p><input type="button" value="New Game" onclick="OnNewGameClicked()"></input></p>
                <p>
                For information on how to play Go, click <a href="go_rules.html">here</a>.
                </p>
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
        size = int( kwargs[ 'size' ] ) if 'size' in kwargs else 7
        go_game = GoGame( size )
        data = go_game.Serialize()
        game_doc = {
            'name' : name,
            'data' : data,
        }
        result = self.game_collection.insert_one( game_doc )
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def del_game( self, **kwargs ):
        name = kwargs[ 'name' ]
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if not game_doc:
            return { 'error' : 'Failed to find game by the name: ' + name }
        result = self.game_collection.delete_one( { 'name' : name } )
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def my_turn_yet(self, **kwargs):
        name = kwargs['name']
        color = kwargs['color']
        game_doc = self.game_collection.find_one({'name': name})
        if not game_doc:
            return {'error': 'Failed to find game by the name: ' + name}
        go_game = GoGame()
        go_game.Deserialize(game_doc['data'])
        whose_turn = 'white' if go_game.whose_turn == GoBoard.WHITE else 'black'
        return {'answer': 'yes' if whose_turn == color else 'no', 'error': False}

    @cherrypy.expose
    def game( self, **kwargs ):
        name = kwargs[ 'name' ]
        color = kwargs[ 'color' ]
        game_doc = self.game_collection.find_one( { 'name' : name } )
        if not game_doc:
            return self.MakeErrorPage( 'Failed to find game: %s', name )
        go_game = GoGame()
        go_game.Deserialize( game_doc[ 'data' ] )
        whose_turn = 'white' if go_game.whose_turn == GoBoard.WHITE else 'black'
        color_id = GoBoard.WHITE if color == 'white' else GoBoard.BLACK
        move = { 'row' : -1, 'col' : -1 }
        if 'most_recent_move' in game_doc:
            move = game_doc[ 'most_recent_move' ]
        board = go_game.CurrentBoard()
        group_list = {
            GoBoard.WHITE : board.AnalyzeGroups( GoBoard.WHITE ),
            GoBoard.BLACK : board.AnalyzeGroups( GoBoard.BLACK )
        }
        html_board_table = '<table cellspacing="0" cellpadding="0">\n'
        for i in range( board.size ):
            html_board_table += '<tr>'
            for j in range( board.size ):
                html_board_table += '<td class="cell" style="height: 64px; width: 64px;">\n'
                board_back_image = self.DetermineBoardImage( i, j, board.size )
                state = board.GetState( ( i, j ) )
                if state == GoBoard.EMPTY:
                    html_board_table += '<img src="images/%s" onclick="OnPlaceStoneClicked( \'%s\', \'%s\', %d, %d )">\n' % ( board_back_image, name, color, i, j )
                    if any( [ board.GetState( adj_location ) != GoBoard.EMPTY for adj_location in board.AdjacentLocations( ( i, j ) ) ] ):
                        html_board_table += '<img class="lib_img" id="liberty_%d_%d" src="images/liberty.png" style="visibility:hidden"/>\n' % ( i, j )
                else:
                    if state == GoBoard.WHITE:
                        board_fore_image = 'white_stone.png'
                    elif state == GoBoard.BLACK:
                        board_fore_image = 'black_stone.png'
                    hover_calls = self.FormulateLibertyHoverJSCalls( group_list[ state ], i, j )
                    click_calls = 'onclick="OnGiveUpStoneClicked( \'%s\', \'%s\', %d, %d )"' % ( name, color, i, j ) if state == color_id else ''
                    html_board_table += '<img class="back_img" src="images/%s"/>\n' % board_back_image
                    html_board_table += '<img class="fore_img" src="images/%s" %s %s/>\n' % ( board_fore_image, hover_calls, click_calls )
                    if move[ 'row' ] == i and move[ 'col' ] == j:
                        html_board_table += '<img class="high_img" src="images/highlight.png" %s/>\n' % hover_calls
                html_board_table += '</td>\n'
            html_board_table += '</tr>\n'
        html_board_table += '</table>\n'
        html_message = '<p>It is %s\'s turn.  You are %s.</p>' % ( whose_turn, color )
        html_white_info = self.GenerateInfoForColor( go_game, 'white' )
        html_black_info = self.GenerateInfoForColor( go_game, 'black' )
        scores = go_game.CalculateScores()
        html_score_info = '<center><table border="2">\n'
        html_score_info += '<tr><th></th><th>white</th><th>black</th></tr>\n'
        html_score_info += '<tr><td>score</td><td>%d</td><td>%d</td></tr>\n' % ( scores[ GoBoard.WHITE ][ 'score' ], scores[ GoBoard.BLACK ][ 'score' ] )
        html_score_info += '<tr><td>captures</td><td>%d</td><td>%d</td></tr>\n' % ( scores[ GoBoard.WHITE ][ 'captures' ], scores[ GoBoard.BLACK ][ 'captures' ] )
        html_score_info += '<tr><td>territory</td><td>%d</td><td>%d</td></tr>\n' % ( scores[ GoBoard.WHITE ][ 'territory' ], scores[ GoBoard.BLACK ][ 'territory' ] )
        html_score_info += '</table></center>\n'
        html_pass_button = '<p><center><button type="button" onclick="OnPlaceStoneClicked( \'%s\', \'%s\', -1, -1 )">forfeit turn</button>' % ( name, color )
        return '''
        <html lang="en-US">
            <head>
                <title>Go Game: %s</title>
                <link rel="stylesheet" href="css/go.css">
                <script src="https://code.jquery.com/jquery.js"></script>
                <script src="scripts/go.js"></script>
            </head>
            <body onload="OnPageLoad(%s, '%s', '%s')">
                <div>
                    <p><center>%s</center></p>
                    <p><center>%s</center></p>
                    <!--<center><input type="checkbox" id="respond">Have computer respond.</input></center>-->
                    <center>%s</center>
                    %s
                    <p><center>Click an empty board intersection to place a stone.  Click on your own stone to give it up as a prisoner (at end of game.)</center></p>
                </div>
                <div>
                    %s
                    %s
                </div>
            </body>
        </html>
        ''' % ( name, ('true' if whose_turn != color else 'false'), color, name, html_message, html_score_info, html_board_table, html_pass_button, html_white_info, html_black_info )

    def FormulateLibertyHoverJSCalls( self, group_list, i, j ):
        for group in group_list:
            if ( i, j ) in group[ 'location_list' ]:
                id_list = '[' + ','.join( [ '\'liberty_%d_%d\'' % ( location[0], location[1] ) for location in group[ 'liberty_location_list' ] ] ) + ']'
                js_calls = 'onmouseover="OnMouseOverStone( %s, true )" onmouseout="OnMouseOverStone( %s, false )"' % ( id_list, id_list )
                return js_calls
        return ''

    def GenerateInfoForColor( self, go_game, color ):
        color_id = GoBoard.WHITE if color == 'white' else GoBoard.BLACK
        html_info = '<div id="%s_column_info">\n' % color
        html_info += '<center><h2>%s info</h2></center>\n' % color
        #html_info += '<p><center>captures: %s</center></p>\n' % go_game.captures[ color_id ]
        html_info += '<center><table border="2">\n'
        html_info += '<tr><th>Group Size</th><th>Liberties</th></tr>\n'
        board = go_game.CurrentBoard()
        group_list = board.AnalyzeGroups( color_id )
        group_list = sorted( group_list, key = lambda group : group[ 'liberties' ] )
        for group in group_list:
            html_info += '<tr>\n'
            html_info += '<td>%d</td>\n' % len( group[ 'location_list' ] )
            html_info += '<td>%s</td>\n' % group[ 'liberties' ]
            html_info += '</tr>\n'
        html_info += '</table></center>\n'
        html_info += '</div>\n'
        return html_info

    def DetermineBoardImage( self, i, j, size ):
        directions = []
        if i > 0:
            directions.append( 'n' )
        if i < size - 1:
            directions.append( 's' )
        if j > 0:
            directions.append( 'w' )
        if j < size - 1:
            directions.append( 'e' )
        directions.sort()
        return 'go_' + ''.join( directions ) + '.jpg'
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def place_stone( self, **kwargs ):
        return self.take_turn( **kwargs )
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def relinquish_stone( self, **kwargs ):
        return self.take_turn( **kwargs )
        
    def take_turn( self, **kwargs ):
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
        row = int( kwargs[ 'row' ] )
        col = int( kwargs[ 'col' ] )
        go_game = GoGame()
        go_game.Deserialize( game_doc[ 'data' ] )
        if go_game.whose_turn != color:
            return { 'error' : 'It is not yet your turn.' }
        move = None
        if row < 0 or col < 0 or go_game.CurrentBoard().GetState( ( row, col ) ) == GoBoard.EMPTY:
            try:
                go_game.PlaceStone( row, col )
            except Exception as ex:
                return { 'error' : str(ex) }
            move = { 'row' : row, 'col' : col }
            if 'respond' in kwargs and kwargs[ 'respond' ] == 'true':
                move = go_game.CalculateReasonableMove()
                go_game.PlaceStone( move[0], move[1] )
                move = { 'row' : move[0], 'col' : move[1] }
        elif go_game.CurrentBoard().GetState( ( row, col ) ) == color:
            try:
                go_game.RelinquishStone( row, col )
            except Exception as ex:
                return { 'error' : str(ex) }
        data = go_game.Serialize()
        update = { 'data' : data }
        if move:
            update[ 'most_recent_move' ] = move
        result = self.game_collection.update_one( { 'name' : name }, { '$set' : update } )
        if result.modified_count != 1:
            return { 'error' : 'Failed to update game in database.' }
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
            'tools.staticdir.root' : root_dir,
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : '',
        },
        '/scripts' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : 'scripts',
        },
        '/images' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : 'images',
        },
        '/css' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : 'css',
        },
    }
    
    cherrypy.quickstart( go_app, '/', config = app_config )