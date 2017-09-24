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
    
    def CalculateScores( self ):
        board = self.CurrentBoard()
        self.history.append( board.Clone() )
        try:
            # TODO: Cull dead stones and count them as captures for our calculation.
            #       Make sure to restore captures before returning.  What defines a dead stone?
            #       I think it might have to be an agreed-upon thing unless they play things out.
            territory, group_list = self.CurrentBoard().CalculateTerritory()
            scores = {
                GoBoard.WHITE : territory[ GoBoard.WHITE ] - self.captures[ GoBoard.BLACK ],
                GoBoard.BLACK : territory[ GoBoard.BLACK ] - self.captures[ GoBoard.WHITE ],
            }
        finally:
            self.history.pop()
        return scores

    def CalculateReasonableMove( self ):
        # This is a quite laughable proposition as only programs like Google's DeepMind AlphaGo
        # have been able to master the game of Go.  I can't help, however, but try to offer some
        # kind of support for the idea of the computer trying to take a good or somewhat reasonable turn.
        whose_turn = self.whose_turn
        consecutive_pass_count = self.consecutive_pass_count
        opponent = self.OpponentOf( self.whose_turn )
        baseline_scores = self.CalculateScores()
        board = self.CurrentBoard()
        move_list = []
        for location in board.AllLocationsOfState( GoBoard.EMPTY ):
            self.history.append( board.Clone() )
            try:
                self.PlaceStone( location[0], location[1] )
                scores = self.CalculateScores()
                gain = 0
                gain -= scores[ opponent ] - baseline_scores[ opponent ]
                gain += scores[ self.whose_turn ] - baseline_scores[ self.whose_turn ]
                move_list.append( ( location, gain ) )
            except:
                pass
            finally:
                self.history.pop()
                self.whose_turn = whose_turn
                self.consecutive_pass_count = consecutive_pass_count
        largest_gain = 0
        for move in move_list:
            if move[1] > largest_gain:
                largest_gain = move[1]
        best_move_list = []
        for move in move_list:
            if move[1] == largest_gain:
                best_move_list.append( move )
        if len( best_move_list ) > 0:
            best_move = best_move_list[ random.randint( 0, len( best_move_list ) - 1 ) ][0]
        else:
            best_move = ( -1, -1 )
        return best_move

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
        print( 'White score: %d' % scores[ GoBoard.WHITE ] )
        print( 'Black score: %d' % scores[ GoBoard.BLACK ] )
    
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