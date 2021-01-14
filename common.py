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