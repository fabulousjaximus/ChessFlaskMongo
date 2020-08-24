class WebInterface:
    '''A wrapper for ui attributes (str type).'''
    def __init__(self):
        self.inputlabel = None
        self.btnlabel = None
        self.errmsg = None
        self.board = None
        self.debugmsg = None
        self.winner = None
        self.undo = False
        self.action = None
