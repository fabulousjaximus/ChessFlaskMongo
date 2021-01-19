# https://repl.it/@mrjsng/ChessFlask#main.py
# https://chessflask.mrjsng.repl.co/

from flask import Flask, render_template, redirect, request
import pymongo
from chess import GameMaster, ChessBoard
from interface import WebInterface
from errors import MoveError

app = Flask(__name__)

COLL = 'test'

class DataStore:
    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client.h2_computing
        self.coll = self.db[COLL]
    
    def init(self, board, game):
        '''Create collection and ensure that documents exist'''
        result = self.coll.update_one(
            {'name': game.name},
            {'$set': {
                'board': [],
                'game': None,
                }
            }
        )
        if result.matched_count == 0:
            self.coll.insert_one(
                {'name': game.name,
                 'board': [],
                 'game': None,
                },
            )
        self.save(board, game)

    def load(self, label):
        data = self.coll.find_one({'name': label})
        if not (data['board'] and data['game']):
            breakpoint()
        board = ChessBoard.fromdoc(data['board'])
        game = GameMaster.fromdoc(data['game'])
        game.name = label
        return board, game

    def save(self, board, game):
        self.coll.update_one(
            {'name': game.name},
            {'$set': {
                'board': board.asdoc(),
                'game': game.asdoc(),
                },
            },
        )

def save_data_to_json(label):
    import json
    doc = datastore.coll.find_one({'name': label})
    doc.pop('_id')
    with open('data.json', 'w') as f:
        json.dump(doc, f, indent=4)

URI = 'mongodb://mongo:ktnHJtg7vBmc@cluster0-shard-00-00.iol15.mongodb.net:27017,cluster0-shard-00-01.iol15.mongodb.net:27017,cluster0-shard-00-02.iol15.mongodb.net:27017/h2_computing?ssl=true&replicaSet=atlas-14p70c-shard-0&authSource=admin&retryWrites=true&w=majority'

ui = WebInterface()
board = ChessBoard()
game = GameMaster()
datastore = DataStore(URI)

# We assume that white and black player are seated at the same keyboard and taking turns.
# Hence black player can undo her move after turn switches to white player. 

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/newgame', methods=['GET'])
def newgame():
    board.newgame()
    game.newgame()
    game.name = request.args['game']
    datastore.init(board, game)
    return redirect('/play')

@app.route('/load', methods=['GET'])
def loadgame():
    global board, game
    board, game = datastore.load(request.args['game'])
    return redirect('/play')

@app.route('/play', methods=['GET', 'POST'])
def play():
    # Player input will be passed through POST request
    # Any GET request can be assumed to not contain move info;
    # go straight to ui update
    if  request.method == 'POST':
        # Normal board display
        # Called when:
        # 1. Prev player turn completed normally
        # 2. Move is not valid (display error)
        if 'player_input' in request.form.keys():
            try:
                move = game.get_player_move(
                    request.form['player_input'],
                    board=board,
                )
            except MoveError as e:
                ui.errmsg = e.msg
                return render_template('chess.html', ui=ui)
            board.update(move)
        # Player turn expected to be complete if
        # this point is reached
        game.next_turn()
        datastore.save(board, game)
        ui.board = board.as_str()
        save_data_to_json(game.name)

    ui.winner = board.winner()
    ui.board = board.as_str()
    ui.inputlabel = f'{game.turn.title()} player:'
    ui.btnlabel = 'Move'
    ui.action = '/play'
    # ui.debugmsg = board.as_str()
    return render_template('chess.html', ui=ui)

app.run(host='0.0.0.0')