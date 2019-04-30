import requests
import chess
from time import sleep
class BotHandler():
    def __init__(self):
        self.url = "https://api.telegram.org/bot876799383:AAEb3lfEJezY5utjCGSWHMudMk7gAExnTFk/"
        self.general_offset = None
        self.chat_id = 306246284


    def get_updates(self):
        method = 'getUpdates'
        params = {'offset': self.general_offset}
        resp = requests.get(self.url + method, params)
        result_json = resp.json()['result']
        if len(result_json) > 0:
            self.general_offset = result_json[-1]['update_id'] + 1
        return result_json

    def send_message(self, text):
        params = {'chat_id': self.chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.url + method, params)
        return resp

a = BotHandler()
board = chess.Board()

def action():
    while True:
        arr = a.get_updates()
        if arr != []:
            return arr[-1]['message']['text']
        sleep(2)

def mistake():
    a.send_message("Wrong command. You`re directed to the start")

def check_result(colour):
    result = board.result()
    if result == '*':
        return False
    if_won = ((result == '1-0') ^ (colour == 'Black'))
    if result == '1/2-1/2':
        a.send_message("Draw")
    elif if_won:
        a.send_message("You won")
    else:
        a.send_message("You lose")
    return True

def make_move():
    fen = board.fen()
    fen = fen.replace('/', '%2F')
    fen = fen.replace(' ', '+')
    address = 'http://api.underwaterchess.com/game?fen=' + fen + '&move=&format=json'
    r = requests.get(address)
    mv = r.json()['turn']['bestMove']
    machine_move = chess.Move.from_uci(mv)
    view = board.san(machine_move)
    a.send_message(view)
    board.push(machine_move)

def suggestion():
    a.send_message("Make a move!")

def game():
    board.reset()
    a.send_message("Choose a colour. Send message White or Black")
    colour = action()
    if colour == 'White':
        pass
    elif colour == 'Black':
        make_move()
    else:
        mistake()
        return
    suggestion()
    while True:
        move = action()
        if move == '/resign':
            a.send_message("Thank you for the game!")
            return
        try:
            machine_move = board.parse_san(move)
        except:
            a.send_message("Wrong move")
            continue
        board.push(machine_move)
        if check_result(colour):
            return
        make_move()
        if check_result(colour):
            return
        suggestion()

def main():
    while True:
        message = action()
        if message == '/start_game':
            game()
        else:
            mistake()


main()
