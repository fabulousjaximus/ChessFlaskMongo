# https://repl.it/@mrjsng/ChessFlask#main.py
# https://chessflask.mrjsng.repl.co/

from flask import Flask, render_template, redirect, request
from chess import GameMaster, ChessBoard
from interface import WebInterface
from errors import MoveError

app = Flask(__name__)

ui = WebInterface()
board = ChessBoard()
game = GameMaster()

# We assume that white and black player are seated at the same keyboard and taking turns.
# Hence black player can undo her move after turn switches to white player. 

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/newgame', methods=['GET'])
def newgame():
    board.clear()   # Reset board state
    board.start()
    game.start()
    return redirect('/play')

@app.route('/play', methods=['GET', 'POST'])
def play():
    # Player input will be passed through POST request
    # Any GET request can be assumed to not contain move info
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # Normal board display
        # Called when:
        # 1. Prev player turn completed normally
        # 2. Move is not valid (display error)
        if 'player_input' in request.form.keys():
            try:
                move = game.get_player_move(request.form['player_input'],
                                            board=board,
                )
            except MoveError as e:
                ui.errmsg = e.msg
                return render_template('chess.html', ui=ui)
            board.update(move)
            ui.board = board.as_str()
            # Redirect for promotion prompt
            # Called when:
            # 1. There are pawns to be promoted at end of player's turn
            promote_coord = board.pawns_to_promote(move.player)
            if promote_coord is not None:
                ui.errmsg = None
                col, row = promote_coord
                return redirect('/promote', coord=f'{col}{row}')

        # Player turn expected to be complete if
        # this point is reached
        game.next_turn()

    ui.winner = board.winner()
    ui.board = board.as_str()
    ui.inputlabel = f'{game.turn.title()} player:'
    ui.btnlabel = 'Move'
    ui.action = '/play'
    # ui.debugmsg = board.as_str()
    return render_template('chess.html', ui=ui)

app.run(host='0.0.0.0')