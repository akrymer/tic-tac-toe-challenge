# Define Python user-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class GameNotInProgress(Error):
   """Raised when the move is made in the completed game"""
   pass

class MoveNotInTurn(Error):
   """Raised when the move was made during another player's turn"""
   pass

class InvalidMove(Error):
   """Raised when the input board state could not be reached from the previous one in one turn"""
   pass
