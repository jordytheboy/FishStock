"""
Will contain an object for each piece
"""
import pygame
import copy
import sys
sys.setrecursionlimit(20000)

def chk_move(self, color, x, y, board):
    """
    Checks if a move is valid, if the coordinate on the board is empty,
    the move is valid, if the coordinate contains an enemy, the move is
    valid, if the coordinate is out of bounds or contains a friend, the
    move is invalid
    """
    if x < 0 or x > 7 or y < 0 or y > 7:
        # Out of bounds
        return False
    
    piece = board.board_[y][x]
    if piece == None:
        # Empty Space
        return True
    else:
        if piece.color != color:
            piece.attacked_by.add((self.x, self.y))
            # Enemy piece
            return True
        if piece.color == color:
            # Friend
            return False

    
def get_straight_moves(self,board):
    """
    Generates all possible legal horizontal and vertical moves
    Args:
        Instance of chess board
    Returns:
        plegal_moves - set containing tuples (x,y) of coordinates of each valid move
    """
    # Vertical moves
    plegal_moves = set()

    for i in(-1, 1):
        possible_y = self.y 
        while(True):
            possible_y += i

            if chk_move(self, self.color, self.x, possible_y, board):
                if (board.board_[possible_y][self.x] != None):
                    plegal_moves.add((self.x, possible_y))
                    self.attacking.add((self.x, possible_y))
                    break
                else:
                    plegal_moves.add((self.x, possible_y))
            else:
                break

    # Horizontal moves
    for i in(-1, 1):
        possible_x = self.x 
        while(True):
            possible_x += i

            if chk_move(self, self.color, possible_x, self.y, board):
                if (board.board_[self.y][possible_x] != None): # If there is an enemy piece
                    plegal_moves.add((possible_x, self.y))
                    self.attacking.add((possible_x, self.y))
                    break
                else: # If board is empty here
                    plegal_moves.add((possible_x, self.y))
            else:
                break

    return plegal_moves

def get_diag_moves(self,board):
    """
    Generates all possible legal diagonal moves
    Args:
        Instance of chess board
    Returns:
        plegal_moves - set containing tuples (x,y) of coordinates of each valid move
    """
    plegal_moves = set()

    for movement in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
        possible_x = self.x 
        possible_y = self.y
        while(True):
            possible_x += movement[0]
            possible_y += movement[1]
            if chk_move(self, self.color, possible_x, possible_y, board):
                if (board.board_[possible_y][possible_x] != None): # If there is an enemy piece
                    plegal_moves.add((possible_x, possible_y))
                    self.attacking.add((possible_x, possible_y))
                    break
                else: # If the board is empty here
                    plegal_moves.add((possible_x, possible_y))
            else:
                break
    return plegal_moves

class Piece():
    """
    Basic piece object, stores color and position
    """
    def __init__(self,color,x,y):
        self.x = x
        self.y = y
        self.color = color
        self.attacking = set()
        self.attacked_by = set()
        self.legal_moves = set()
    
    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def generate_moves(self, board):
        return set()

    def generate_legal_moves(self, board):
        """
        Generates the legal moveset of any given piece
        Legal meaning not putting the King into check
        """
        pseudo_moves = self.generate_moves(board)
        
        for move in pseudo_moves:
            # Copy the current piece
            testpiece = copy.copy(self)
            testpiece.x = move[0]
            testpiece.y = move[1]
            # Copy the board
            testboard = copy.deepcopy(board)
            # Remove the current piece from the board
            testboard.board_[self.y][self.x] = None
            # Move it to the test location
            testboard.board_[move[1]][move[0]] = testpiece
            # Set testboard king check status
            board.black_king.check_status()
            board.white_king.check_status()

            testboard.black_king.is_in_check = board.black_king.is_in_check
            testboard.white_king.is_in_check = board.white_king.is_in_check

            # Generate the pseudo-legal moves for the testboard pieces
            # This entire method is extremely slow, will need to optimize
            for row in testboard.board_:
                for item in row:
                    if item is not None:
                        item.generate_moves(testboard)

            # Now set the king status again
            testboard.black_king.check_status()
            testboard.white_king.check_status()
            
            # Now check if that moves results in the king going into check
            if self.color == 'w':
                if (testboard.white_king.is_in_check == False):
                    self.legal_moves.add((testpiece.x, testpiece.y))
            if self.color == 'b':
                print(board.black_king.is_in_check)
                if (testboard.black_king.is_in_check == False):
                    self.legal_moves.add((testpiece.x, testpiece.y))
        return self.legal_moves

