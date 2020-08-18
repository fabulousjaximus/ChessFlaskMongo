class MoveError(Exception):
    def __init__(self, move, msg):
        self.move = move
        self.msg = msg

        super().__init__(f'{move.start} -> {move.end}: {self.msg}')

class InvalidPieceMovedError(MoveError):
    pass

class DestinationIsBlockedError(MoveError):
    pass

class PathIsBlockedError(MoveError):
    pass

class InvalidMoveError(MoveError):
    pass

class InvalidPawnCaptureError(InvalidMoveError):
    pass

class InvalidCastlingError(InvalidMoveError):
    pass

class InputError(ValueError):
    def __init__(self,  msg):
        self.msg = msg

        super().__init__(self.msg)

class InvalidBoardError(Exception):
    pass

class PromptPromotionPiece(Exception):
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.prompt = kwargs.get('prompt')
        self.coord = kwargs.get('coord')
        super().__init__(self.msg)

class UndoError(Exception):
    def __init__(self, change, msg):
        self.change = change
        self.msg = msg

        super().__init__(f'{self.msg}')
