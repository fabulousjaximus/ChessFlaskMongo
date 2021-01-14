from copy import copy
from errors import (MoveError,
                    InvalidMoveError,
                    InvalidPieceMovedError,
                    DestinationIsBlockedError,
                    PathIsBlockedError,
                    InputError,
                    UndoError,
                    )



def vector(start, end):
    '''
    Return three values as a tuple:
    - x, the number of spaces moved horizontally,
    - y, the number of spaces moved vertically,
    - dist, the total number of spaces moved.
    
    positive integers indicate upward or rightward direction,
    negative integers indicate downward or leftward direction.
    dist is always positive.
    '''
    x = end[0] - start[0]
    y = end[1] - start[1]
    dist = abs(x) + abs(y)
    return x, y, dist

def debugmsg(msg):
    print('[DEBUG]', msg)



class Move:
    def __init__(self, step, **kwargs):
        # TODO: consider how add/remove will affect piece.move attrib
        self.step = step
        self.player = kwargs['player']
        self.start = kwargs['start']
        self.end = kwargs['end']
        self.movetype = kwargs.get('movetype')
        self.changes = kwargs.get('changes', [])
    
    def push(self, **kwargs):
        action = kwargs['action']
        coord = kwargs['coord']
        piece = kwargs['piece']
        if type(action) != str:
            raise TypeError('str expected for action argument')
        if action not in ('add', 'remove'):
            raise ValueError('action must be add or remove')
        if type(coord) != tuple and len(coord) != 2:
            raise TypeError('invalid coordinates provided')
        # Store a copy of piece to preserve moved attribute value
        self.changes.append({'action': action,
                             'coord': coord,
                             'piece': copy(piece),
                             })
    
    def pop(self):
        if len(self.changes) > 0:
            return self.changes.pop()
        else:
            raise IndexError('no changes to pop from history')



class BasePiece:
    name = 'piece'
    def __init__(self, colour):
        if type(colour) != str:
            raise TypeError('colour argument must be str')
        elif colour.lower() not in {'white', 'black'}:
            raise ValueError('colour must be {white, black}')
        else:
            self.colour = colour
            self.moved = 0
    
    def __eq__(self, other):
        return (self.name == other.name) and (self.colour == other.colour)

    def __repr__(self):
        return f'BasePiece({repr(self.colour)})'

    def __str__(self):
        return f'{self.colour} {self.name}'

    def symbol(self):
        return f'{self.sym[self.colour]}'


class King(BasePiece):
    name = 'king'
    sym = {'white': '♔', 'black': '♚'}
    def __repr__(self):
        return f"King('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''
        King can move one step in any direction
        horizontally, vertically, or diagonally.
        '''
        x, y, dist = vector(start, end)
        return (dist == 1) or (abs(x) == abs(y) == 1)

    
class Queen(BasePiece):
    name = 'queen'
    sym = {'white': '♕', 'black': '♛'}
    def __repr__(self):
        return f"Queen('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''
        Queen can move any number of steps horizontally,
        vertically, or diagonally.
        '''
        x, y, dist = vector(start, end)
        return (abs(x) == abs(y) != 0) \
            or ((abs(x) == 0 and abs(y) != 0) \
            or (abs(y) == 0 and abs(x) != 0))


class Bishop(BasePiece):
    name = 'bishop'
    sym = {'white': '♗', 'black': '♝'}
    def __repr__(self):
        return f"Bishop('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''Bishop can move any number of steps diagonally.'''
        x, y, dist = vector(start, end)
        return (abs(x) == abs(y) != 0)


class Knight(BasePiece):
    name = 'knight'
    sym = {'white': '♘', 'black': '♞'}
    def __repr__(self):
        return f"Knight('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''
        Knight moves 2 spaces in any direction, and
        1 space perpendicular to that direction, in an L-shape.
        '''
        x, y, dist = vector(start, end)
        return (dist == 3) and (abs(x) != 3 and abs(y) != 3)


class Rook(BasePiece):
    name = 'rook'
    sym = {'white': '♖', 'black': '♜'}
    def __repr__(self):
        return f"Rook('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''
        Rook can move any number of steps horizontally
        or vertically.
        '''
        x, y, dist = vector(start, end)
        return (abs(x) == 0 and abs(y) != 0) \
            or (abs(y) == 0 and abs(x) != 0) 