class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wpawn.png'
        else: self.sprite = 'resources\\bpawn.png'


    def generate_moves(self, board):
        """
        Generates the possible legal moves, not accounting for check
        Args:
            Instance of the legal moves
        Returns:
            plegal_moves - set containing tuples (x,y) of coordinates of 
            each valid move
        """
        plegal_moves = set()

        direction = {'w': -1, 'b': 1}
        col = self.color

        possible_y = self.y + direction[col]
        """
        Cannot use the chk_move method, as the pawn cannot capture piece in occupied
        squares directly ahead of it
        """
        piece = board.board_[possible_y][self.x]
        if (possible_y >= 0 or possible_y <= 7) and piece == None:
            plegal_moves.add((self.x, possible_y))

        # Out of bounds or occupied, so check if the diagonally adjacent squares contain an enemy piece
        if (self.x+1 <= 7): # Check if the piece you're looking at is off the board
            enemy1 = board.board_[possible_y][self.x+1]
        else: enemy1 = None
        if (self.x-1 >= 0): # Check if the piece you're looking at is off the board
            enemy2 = board.board_[possible_y][self.x-1]
        else: enemy2 = None

        # Check if the two spaces contain an enemy
        if ((enemy1 is not None) and (enemy1.color != col)):
            self.attacking.add((self.x+1, possible_y))
            plegal_moves.add((self.x+1, possible_y))
        if ((enemy2 is not None) and (enemy2.color != col)):
            self.attacking.add((self.x-1, possible_y))
            plegal_moves.add((self.x-1, possible_y))
        return plegal_moves


    
class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wrook.png'
        else: self.sprite = 'resources\\brook.png'

    def generate_moves(self, board):
        return get_straight_moves(self, board)

class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wbishop.png'
        else: self.sprite = 'resources\\bbishop.png'

    def generate_moves(self, board):
        return get_diag_moves(self,board)

class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wknight.png'
        else: self.sprite = 'resources\\bknight.png'

    def generate_moves(self, board):
        plegal_moves = set()
        # Possible offset of the moves the knight can make from his starting position - starting(x,y) + (x, y)
        possible_moves = [(-1, 2), (1, 2), (-1, -2), (1, -2), (2, -1), (2, 1), (-2, -1), (-2, 1)]

        for move in possible_moves:
            possible_x = self.x + move[0]
            possible_y = self.y + move[1]
            if chk_move(self, self.color, possible_x, possible_y, board):
                plegal_moves.add((possible_x, possible_y))
                if (board.board_[possible_y][possible_x] is not None) and (board.board_[possible_y][possible_x].color != self.color):
                    self.attacking.add((possible_x, possible_y))
        return plegal_moves

class King(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wking.png'
        else: self.sprite = 'resources\\bking.png'
        self.is_in_check = False

    def generate_moves(self, board):
        plegal_moves = set()
        # Possible offset of the moves the king can make from his starting position
        possible_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1), (1, 0), (-1, 0), (0, -1), (0, 1)]

        for move in possible_moves:
            possible_x = self.x + move[0]
            possible_y = self.y + move[1]
            if chk_move(self, self.color, possible_x, possible_y, board):
                plegal_moves.add((possible_x, possible_y))
                if (board.board_[possible_y][possible_x] is not None) and (board.board_[possible_y][possible_x].color != self.color):
                    self.attacking.add((possible_x, possible_y))
        return plegal_moves

    def check_status(self):
        if len(self.attacked_by) != 0:
            self.is_in_check = True
        else: self.is_in_check = False
        

class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        if (color == 'w'):
            self.sprite = 'resources\\wqueen.png'
        else: self.sprite = 'resources\\bqueen.png'

    def generate_moves(self, board):
        return get_diag_moves(self,board).union(get_straight_moves(self,board))


