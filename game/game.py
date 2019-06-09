import uuid
import json
from enum import Enum
import logging
import exceptions

BOARD_SIZE = 3

logger = logging.getLogger('game.game')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class GameState(Enum):
    NEW = "new"
    IN_PROGRESS = "in progress"
    DRAW = "draw"
    WIN_1 = "player 1 won"
    WIN_2 = "player 2 won"

class Players(Enum):
    PLAYER1 = 0
    PLAYER2 = 1

class Game(object):
    """ An instance of a Tic Tac Toe game

        Attributes:
        id          The game identifier
        player1     The name of the player 1
        player2     The name of the player 2
        state       The state of the game (new, in progress, draw, win)
        board       The current state of the board, as 2D list
        history     The list of moves in the form of move coordinates
    """
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.id = str(uuid.uuid4())
        self.state = GameState.NEW
        self.board = [[None for _ in range(BOARD_SIZE)]
                      for _ in range(BOARD_SIZE)]
        self.history = []

        logger.info("[%s] Game created" % self.id)

    def makeMove(self, payload):
        """ Validate input board and update the game state to reflect 
            the last move

            Raises:
                InvalidMove       - The new board state could not be 
                                    reached from the previous one
                GameNotInProgress - The game is already over
        """
        newBoard = payload['board']

        logger.debug("[%s] Preparing to make move %s" % (self.id, newBoard))

        # Only allow move if the game hasn't finished yet
        if self.state in [GameState.NEW, GameState.IN_PROGRESS]:
            if self.isMoveValid(newBoard):
                self.board = newBoard
                self.updateState()
            else:
                raise exceptions.InvalidMove(
                    "[%s] Move was not valid: %s" % (self.id, newBoard))
        else:
            raise exceptions.GameNotInProgress(
                "[%s] Game has finished already" % self.id)

    def isMoveValid(self, board):
        """ This method check if the if the turn is correct and if the 
            difference is in 1 cell only 
            
            Arguments:
                board - 2D list of cells representing the desired state 
                        after the move
            Returns:
                boot - True, if the move is valid, False otherwise

            Raises:
                InvalidMove   - The new board state could not be reached
                                from the previous one
                MoveNotInTurn - The move was made by a wrong player
            """

        # Check the current turn.
        # Player 1 - if the total number of cells in the previous board
        # is even (0)
        # Player 2 - if the total number of cells in the previous board 
        # is odd  (1)
        count = self.countMarks()
        turn = Players.PLAYER1.value if count % 2 == 0 else \
               Players.PLAYER2.value

        logger.debug("[%s] Expecting turn from player %s" % 
                     (self.id, Players(turn).name))

        # Locate the differences between previous board and new board
        # by comparing every cell
        diff = 0
        currentTurn = None
        exception = None
        for i in range(0, BOARD_SIZE):
            for j in range(0, BOARD_SIZE):
                if self.board[i][j] != board[i][j]:
                    logger.debug(
                        "[%s] Value changed from %s to %s in cell (%d, %d)" %
                        (self.id, self.board[i][j], board[i][j], i, j))

                    if board[i][j] == None:
                        exception = exceptions.InvalidMove(
                            "[%s] Value in cell (%d, %d) was unset" %
                            (self.id, i, j)) \
                            if not exception else None

                    if self.board[i][j] != None:
                        exception = exceptions.InvalidMove(
                            "[%s] Value %s replaced %s in cell (%d, %d)" %
                            (self.id, board[i][j], self.board[i][j], i, j)) \
                            if not exception else None

                    if board[i][j] != turn:
                        exception = exceptions.MoveNotInTurn(
                            "[%s] %s made a move out of turn \
                             in cell (%d, %d)" %
                            (self.id, Players(board[i][j]).name, i, j)) \
                            if not exception else None

                    diff += 1
                    if diff == 1:
                        currentTurn = {'x': i, 'y': j}

        if diff == 0:
            raise exceptions.InvalidMove(
                "[%s] No turns have been made" % (self.id))
        elif diff > 1:
            raise exceptions.InvalidMove(
                "[%s] More than one change has been detected" % (self.id))
        elif exception:
            raise exception # pylint: disable=E0702

        self.history.append(currentTurn)

        return True

    def countMarks(self):
        """ Counts the number of non-empty cells on the board
        """
        count = 0
        for i in range(0, BOARD_SIZE):
            for j in range(0, BOARD_SIZE):
                if self.board[i][j] is not None:
                    count += 1

        return count

    def updateState(self):
        """ Check the current situation and update the status
            if the board is in final state (draw or win)
        """
        logger.debug("[%s] Checking empty space" % self.id)
        # Check free space
        count = self.countMarks()
        if count == BOARD_SIZE * BOARD_SIZE:
            logger.info("[%s] Draw" % self.id)
            self.state = GameState.DRAW
            return

        # Check diagonals
        winFound = False
        logger.debug(
            "[%s] Checking the first diagonal" % self.id)
        start = self.board[0][BOARD_SIZE - 1]
        if start is not None:
            winFound = True
            for i in range(1, BOARD_SIZE):
                if (self.board[i][BOARD_SIZE - i - 1] != start):
                    winFound = False
                    break

        if winFound:
            self.updateStateOnWin(start)
            return

        logger.debug(
            "[%s] Checking the second diagonal" % self.id)
        start = self.board[0][0]
        if start is not None:
            winFound = True
            for i in range(1, BOARD_SIZE):
                if (self.board[i][i] != start):
                    winFound = False
                    break

        if winFound:
            self.updateStateOnWin(start)
            return

        # Check horizontals
        logger.debug("[%s] Checking horizontals" % (self.id))
        for i in range(0, BOARD_SIZE):
            start = self.board[i][0]
            if start is not None:
                winFound = True
                for j in range(1, BOARD_SIZE):
                    if (self.board[i][j] != start):
                        winFound = False
                        break

                if winFound:
                    self.updateStateOnWin(start)
                    return

        # Check verticals
        logger.debug("[%s] Checking verticals" % (self.id))
        for j in range(0, BOARD_SIZE):
            start = self.board[0][j]
            if start is not None:
                winFound = True
                for i in range(1, BOARD_SIZE):
                    if (self.board[i][j] != start):
                        winFound = False
                        break

                if winFound:
                    self.updateStateOnWin(start)
                    return

        self.state = GameState.IN_PROGRESS

        return

    def toDict(self):
        """ Convert the object into a dict suitable for JSON conversion """
        return {
            "player1": self.player1,
            "player2": self.player2,
            "id": self.id,
            "state": self.state.value,
            "board": self.board,
            "history": self.history
        }

    def updateStateOnWin(self, value):
        """ Update the state of the game according to the winner """
        self.state = GameState.WIN_1 if value == 0 else GameState.WIN_2
        logger.info("[%s] Winner found: %s" % (self.id, self.state.value))