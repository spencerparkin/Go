# go_game.py

from go_board import GoBoard

class GoGame:
    def __init__( self, size ):
        self.size = size
        self.history = [ GoBoard( size ) ]
        self.whose_turn = GoBoard.WHITE
        self.consecutive_pass_count = 0
        self.captures = { GoBoard.WHITE : 0, GoBoard.BLACK : 0 }
    
    def CurrentBoard( self ):
        return self.history[ len( self.history ) - 1 ]
    
    def PlaceStone( self, i, j ):
        
        opponent = GoBoard.WHITE if self.whose_turn == GoBoard.BLACK else GoBoard.BLACK
        
        # If the given coordinates are out of range, then we consider it a pass.
        if i >= 0 and i < self.size and j >= 0 and j < self.size:
            board = self.CurrentBoard()
            if board.matrix[i][j] != GoBoard.EMPTY:
                raise Exception( 'Cannot place a stone where one already exists.' )
            
            board = board.Clone()
            board.matrix[i][j] = self.whose_turn
            if len( self.history ) >= 2 and self.history[ len( self.history ) - 2 ] == board:
                raise Exception( 'Cannot repeat board state so soon.' )
            
            group_list = board.Analyze( opponent )
            for group in group_list:
                if group[ 'liberties' ] == 0:
                    for location in group[ 'location_list' ]:
                        board.SetState( location, GoBoard.EMPTY )
                        self.captures[ self.whose_turn ] += 1
                        
            group_list = board.Analyze( self.whose_turn )
            for group in group_list:
                if group[ 'liberties' ] == 0:
                    raise Exception( 'Cannot commit suicide.' )
            
            self.history.append( board )
            self.consecutive_pass_count = 0
        else:
            self.consecutive_pass_count += 1
        
        self.whose_turn = opponent
    
    def Print( self ):
        print( str( self.CurrentBoard() ) )
    
    def PrintGroupListData( self, group_list ):
        group_list = sorted( group_list, key = lambda group : group[ 'liberties' ] )
        for group in group_list:
            print( '-------------------------' )
            print( 'Group: ' + ','.join( [ '(%d,%d)' % ( location[0], location[1] ) for location in group[ 'location_list' ] ] ) )
            print( 'Liberties: %d' % group[ 'liberties' ] )
    
    def PrintAnalysis( self ):
        board = self.CurrentBoard()
        white_group_list = board.Analyze( GoBoard.WHITE )
        black_group_list = board.Analyze( GoBoard.BLACK )
        print( 'ANALYSIS OF BOARD' )
        print( '==================================' )
        print( 'For white:' )
        self.PrintGroupListData( white_group_list )
        print( '==================================' )
        print( 'For black:' )
        self.PrintGroupListData( black_group_list )
        print( '' )