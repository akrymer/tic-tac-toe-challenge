import game.exceptions as exceptions
from game.game import Game
from game.game import GameState

import json

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def testNewGame(self):
        player1 = "p1"
        player2 = "p2"
        game = Game(player1, player2)

        assert(game.id != None)
        assert(game.player1 == player1)
        assert(game.player2 == player2)
        assert(len(game.history) == 0)
        assert(game.state == GameState.NEW)
        assert(len(game.board) == 3)
        for i in range(3):
            assert(len(game.board[i]) == 3)
        assert(game.countMarks() == 0)

    def testGoodMoves(self):
        game = playGame('tests/goodMoves1.json')
        assert(game.state == GameState.WIN_1)
        assert(len(game.history) == 5)
        game = playGame('tests/goodMoves2.json')
        assert(game.state == GameState.WIN_2)
        assert(len(game.history) == 8)
        game = playGame('tests/goodMoves3.json')
        assert(game.state == GameState.WIN_1)
        assert(len(game.history) == 5)

    def testMoveAfterFinish(self):
        game = playGame('tests/goodMoves1.json')
        with self.assertRaises(exceptions.GameNotInProgress):
            game.makeMove({ 'board':[]})

    def testBadMoves(self):
        with self.assertRaises(exceptions.MoveNotInTurn):
            playGame('tests/doubleMove.json')

        with self.assertRaises(exceptions.MoveNotInTurn):
            playGame('tests/doubleMove.json')

        with self.assertRaises(exceptions.InvalidMove):
            playGame('tests/invalidMove.json')




def playGame(fileName):
    player1 = "p1"
    player2 = "p2"
    game = Game(player1, player2)

    with open(fileName) as json_file:  
        data = json.load(json_file)
        for move in data:
            game.makeMove(move)
    
    return game


if __name__ == '__main__':
    unittest.main()