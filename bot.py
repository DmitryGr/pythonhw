import requests
import chess
import os
import sys
from time import sleep


class BotHandler:
    def __init__(self, token):
        self.url = "https://api.telegram.org/bot" + token + "/"
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


def mistake(handler, chat_id):
    handler.send_message(chat_id, "Wrong command. You`re directed to the start")


def check_result(handler, chat, board, colour):
    result = board.result()
    if result == '*':
        return False
    if_won = ((result == '1-0') ^ (colour == 'Black'))
    if result == '1/2-1/2':
        handler.send_message(chat, "Draw")
    elif if_won:
        handler.send_message(chat, "You won")
    else:
        handler.send_message(chat, "You lose")
    return True


def make_move(handler, chat, board):
    fen = board.fen()
    fen = fen.replace('/', '%2F')
    fen = fen.replace(' ', '+')
    address = 'http://api.underwaterchess.com/game?fen=' + fen + '&move=&format=json'
    r = requests.get(address)
    mv = r.json()['turn']['bestMove']
    machine_move = chess.Move.from_uci(mv)
    view = board.san(machine_move)
    handler.send_message(chat, view)
    board.push(machine_move)


def suggestion(handler, chat_id):
    handler.send_message(chat_id, "Make a move!")


def check_move(handler, started_games, colours, games, action):
    move = action['message']['text']
    chat = action['message']['chat']['id']
    if move == '/resign':
        handler.send_message(chat, "Thank you for the game!")
        games.pop(chat)
        started_games.remove(chat)
        return
    board = games[chat]
    try:
        machine_move = board.parse_san(move)
    except Exception:
        handler.send_message(chat, "Wrong move")
        return
    board.push(machine_move)
    colour = colours[chat]
    if check_result(handler, chat, board, colour):
        games.pop(chat)
        started_games.remove(chat)
        return
    make_move(handler, chat, board)
    if check_result(handler, chat, board, colour):
        games.pop(chat)
        started_games.remove(chat)
        return
    suggestion(handler, chat)


def start_game(handler, started_games, action):
    text = action['message']['text']
    chat = action['message']['chat']['id']
    if text != "/start_game":
        mistake(handler, chat)
        return
    started_games.add(chat)
    handler.send_message(chat, "Choose a colour. Send message White or Black")


def check_colour(handler, games, started_games, colours, action):
    text = action['message']['text']
    chat = action['message']['chat']['id']
    if text == 'White':
        games[chat] = chess.Board()
        colours[chat] = 'White'
        pass
    elif text == 'Black':
        games[chat] = chess.Board()
        colours[chat] = 'Black'
        make_move(handler, chat, games[chat])
    else:
        started_games.remove(chat)
        mistake(handler, chat)
        return
    suggestion(handler, chat)


def delete_exceed(handler, actions):
    real_actions = []
    was_chats = set()
    for element in actions:
        if 'text' not in element['message']:
            continue
        chat = element['message']['chat']['id']
        if element['message']['text'] == '/help':
            handler.send_message(chat, "Commands are:\nstart_game - to start a game\nresign - to resign")
            continue
        if chat in was_chats:
            continue
        real_actions += [element]
        was_chats.add(chat)
    return real_actions


def main():
    var = sys.argv[1]
    handler = BotHandler(var)
    used_chats = dict()
    started_games = set()
    colours=dict()
    while True:
        sleep(2)
        actions = handler.get_updates()
        actions = delete_exceed(handler, actions)
        for action in actions:
            chat = action['message']['chat']['id']
            if chat not in used_chats:
                if chat not in started_games:
                    start_game(handler, started_games, action)
                else:
                    check_colour(handler, used_chats, started_games, colours, action)
            else:
                check_move(handler, started_games, colours, used_chats, action)


if __name__ == "__main__":
    main()
