# go_board.py

class GoBoard:
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    
    def __init__( self, size = 0 ):
        self.size = size
        if size > 0:
            self.matrix = [ [ self.EMPTY for j in range( size ) ] for i in range( size ) ]

    def Serialize( self ):
        return {
            'size' : self.size,
            'matrix' : self.matrix
        }

    def Deserialize( self, data ):
        self.size = data[ 'size' ]
        self.matrix = data[ 'matrix' ]
        return self

    def __eq__( self, board ):
        for i in range( self.size ):
            for j in range( self.size ):
                if self.matrix[i][j] != board.matrix[i][j]:
                    return False
        return True
    
    def AllLocationsOfState( self, state ):
        for i in range( self.size ):
            for j in range( self.size ):
                if self.matrix[i][j] == state:
                    yield ( i, j )
    
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
    
    def AnalyzeGroups( self, for_who ):
        location_list = [ location for location in self.AllLocationsOfState( for_who ) ]
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
                    if adjacent_location in queue:
                        continue
                    if self.GetState( adjacent_location ) == for_who:
                        queue.append( adjacent_location )
            if for_who != self.EMPTY:
                for location in group[ 'location_list' ]:
                    for adjacent_location in self.AdjacentLocations( location ):
                        if self.GetState( adjacent_location ) == self.EMPTY:
                            group[ 'liberties' ] += 1
            else:
                del group[ 'liberties' ]
            group_list.append( group )
        return group_list
    
    def CalculateTerritory( self ):
        territory = {
            self.WHITE : 0,
            self.BLACK : 0,
        }
        group_list = self.AnalyzeGroups( self.EMPTY )
        for group in group_list:
            location_list = group[ 'location_list' ]
            touch_map = {
                self.WHITE : set(),
                self.BLACK : set(),
            }
            for location in location_list:
                for adjacent_location in self.AdjacentLocations( location ):
                    state = self.GetState( adjacent_location )
                    if state != self.EMPTY:
                        touch_map[ state ].add( adjacent_location )
            white_touch_count = len( touch_map[ self.WHITE ] )
            black_touch_count = len( touch_map[ self.BLACK ] )
            group[ 'owner' ] = None
            if white_touch_count > 0 and black_touch_count == 0:
                group[ 'owner' ] = self.WHITE
            elif black_touch_count > 0 and white_touch_count == 0:
                group[ 'owner' ] = self.BLACK
            else:
                pass
                # Here we may be able to claim that neither owns the territory,
                # because we must capture all "dead stones" before making our calculation.
            owner = group[ 'owner' ]
            if owner:
                territory[ owner ] += len( location_list )
        return territory, group_list
    
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