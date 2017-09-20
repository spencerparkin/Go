# go_board.py

class GoBoard:
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    
    def __init__( self, size ):
        self.size = size
        self.matrix = [ [ self.EMPTY for j in range( size ) ] for i in range( size ) ]
    
    def __eq__( self, board ):
        for i in range( self.size ):
            for j in range( self.size ):
                if self.matrix[i][j] != board.matrix[i][j]:
                    return False
        return True
    
    def AdjacentLocations( self, location ):
        for offset in [ ( -1, 0 ), ( 1, 0 ), ( 0, -1 ), ( 0, 1 ) ]:
            adjacent_location = ( location[0] + offset[0], location[1] + offset[1] )
            if adjacent_location[0] < 0 or adjacent_location[1] < 0:
                continue
            if adjacent_location[0] >= self.size or adjacent_location[1] >= self.size:
                continue
            yield adjacent_location
    
    def GetState( self, location ):
        return self.matrix[ location[0] ][ location[1] ]
    
    def SetState( self, location, state ):
        self.matrix[ location[0] ][ location[1] ] = state
    
    def Analyze( self, for_who ):
        location_list = []
        for i in range( self.size ):
            for j in range( self.size ):
                if self.GetState( ( i, j ) ) == for_who:
                    location_list.append( ( i, j ) )
        group_list = []
        while len( location_list ) > 0:
            location = location_list[0]
            group = { 'location_list' : [], 'liberties' : 0 }
            queue = [ location ]
            while len( queue ) > 0:
                location = queue.pop()
                group[ 'location_list' ].append( location )
                location_list.remove( location )
                for adjacent_location in self.AdjacentLocations( location ):
                    if adjacent_location in group[ 'location_list' ]:
                        continue
                    if self.GetState( adjacent_location ) == for_who:
                        queue.append( adjacent_location )
            for location in group[ 'location_list' ]:
                for adjacent_location in self.AdjacentLocations( location ):
                    if self.GetState( adjacent_location ) == self.EMPTY:
                        group[ 'liberties' ] += 1
            group_list.append( group )
        return group_list
    
    def Clone( self ):
        clone = GoBoard( self.size )
        for i in range( self.size ):
            for j in range( self.size ):
                clone.matrix[i][j] = self.matrix[i][j]
        return clone
    
    def __str__( self ):
        board_string = ''
        for i in range( self.size ):
            for j in range( self.size ):
                stone = self.matrix[i][j]
                if stone == self.EMPTY:
                    stone = ' '
                elif stone == self.WHITE:
                    stone = 'O'
                elif stone == self.BLACK:
                    stone = '#'
                else:
                    stone = '?'
                board_string += '[' + stone + ']'
                if j < self.size - 1:
                    board_string += '--'
            board_string += ' %02d\n' % i
            if i < self.size - 1:
                board_string += ' |   ' * self.size + '\n'
            else:
                for j in range( self.size ):
                    board_string += ' %02d  ' % j
                board_string += '\n'
        return board_string