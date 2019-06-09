import json
import flask
import uuid
import logging

import game.exceptions as exceptions
from game.game import Game

# Keeps the list of all current games
allGames = {}

logger = logging.getLogger('api.core')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def getGames():
    """ Returns the list of all games in JSON format """
    return flask.jsonify({k: (v.toDict()) for k, v in allGames.items()})

def getGame(gameId):
    """ Retrieves the game by ID or HTTP 404 if not found """
    if gameId not in allGames:
        data = {"Error": "Game with ID %s was not found" % gameId}
        resp = flask.jsonify(data)
        resp.status_code = 404
        flask.abort(resp)

    return flask.jsonify(allGames[gameId].toDict())


def createGame(player1, player2):
    """ Start a new game for 2 provided players """
    newGame = Game(player1, player2)

    allGames[newGame.id] = newGame

    return flask.jsonify(newGame.toDict()), 201


def updateGame(gameId):
    """ Make the next move in the game """
    payload = flask.request.json

    game = allGames.get(gameId)

    if not game:
        data = {"Error": "Game with ID %s was not found" % gameId}
        resp = flask.jsonify(data)
        resp.status_code = 404
        flask.abort(resp)

    try:
        game.makeMove(payload)
    except (exceptions.InvalidMove, exceptions.MoveNotInTurn,
            exceptions.GameNotInProgress) as e:
        data = {"Error": "%s" % e}
        resp = flask.jsonify(data)
        resp.status_code = 409
        flask.abort(resp)

    return flask.jsonify(game.toDict()), 200