class Pawn(BasePiece):
    name = 'pawn'
    sym = {'white': '♙', 'black': '♟︎'}
    def __repr__(self):
        return f"Pawn('{self.colour}')"

    def isvalid(self, start: tuple, end: tuple):
        '''Pawn can only move 1 step forward.'''
        x, y, dist = vector(start, end)
        if x == 0:
            if self.colour == 'black':
                if self.moved:
                    return (y == -1)
                else:
                    return (0 > y >= -2)
            elif self.colour == 'white':
                if self.moved:
                    return (y == 1)
                else:
                    return (0 < y <= 2)
        return False



class GameMaster:
    '''
    The GameMaster is responsible for:

    1. Prompting the player for a move
    2. Checking if the move is valid
       (and re-prompting the player)
    3. Passing the move to the board for updating
    4. Checking if a player has won,
       and checking game status
    '''
    def __init__(self, **kwargs):
        self.inputf = kwargs.get('inputf', input)
        self.printf = kwargs.get('printf', print)

    @staticmethod
    def format_move(start, end, movetype):
        return (f'{start} -> {end} {movetype}')

    def start(self, **kwargs):
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
        move = Move(kwargs['step'],
                    start=start,
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

        def validatepathblocked(start, end):
            '''
            Checks if the path between start and end is not
            occupied by any pieces.
            Raises MoveError if conditions not met.
            '''
            piece = kwargs['board'].get_piece(start)
            if piece.name.lower() != 'knight':
                for coord in kwargs['board'].coords_between(start, end):
                    if kwargs['board'].get_piece(coord) is not None:
                        raise PathIsBlockedError(move,
                f'Path from {start} to {end} is blocked')

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
            validatepathblocked(move.start, move.end)
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
    movetypes = {'pawncapture', 'enpassant', 'castling', 'capture', 'move'}
    def __init__(self, **kwargs):
        self.position = {}
        self.debug = kwargs.get('debug', False)

    @staticmethod
    def vector(start, end):
        '''
        Return three values as a tuple:
        - x, the number of spaces moved horizontally,
        - y, the number of spaces moved vertically,
        - dist, the total number of spaces moved.
        
        positive integers indicate upward or rightward direction,
        negative integers indicate downward or leftward direction.
        dist is always positive.
        '''
        x = end[0] - start[0]
        y = end[1] - start[1]
        dist = abs(x) + abs(y)
        return x, y, dist

    @classmethod
    def coords_between(cls, start, end):
        '''
        Return list of coordinates between start and end coord.
        List does not include start coord but includes end coord.
        Move must be horizontal, vertical, or diagonal only.
        '''
        x, y, dist = vector(start, end)
        if dist == 0:  # x == 0 and y == 0
            return []
        elif x == 0:  # vertical move
            incr = 1 if y > 0 else -1
            return [(start[0], row) for row in \
                    range(start[1] + incr, end[1], incr)]
        elif y == 0:  # horizontal move
            incr = 1 if x > 0 else -1
            return [(col, start[1]) for col in \
                    range(start[0] + incr, end[0], incr)]
        elif abs(x) == abs(y):
            y_incr = 1 if y > 0 else -1
            x_incr = 1 if x > 0 else -1
            cols = [(col, start[1]) for col in \
                    range(start[0] + y_incr, end[0] + y_incr, y_incr)]
            rows = [(start[0], row) for row in \
                    range(start[1] + x_incr, end[1] + x_incr, x_incr)]
            return [(col, row) for col, row in zip(cols, rows)]
        else:
            raise InvalidMoveError(start, end, 'Not a horizontal, vertical, or diagonal move')
        
    def coords(self, colour=None):
        '''
        Return list of piece coordinates.
        Filters for colour if provided in keyword argument.
        '''
        if colour in ('white', 'black'):
            return [coord for coord, piece in self.position.items() if piece.colour == colour]
        elif colour is None:
            return self.position.keys()
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
            return self.position.values()
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

    def add(self, coord, piece, **kwargs):
        '''Add/replace a piece at coord.'''
        if self.get_piece(coord) is not None:
            self.remove(coord, push_to=kwargs.get('push_to'))
        self.position[coord] = piece
        if kwargs.get('push_to'):
            kwargs['push_to'].push(action='add',
                                coord=coord,
                                piece = piece,
                                )

    def remove(self, coord, **kwargs):
        '''
        Remove the piece at coord, if any.
        Does nothing if there is no piece at coord.
        '''
        if coord in self.coords():
            if kwargs.get('push_to'):
                kwargs['push_to'].push(action='remove',
                                    coord=coord,
                                    piece = self.get_piece(coord),
                                    )
            del self.position[coord]

    def move(self, start, end, **kwargs):
        '''
        Move the piece at start to end.
        Validation should be carried out first
        to ensure the move is valid.
        '''
        piece = self.get_piece(start)
        self.remove(start, push_to=kwargs.get('push_to'))
        self.add(end, piece, push_to=kwargs.get('push_to'))

    def clear(self):
        '''Clear all pieces off the board.'''
        for coord in list(self.coords()):
            self.remove(coord)

    def start(self):
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

    def pawns_to_promote(self, colour):
        '''Returns the first coord of any pawn to be promoted'''
        if colour == 'white':
            enemy_home = 7
        elif colour == 'black':
            enemy_home = 0
        else:
            raise ValueError("colour must be {'white', 'black'}")
        for coord in self.get_coords(colour, 'pawn'):
            col, row = coord
            if row == enemy_home:
                # TODO: replace with raise PromptPromotionPiece
                # with 'msg' argument and 'prompt' kwarg
                return coord
        return None

    def promote_pawn(self, coord, char, **kwargs):
        piece_dict = {'r': Rook,
                     'k': Knight,
                     'b': Bishop,
                     'q': Queen,
                     }
        # Transfer old_piece move attributes to new_piece
        old_piece = self.get_piece(coord)
        new_piece = piece_dict[char.lower()](old_piece.colour)
        new_piece.moved = old_piece.moved
        self.add(coord, new_piece, push_to=kwargs.get('push_to'))

    def undo(self, move):
        while len(move.changes) > 0:
            change = move.changes.pop()
            if change['action'] == 'add':
                if self.get_piece(change['coord']) is not None \
                and self.get_piece(change['coord']) != change['piece']:
                    raise UndoError('history piece does not match board piece')
                else:
                    # Do not push move to history
                    self.remove(change['coord'])
            elif change['action'] == 'remove':
                self.add(change['coord'], change['piece'])


    def update(self, move, **kwargs):
        '''
        Update board information with the player's move.
        Update move information with added/removed pieces.
        '''
        end_piece = self.get_piece(move.end)

        # Remove opponent piece to be captured
        if move.movetype == 'capture':
            move.push(action='remove', coord=move.end, piece=end_piece)
        elif move.movetype == 'enpassantcapture':
            s_col, s_row = move.start
            e_col, e_row = move.end
            enpassant_coord = (s_row, e_col)
            self.remove(enpassant_coord, push_to=move)

        self.move(move.start, move.end, push_to=move)

        # Move rook for castling
        if move.movetype == 'castling':
            s_col, s_row = move.start
            e_col, e_row = move.end
            if e_col < s_col:    # castle leftward
                rook_start, rook_end = (0, s_row), (3, e_row)
            elif e_col > s_col:  # castle rightward
                rook_start, rook_end = (7, s_row), (5, e_row)
            piece = self.get_piece(rook_start)
            assert piece.name == 'rook', f'Piece at {rook_start} is not a rook'
            self.move(rook_start, rook_end, push_to=kwargs.get('push_to'))

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
            debugmsg('Neither king is on the board')

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