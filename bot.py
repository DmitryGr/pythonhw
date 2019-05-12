import requests
import chess
from time import sleep
class BotHandler():
    def __init__(self):
        self.url = "https://api.telegram.org/bot876799383:AAEb3lfEJezY5utjCGSWHMudMk7gAExnTFk/"
        self.general_offset = None

    def get_updates(self):
        method = 'getUpdates'
        params = {'offset': self.general_offset}
        resp = requests.get(self.url + method, params)
        result_json = resp.json()['result']
        real_res = []
        for element in result_json:
            if self.general_offset is None or element['update_id'] >= self.general_offset:
                real_res += [element]
        if len(real_res) > 0:
            self.general_offset = real_res[-1]['update_id'] + 1
        return real_res

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.url + method, params)
        return resp

a = BotHandler()

def mistake(chat_id):
    a.send_message(chat_id, "Wrong command. You`re directed to the start")

def check_result(board, colour):
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

def make_move(chat, board):
    fen = board.fen()
    fen = fen.replace('/', '%2F')
    fen = fen.replace(' ', '+')
    address = 'http://api.underwaterchess.com/game?fen=' + fen + '&move=&format=json'
    r = requests.get(address)
    mv = r.json()['turn']['bestMove']
    machine_move = chess.Move.from_uci(mv)
    view = board.san(machine_move)
    a.send_message(chat, view)
    board.push(machine_move)

def suggestion(chat_id):
    a.send_message(chat_id, "Make a move!")

def check_move(started_games, colours, games, action):
    move = action['message']['text']
    chat = action['message']['chat']['id']
    if move == '/resign':
        a.send_message(chat, "Thank you for the game!")
        games.pop(chat)
        started_games.remove(chat)
        return
    board = games[chat]
    try:
        machine_move = board.parse_san(move)
    except:
        a.send_message(chat, "Wrong move")
        return
    board.push(machine_move)
    colour = colours[chat]
    if check_result(board, colour):
        games.pop(chat)
        started_games.remove(chat)
        return
    make_move(chat, board)
    if check_result(board, colour):
        games.pop(chat)
        started_games.remove(chat)
        return
    suggestion(chat)

def start_game(started_games, action):
    text = action['message']['text']
    chat = action['message']['chat']['id']
    if text != "/start_game":
        mistake(chat)
        return
    started_games.add(chat)
    a.send_message(chat, "Choose a colour. Send message White or Black")


def check_colour(games, started_games, colours, action):
    text = action['message']['text']
    chat = action['message']['chat']['id']
    if text == 'White':
        games[chat] = chess.Board()
        colours[chat] = 'White'
        pass
    elif text == 'Black':
        games[chat] = chess.Board()
        colours[chat] = 'Black'
        make_move(chat, games[chat])
    else:
        started_games.remove(chat)
        mistake(chat)
        return
    suggestion(chat)

def delete_exceed(actions):
    real_actions = []
    was = set()
    for element in actions:
        if 'text' not in element['message']:
            continue
        ch = element['message']['chat']['id']
        if ch in was:
            continue
        real_actions += [element]
        was.add(ch)
    return real_actions

def main():
    dt = dict()
    started_games = set()
    colours=dict()
    while True:
        sleep(2)
        actions = a.get_updates()
        actions = delete_exceed(actions)
        for action in actions:
            ch = action['message']['chat']['id']
            if ch not in dt:
                if ch not in started_games:
                    start_game(started_games, action)
                else:
                    check_colour(dt, started_games, colours, action)
            else:
                check_move(started_games, colours, dt, action)

main()
