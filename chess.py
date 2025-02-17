from common import vector, Move
from pieces import King, Queen, Bishop, Knight, Rook, Pawn
from errors import (MoveError,
                    InvalidMoveError,
                    InvalidPieceMovedError,
                    DestinationIsBlockedError,
                    InputError,
                    )

PIECE = {
    'king': King,
    'queen': Queen,
    'bishop': Bishop,
    'knight': Knight,
    'rook': Rook,
    'pawn': Pawn,
}



class GameMaster:
    '''
    The GameMaster is responsible for:

    1. Prompting the player for a move
    2. Checking if the move is valid
       (and re-prompting the player)
    3. Checking if a player has won,
       and checking game status
    '''
    def __init__(self):
        self.turn = None

    @classmethod
    def fromdoc(cls, doc):
        game = cls()
        game.turn = doc['turn']
        return game
    
    def asdoc(self):
        return {'turn': self.turn}

    @staticmethod
    def format_move(start, end, movetype):
        return (f'{start} -> {end} {movetype}')

    def newgame(self):
        self.turn = 'white'
    
    def get_player_move(self, inputstr, **kwargs):
        '''
        Input format should be two ints,
        followed by a space,
        then another 2 ints
        e.g. 07 27
        '''
        def valid_format(inputstr):
            '''
            Ensure input is 5 characters: 2 numerals,
            followed by a space,
            followed by 2 numerals
            '''
            return len(inputstr) == 5 and inputstr[2] == ' ' \
                and inputstr[0:2].isdigit() \
                and inputstr[3:5].isdigit()
        
        def valid_num(inputstr):
            '''Ensure all inputted numerals are 0-7.'''
            for char in (inputstr[0:2] + inputstr[3:5]):
                if char not in '01234567':
                    return False
            return True
        
        def split_and_convert(inputstr):
            '''Convert 5-char inputstr into start and end tuples.'''
            start, end = inputstr.split(' ')
            start = (int(start[0]), int(start[1]))
            end = (int(end[0]), int(end[1]))
            return (start, end)

        if not valid_format(inputstr):
            raise InputError('Invalid input. Please enter your move in the following format: __ __, _ represents a digit.')
        elif not valid_num(inputstr):
            raise InputError('Invalid input. Move digits should be 0-7.')
        start, end = split_and_convert(inputstr)
        move = Move(start=start,
                    end=end,
                    player=self.turn,
                    )
        try:
            move.movetype = self.classify_move(move, board=kwargs['board'])
        except InvalidMoveError:
            raise
        else:
            return move

    def classify_move(self, move, **kwargs):
        '''
        Checks for the following conditions:
        1. Move is valid;
           Path between start and end coord is not blocked
           (for Rook, Bishop, Queen)
        ~~2. The move is a valid castling move~~
        3. For pawn piece, the move is:
           - pawn capture
           ~~- en passant capture~~
           - pawn move
        4. For other pieces, the move is valid for the selected piece
        
        Returns the type of move, otherwise raises InvalidMoveError
        '''
        def validatestartend(start, end):
            ''''
            Checks for the following conditions:
            1. There is a start piece of the player's colour,
            2. There is no end piece, or end piece is not of player's colour.
            Raises MoveError if conditions not met.
            '''
            start_piece = kwargs['board'].get_piece(start)
            end_piece = kwargs['board'].get_piece(end)
            # (1)
            if start_piece is None:
                raise InvalidPieceMovedError(move,
                    f'No player piece at {start}')
            if start_piece.colour != move.player:
                raise InvalidPieceMovedError(move, 
                    f'Piece at {start} does not belong to player')
            # (2)
            if end_piece is not None \
                    and end_piece.colour == move.player:
                raise DestinationIsBlockedError(move,
                    f'{end} is occupied by {end_piece}')

        def ispawncapture(start, end, colour):
            x, y, dist = vector(start, end)
            own_piece = kwargs['board'].get_piece(start)
            opp_piece = kwargs['board'].get_piece(end)
            if opp_piece is not None \
                    and opp_piece.colour != self.turn \
                    and abs(x) == 1:
                if own_piece.colour == 'white' and y == 1:
                    return True
                if own_piece.colour == 'black' and y == -1:
                    return True
            return False
        
        start_piece = kwargs['board'].get_piece(move.start)
        end_piece = kwargs['board'].get_piece(move.end)

        # (1)
        try:
            validatestartend(move.start, move.end)
        except MoveError:
            raise
        # (3)
        if start_piece.name == 'pawn':
            if ispawncapture(move.start, move.end, move.player):
                return 'pawncapture'
            if start_piece.isvalid(move.start, move.end):
                return 'move'
        # (4)
        elif start_piece.isvalid(move.start, move.end):
            if end_piece is not None:
                return 'capture'
            else:
                return 'move'
        raise InvalidMoveError(move,
            f'Invalid move for {start_piece}')

    def ischecked(self, **kwargs):
        '''
        Return True if current turn's king is checked,
        else return False.
        '''
        other_colour = 'white' if self.turn == 'black' else 'black'
        attkmove = Move(None,
                        player=other_colour,
                        )
        for own_king_coord in kwargs['board'].get_coords(self.turn, 'king'):
            attkmove.end = own_king_coord
            for opp_coord in kwargs['board'].coords(other_colour):
                attkmove.start = opp_coord
                try:
                    self.classify_move(attkmove,
                                        debug = False,
                                        board=kwargs['board'],
                                        )
                except MoveError:
                    return False
        return True

    def next_turn(self):
        '''Hand the turn over to the other player.'''
        if self.turn == 'white':
            self.turn = 'black'
        elif self.turn == 'black':
            self.turn = 'white'



