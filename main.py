# https://repl.it/@mrjsng/ChessFlask#main.py
# https://chessflask.mrjsng.repl.co/

from flask import Flask, render_template, redirect, request
from chess import GameMaster, ChessBoard
from interface import WebInterface
from movehistory import MoveHistory
from errors import MoveError

app = Flask(__name__)

ui = WebInterface()
board = ChessBoard()
game = GameMaster()
history = MoveHistory(10)

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
                                            step=(history.step + 1),
                )
            except MoveError as e:
                ui.errmsg = e.msg
                return render_template('chess.html', ui=ui)
            board.update(move, push_to=move)
            ui.board = board.as_str()
            history.push(move)
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
    ui.undo = (not history.isempty())
    ui.action = '/play'
    # ui.debugmsg = board.as_str()
    return render_template('chess.html', ui=ui)

@app.route('/promote', methods=['GET', 'POST'])
def promote():
    # /promote path must always have coord in GET parameter so that
    # board knows where the pawn to be promoted is
    digits = request.args['coord']
    coord = (digits[0], digits[1])
    # Process pawn promotion
    # Player will be prompted for another input if invalid
    if request.METHOD == 'POST':
        char = request.form['player_input'].lower()
        if char in 'rkbq':
            board.promote_pawn(coord,
                               char,
                               push_to=history.this_move(),
                               )
            return redirect('/play')
        else:
            ui.errmsg = 'Invalid input (r, k, b, or q only). Please try again.'
            return redirect('/promote', coord=digits)
    ui.board = board.as_str()
    ui.inputlabel = f'Promote pawn at {coord} to (r, k, b, q): '
    ui.btnlabel = 'Promote'
    ui.action = '/promote'
    return render_template('chess.html', ui=ui)

@app.route('/undo')
def undo():
    move = history.pop()
    board.undo(move)
    game.next_turn()
    return redirect('/play')

app.run(host='0.0.0.0')