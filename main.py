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

@app.route('/', methods=['GET'])
def root():
    # TODO Add button to start new game
    return render_template('index.html')

@app.route('/newgame', methods=['GET'])
def newgame():
    board.clear()   # Reset board state
    board.start()
    game.start()
    return redirect('/play')

@app.route('/play', methods=['GET', 'POST'])
def play():
    # Player input will be passed through POST
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
                # ui.errmsg = f'Invalid move for {game.turn} player. Try again.'
                ui.errmsg = e.msg
                return render_template('chess.html', ui=ui)
            board.update(move)
            ui.board = board.as_str()
            history.push(move)
            promote_coord = board.pawns_to_promote(move.player)
            if promote_coord is not None:
                ui.errmsg = None
                col, row = promote_coord
                return redirect('/promote', coord=f'{col}{row}')

        # Prompt for promotion display
        # Called when:
        # 1. There are pawns to be promoted at end of player's turn
        elif 'promote_to' in request.form.keys():
            digits = request.form['coord']
            coord = (digits[0], digits[1])
            promote_to = request.form['promote'].lower()
            if promote_to in 'rkbq':
                board.promote_pawn(coord,
                                   promote_to,
                                   push_to=history.this_move(),
                                   )
            else:
                ui.errmsg = 'Invalid input (r, k, b, or q only). Please try again.'
                return redirect('/promote', coord=digits)
        
        # Player turn expected to be complete if
        # this point is reached
        game.next_turn()

    ui.winner = board.winner()
    ui.inputlabel = f'{game.turn.title()} player:'
    ui.btnlabel = 'Move'
    ui.board = board.as_str()
    ui.undo = (not history.isempty())
    # ui.debugmsg = board.as_str()
    return render_template('chess.html', ui=ui)

@app.route('/promote')
def promote():
    digits = request.args['coord']
    coord = (digits[0], digits[1])
    ui.board = board.as_str()
    ui.inputlabel = f'Promote pawn at {coord} to (r, k, b, q): '
    ui.btnlabel = 'Promote'
    return render_template('chess.html', ui=ui)

@app.route('/undo')
def undo():
    breakpoint()
    move = history.pop()
    board.undo(move)
    game.next_turn()
    return redirect('/play')

app.run(host='0.0.0.0')