class ChessBoard:
    '''
    The game board is represented as an 8×8 grid,
    with each position on the grid described as
    a pair of ints (range 0-7): col followed by row

    07  17  27  37  47  57  67  77
    06  16  26  36  46  56  66  76
    05  15  25  35  45  55  65  75
    04  14  24  34  44  54  64  74
    03  13  23  33  43  53  63  73
    02  12  22  32  42  52  62  72
    01  11  21  31  41  51  61  71
    00  10  20  30  40  50  60  70
    '''
    movetypes = {'pawncapture', 'capture', 'move'}
    def __init__(self):
        self.position = {}

    @classmethod
    def fromdoc(cls, doclist):
        board = cls()
        for doc in doclist:
            coord = (doc['x'], doc['y'])
            name = doc['piece']['name']
            Piece = PIECE[name]
            board.position[coord] = Piece(
                doc['piece']['colour'],
                doc['piece']['moved'],
            )
        return board

    def asdoc(self):
        doc = []
        for coord, piece in self.position.items():
            doc.append(
                {'x': coord[0],
                 'y': coord[1],
                 'piece': piece.asdoc()
                 }
            )
        return doc

    def coords(self, colour=None):
        '''
        Return list of piece coordinates.
        Filters for colour if provided in keyword argument.
        '''
        if colour in ('white', 'black'):
            return [coord for coord, piece in self.position.items() if piece.colour == colour]
        elif colour is None:
            return list(self.position.keys())
        else:
            raise ValueError('Invalid keyword argument colour={colour}')

    def pieces(self, colour=None):
        '''
        Return list of board pieces.
        Filters for colour if provided in keyword argument.
        '''
        if colour in ('white', 'black'):
            return [piece for piece in self.position.values() if piece.colour == colour]
        elif colour is None:
            return list(self.position.values())
        else:
            raise ValueError('Invalid keyword argument colour={colour}')
    
    def get_coords(self, colour, name):
        '''
        Returns a list of coords of pieces matching the name and
        colour.
        Returns empty list if none found.
        '''
        pieces = [i for i in self.coords() 
                  if self.get_piece(i).name == name
                  and self.get_piece(i).colour == colour
                  ]
        return pieces
    
    def get_piece(self, coord):
        '''
        Return the piece at coord.
        Returns None if no piece at coord.
        '''
        return self.position.get(coord, None)

    def add(self, coord, piece):
        '''Add/replace a piece at coord.'''
        if self.get_piece(coord) is not None:
            self.remove(coord)
        self.position[coord] = piece

    def remove(self, coord):
        '''
        Remove the piece at coord, if any.
        Does nothing if there is no piece at coord.
        '''
        if coord in self.coords():
            del self.position[coord]

    def move(self, start, end):
        '''
        Move the piece at start to end.
        Validation should be carried out first
        to ensure the move is valid.
        '''
        piece = self.get_piece(start)
        piece.moved = True
        self.remove(start)
        self.add(end, piece)

    def clear(self):
        '''Clear all pieces off the board.'''
        for coord in self.coords():
            self.remove(coord)

    def newgame(self):
        self.clear()
        colour = 'black'
        self.add((0, 7), Rook(colour))
        self.add((1, 7), Knight(colour))
        self.add((2, 7), Bishop(colour))
        self.add((3, 7), Queen(colour))
        self.add((4, 7), King(colour))
        self.add((5, 7), Bishop(colour))
        self.add((6, 7), Knight(colour))
        self.add((7, 7), Rook(colour))
        for x in range(0, 8):
            self.add((x, 6), Pawn(colour))

        colour = 'white'
        self.add((0, 0), Rook(colour))
        self.add((1, 0), Knight(colour))
        self.add((2, 0), Bishop(colour))
        self.add((3, 0), Queen(colour))
        self.add((4, 0), King(colour))
        self.add((5, 0), Bishop(colour))
        self.add((6, 0), Knight(colour))
        self.add((7, 0), Rook(colour))
        for x in range(0, 8):
            self.add((x, 1), Pawn(colour))

    def update(self, move):
        '''
        Update board information with the player's move.
        Update move information with added/removed pieces.
        '''
        self.move(move.start, move.end)

    def winner(self, **kwargs):
        white_king_alive = bool(self.get_coords('white', 'king'))
        black_king_alive = bool(self.get_coords('black', 'king'))
        if white_king_alive and black_king_alive:
            return None
        elif white_king_alive and not black_king_alive:
            return 'white'
        elif not white_king_alive and black_king_alive:
            return 'black'
        else:
            return None

    def as_str(self):
        '''
        Returns the contents of the board
        as a linebreak-delimited string.
        '''
        output = []
        # Row 7 is at the top, so print in reverse order
        for row in range(7, -1, -1):
            line = []
            for col in range(8):
                coord = (col, row)  # tuple
                if coord in self.coords():
                    line.append(f'{self.get_piece(coord).symbol()}')
                else:
                    line.append(' ')
            output.append(line)
        return output