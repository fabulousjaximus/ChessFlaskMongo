class MoveHistory:
    '''MoveHistory works like a CircularStack'''
    def __init__(self, size):
        if type(size) != int:
            raise TypeError('head must be type int')
        elif size <= 0:
            raise TypeError('size must be greater than 0')
        self.size = size
        self.__data = [None] * size
        self.head = None
        self.step = 0
    
    def isempty(self):
        return self.head is None

    def push(self, move):
        if self.isempty():
            self.head = 0
        else:
            self.head = (self.head + 1) % self.size
        self.__data[self.head] = move
        self.step += 1
            
    def pop(self):
        if self.isempty():
            raise IndexError('MoveHistory is empty')
        move = self.__data[self.head]
        self.__data[self.head] = None

        if self.head == 0:
            self.head = self.size - 1
        else:
            self.head -= 1
        self.step -= 1
        # If no value stored at new head,
        # we assume MoveHistory is empty
        if self.__data[self.head] is None:
            self.head = None

        return move

    def this_move(self):
        '''Return the current move object (which head points to).'''
        if self.isempty():
            raise IndexError('MoveHistory is empty')
        return self.__data[self.head]