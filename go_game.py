# go_game.py

import random

from go_board import GoBoard

class GoGame:
    def __init__( self, size = 0 ):
        self.size = size
        self.history = [ GoBoard( size ) ]
        self.whose_turn = GoBoard.WHITE
        self.consecutive_pass_count = 0
        self.captures = { GoBoard.WHITE : 0, GoBoard.BLACK : 0 }
    
    def CurrentBoard( self ):
        return self.history[ len( self.history ) - 1 ]
    
    def OpponentOf( self, for_who ):
        return GoBoard.WHITE if for_who == GoBoard.BLACK else GoBoard.BLACK
    
    def PlaceStone( self, i, j ):
        
        opponent = self.OpponentOf( self.whose_turn )
        
        # If the given coordinates are out of range, then we consider it a pass.
        if i >= 0 and i < self.size and j >= 0 and j < self.size:
            board = self.CurrentBoard()
            if board.matrix[i][j] != GoBoard.EMPTY:
                raise Exception( 'Cannot place a stone where one already exists.' )
            
            board = board.Clone()
            board.matrix[i][j] = self.whose_turn
            
            group_list = board.AnalyzeGroups( opponent )
            for group in group_list:
                if group[ 'liberties' ] == 0:
                    for location in group[ 'location_list' ]:
                        board.SetState( location, GoBoard.EMPTY )
                        self.captures[ self.whose_turn ] += 1
                        
            group_list = board.AnalyzeGroups( self.whose_turn )
            for group in group_list:
                if group[ 'liberties' ] == 0:
                    raise Exception( 'Cannot commit suicide.' )
            
            if len( self.history ) >= 2 and self.history[ len( self.history ) - 2 ] == board:
                raise Exception( 'Cannot repeat board state so soon.' )
            
            self.history.append( board )
            self.consecutive_pass_count = 0
            
            if len( self.history ) > 10:
                self.history.pop(0)
        else:
            self.consecutive_pass_count += 1
        
        self.whose_turn = opponent
    
    def RelinquishStone( self, i, j ):

        opponent = self.OpponentOf( self.whose_turn )
        
        if i < 0 or i >= self.size or j < 0 or j >= self.size:
            raise Exception( 'Board location bogus: (%d,%d).' % ( i, j ) )
        
        board = self.CurrentBoard()
        if board.GetState( ( i, j ) ) != self.whose_turn:
            raise Exception( 'Can only relinquish your own stones.' )
        
        board.SetState( ( i, j ), GoBoard.EMPTY )
        self.captures[ opponent ] += 1
        
        # Notice that we do not change whose turn it is.
    
    def CalculateScores( self ):
        territory, group_list = self.CurrentBoard().CalculateTerritory()
        scores = {
            GoBoard.WHITE : {
                'score' : territory[ GoBoard.WHITE ] + self.captures[ GoBoard.WHITE ],
                'territory' : territory[ GoBoard.WHITE ],
                'captures' : self.captures[ GoBoard.WHITE ]
            },
            GoBoard.BLACK : {
                'score' : territory[ GoBoard.BLACK ] + self.captures[ GoBoard.BLACK ],
                'territory' : territory[ GoBoard.BLACK ],
                'captures' : self.captures[ GoBoard.BLACK ]
            }
        }
        return scores

    def CalculateReasonableMove( self ):
        # This is a quite laughable proposition as only programs like Google's DeepMind AlphaGo
        # have been able to master the game of Go.  I can't help, however, but try to offer some
        # kind of support for the idea of the computer trying to take a somewhat reasonable turn.
        # What we do here is simply.  We simply try to evaluate every possible move to see which
        # appears to be most immediately advantageous.  Of course, there is no thinking ahead here,
        # so this can't be all that great.
        whose_turn = self.whose_turn
        opponent = self.OpponentOf( self.whose_turn )
        consecutive_pass_count = self.consecutive_pass_count
        captures = {
            whose_turn : self.captures[ whose_turn ],
            opponent : self.captures[ opponent ]
        }
        board = self.CurrentBoard()
        current_territory = board.CalculateTerritory()[0]
        current_group_list_stats = {
            whose_turn : self.CalculateGroupListStats( board.AnalyzeGroups( whose_turn ) ),
            opponent : self.CalculateGroupListStats( board.AnalyzeGroups( opponent ) ),
        }
        best_move = None
        best_rank = 0
        for location in board.AllLocationsOfState( GoBoard.EMPTY ):
            self.history.append( board.Clone() )
            try:
                self.PlaceStone( location[0], location[1] )
                territory = self.CurrentBoard().CalculateTerritory()[0]
                group_list_stats = {
                    whose_turn : self.CalculateGroupListStats( self.CurrentBoard().AnalyzeGroups( whose_turn ) ),
                    opponent : self.CalculateGroupListStats( self.CurrentBoard().AnalyzeGroups( opponent ) )
                }
                rank = 0
                if territory[ whose_turn ] > current_territory[ whose_turn ]:
                    rank += ( territory[ whose_turn ] - current_territory[ whose_turn ] ) * 10
                if territory[ opponent ] < current_territory[ opponent ]:
                    rank += ( current_territory[ opponent ] - territory[ opponent ] ) * 9
                if self.captures[ whose_turn ] > captures[ whose_turn ]:
                    rank += ( self.captures[ whose_turn ] - captures[ whose_turn ] ) * 8
                if group_list_stats[ whose_turn ][ 'jeopardy_count ' ] < current_group_list_stats[ whose_turn ][ 'jeopardy_count' ]:
                    rank += ( current_group_list_stats[ whose_turn ][ 'jeopardy_count' ] - group_list_stats[ whose_turn ][ 'jeopardy_count ' ] ) * 7
                if group_list_stats[ whose_turn ][ 'largest_group' ] > current_group_list_stats[ whose_turn ][ 'largest_group' ]:
                    rank += ( group_list_stats[ whose_turn ][ 'largest_group' ] - current_group_list_stats[ whose_turn ][ 'largest_group' ] ) * 6
                if group_list_stats[ opponent ][ 'total_liberties' ] < current_group_list_stats[ opponent ][ 'total_liberties' ]:
                    rank += ( current_group_list_stats[ opponent ][ 'total_liberties' ] - group_list_stats[ opponent ][ 'total_liberties' ] ) * 5
                if rank > best_rank:
                    best_rank = rank
                    best_move = location
            except:
                pass
            finally:
                self.history.pop()
                self.whose_turn = whose_turn
                self.consecutive_pass_count = consecutive_pass_count
                self.captures[ whose_turn ] = captures[ whose_turn ]
                self.captures[ opponent ] = captures[ opponent ]
        if not best_move:
            best_move = ( -1, -1 )
        return best_move

    def CalculateGroupListStats( self, group_list ):
        stats = {
            'jeopardy_count' : 0,
            'largest_group' : 0,
            'smallest_group' : 9999,
        }
        for group in group_list:
            if group[ 'liberties' ] == 1:
                stats[ 'jeopardy_count' ] += 1
            if len( group[ 'location_list' ] ) > stats[ 'largest_group' ]:
                stats[ 'largest_group' ] = len( group[ 'location_list' ] )
            if len( group[ 'location_list' ] ) < stats[ 'smallest_group' ]:
                stats[ 'smallest_group' ] = len( group[ 'location_list' ] )
        return stats

    def Print( self ):
        print( str( self.CurrentBoard() ) )
    
    def PrintGroupListData( self, group_list ):
        group_list = sorted( group_list, key = lambda group : group[ 'liberties' ] )
        for group in group_list:
            print( '-------------------------' )
            print( 'Group: ' + ','.join( [ '(%d,%d)' % ( location[0], location[1] ) for location in group[ 'location_list' ] ] ) )
            print( 'Liberties: %d' % group[ 'liberties' ] )
    
    def PrintGroupAnalysis( self ):
        board = self.CurrentBoard()
        white_group_list = board.AnalyzeGroups( GoBoard.WHITE )
        black_group_list = board.AnalyzeGroups( GoBoard.BLACK )
        print( 'ANALYSIS OF BOARD' )
        print( '==================================' )
        print( 'For white:' )
        self.PrintGroupListData( white_group_list )
        print( '==================================' )
        print( 'For black:' )
        self.PrintGroupListData( black_group_list )
        print( '' )
    
    def PrintScoreCalculation( self ):
        scores = self.CalculateScores()
        print( 'White score: %d' % scores[ GoBoard.WHITE ][ 'score' ] )
        print( 'Black score: %d' % scores[ GoBoard.BLACK ][ 'score' ] )
    
    def Serialize( self ):
        data = {
            'size' : self.size,
            'history' : [ board.Serialize() for board in self.history ],
            'whose_turn' : self.whose_turn,
            'consecutive_pass_count' : self.consecutive_pass_count,
            'captures' : {
                'white' : self.captures[ GoBoard.WHITE ],
                'black' : self.captures[ GoBoard.BLACK ],
            }
        }
        return data
    
    def Deserialize( self, data ):
        self.size = data[ 'size' ]
        self.history = [ GoBoard().Deserialize( board ) for board in data[ 'history' ] ]
        self.whose_turn = data[ 'whose_turn' ]
        self.consecutive_pass_count = data[ 'consecutive_pass_count' ]
        self.captures = {
            GoBoard.WHITE : data[ 'captures' ][ 'white' ],
            GoBoard.BLACK : data[ 'captures' ][ 'black' ],
        }