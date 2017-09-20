# go_main.py

import re
import argparse

from go_game import GoGame
from go_board import GoBoard

if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument( '--size', help = 'Indicate the desired size of Go board.  7 is the default.', type = str )
    
    args = arg_parser.parse_args()
    
    size = int( args.size ) if args.size else 7
    go_game = GoGame( size )
    
    while go_game.consecutive_pass_count < 2:
        try:
            go_game.Print()
            
            if go_game.whose_turn == GoBoard.WHITE:
                whose_turn = 'WHITE'
            else:
                whose_turn = 'BLACK'
                
            command = input( whose_turn + ': ' )
            if command == 'exit':
                break
            elif command == 'pass':
                go_game.PlaceStone( -1, -1 )
            elif command == 'analyze':
                go_game.PrintAnalysis()
            else:
                match = re.match( r'\(([0-9]+),([0-9]+)\)', command )
                if match:
                    i = int( match.group(1) )
                    j = int( match.group(2) )
                    go_game.PlaceStone( i, j )
                else:
                    raise Exception( 'Failed to parse command: ' + command )
                    
        except Exception as ex:
            print( 'Exception: ' + str(ex) )