# https://repl.it/@mrjsng/ChessFlask#main.py
# https://chessflask.mrjsng.repl.co/

from flask import Flask, render_template, redirect, request
from chess import GameMaster, ChessBoard
from interface import WebInterface
from errors import MoveError

## ER Model
'''
{                         ## Chess document
    game: {               ## Game document
        name: str,
        turn: str
    },
    board: {              ## Board document
        position: [
            {             ## Coord document
                x: int,
                y: int,
                piece: {  ## Piece document
                    colour: str,
                    name: str,
                    moved: bool
                }
            }
        ]
    }
}
'''

class DataStore:
    def __init__(self, uri):
        pass
    
    def load(self, label):
        '''
        Load data from the database using label.
        Deserialises data from the document and
        returns board and game objects.
        Assigns the label to game.name attribute.
        '''
        return board, game

    def save(self, board, game):
        '''
        Save data to the database.
        The label used should be obtained from game.name.
        Data from the board and game objects should
        be serialised before being sent to the database.
        '''
        pass

    def initgame(self, board, game):
        '''
        Checks the database to see if game data
        already exists.
        If it does not exist, insert a document
        with initial game data into the database.
        '''
        pass

def save_to_json(label):
    '''
    Writes the data for the game to a json file.
    '''
    pass

## Constants
COLL = 'your_group_name' # Use your group name as the collection name
URI = 'mongodb://mongo:ktnHJtg7vBmc@cluster0-shard-00-00.iol15.mongodb.net:27017,cluster0-shard-00-01.iol15.mongodb.net:27017,cluster0-shard-00-02.iol15.mongodb.net:27017/h2_computing?ssl=true&replicaSet=atlas-14p70c-shard-0&authSource=admin&retryWrites=true&w=majority'



## Initialise global objects
ui = WebInterface()
board = ChessBoard()
game = GameMaster()
datastore = DataStore(URI)



## FLASK APP START
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/newgame', methods=['GET'])
def newgame():
    # game label is passed through request.args via the 'game' key
    board.newgame()
    game.newgame()
    game.name = request.args['game']
    datastore.initgame(board, game)  # <-- initialise game in database
    return redirect('/play')

@app.route('/load', methods=['GET'])
def loadgame():
    # game label is passed through request.args via the 'game' key
    global board, game  # <-- ensure that database is loaded to global var and not local
    board, game = datastore.load(request.args['game'])  # <-- load data from database
    return redirect('/play')

@app.route('/play', methods=['GET', 'POST'])
def play():
    # Player input will be passed through POST request
    # Any GET request can be assumed to not contain move info;
    # go straight to ui update
    ui.errmsg = None
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
        datastore.save(board, game)  # <-- save data to database
        ui.board = board.as_str()
        save_to_json(game.name)  # <-- save data to json file

    ui.winner = board.winner()
    ui.board = board.as_str()
    ui.inputlabel = f'{game.turn.title()} player:'
    ui.btnlabel = 'Move'
    ui.action = '/play'
    # ui.debugmsg = board.as_str()
    return render_template('chess.html', ui=ui)

app.run(host='0.0.0.0')