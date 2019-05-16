import argparse
import sys
INF = 1e18
ENGLISH_ALPHABET_SIZE = 26


def add_encode_decode(parser):
    parser.add_argument('--cipher', nargs=1, choices = ["caesar", "vigenere", "vernam"], help="name of cipher")
    parser.add_argument('--key', nargs=1, help="name of cipher key")
    parser.add_argument('--input-file', help="name of input file(not necessary)")
    parser.add_argument('--output-file', help="name of output file (not necessary)")

def add_train(parser):
    parser.add_argument('--input-file', help="name of input file")
    parser.add_argument('--model-file', nargs=1, help="name of model file for training")

def add_hack(parser):
    parser.add_argument('--input-file', help="name of input file")
    parser.add_argument('--output-file', help="name of output file(not necessary)")
    parser.add_argument('--model-file', nargs=1, help="name of model file")

def parse():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    encode_parser = subparsers.add_parser('encode')
    encode_parser.set_defaults(func=encode)
    add_encode_decode(encode_parser)
    decode_parser = subparsers.add_parser('decode')
    decode_parser.set_defaults(func=decode)
    add_encode_decode(decode_parser)
    hack_parser = subparsers.add_parser('hack')
    hack_parser.set_defaults(func=hack)
    add_hack(hack_parser)
    train_parser = subparsers.add_parser('train')
    train_parser.set_defaults(func=train)
    add_train(train_parser)
    return parser

def try_redirect(is_input, is_output, namespace):
    if is_input and namespace.input_file is not None:
        sys.stdin = open(namespace.input_file, 'r')
    if is_output and namespace.output_file is not None:
        sys.stdout = open(namespace.output_file, 'w')

def close_file():
    sys.stdout.close()

def add_in_transformation(symbol, step, edge):
    num = ord(symbol) + (step % ENGLISH_ALPHABET_SIZE)
    if num > ord(edge):
        num -= ENGLISH_ALPHABET_SIZE
    return chr(num)

def is_between(symbol, left, right):
    symb_ord, left_ord, right_ord = ord(symbol), ord(left), ord(right)
    return left_ord <= symb_ord <= right_ord

def transform_caesar(symbol, step):
    if is_between(symbol, 'A', 'Z'):
        return add_in_transformation(symbol, step, 'Z')
    if is_between(symbol, 'a', 'z'):
        return add_in_transformation(symbol, step, 'z')
    return symbol

def read_text():
    text = sys.stdin.read()
    return text[:-1]

def encode_full_text_caesar(text, key):
    answer = []
    for symbol in text:
        answer += [transform_caesar(symbol, key)]
    return "".join(answer)

def encode_caesar(key):
    print(encode_full_text_caesar(read_text(), key))

def get_code(symbol):
    if is_between(symbol, 'A', 'Z'):
        return ord(symbol) - ord('A')
    if is_between(symbol, 'a', 'z'):
        return ord(symbol) - ord('a')
    raise Exception('wrong key word')

def encode_vigener(key):
    text = read_text()
    copy_key = key
    while len(copy_key) < len(text):
        copy_key += key
    answer = ""
    for i in range(len(text)):
        second_code = get_code(copy_key[i])
        answer += transform_caesar(text[i], second_code)
    print(answer)

def vernam(key):
    text = read_text()
    answer = ""
    cur=0
    for symbol in text:
        start_symbol = 'a'
        if not is_between(symbol, 'a', 'z') and not is_between(symbol, 'A', 'Z'):
            answer += symbol
            continue
        if cur == len(key):
            raise Exception("key length is too small")
        if is_between(symbol, 'A', 'Z'):
            start_symbol = 'A'
        code = ord(symbol) + ord(key[cur]) - 2 * ord(start_symbol)
        code %= ENGLISH_ALPHABET_SIZE
        answer += chr(ord(start_symbol) + code)
    print(answer)


def encode(namespace):
    try_redirect(True, True, namespace)
    key, cipher = namespace.key[0], namespace.cipher[0]
    if cipher == 'caesar':
        encode_caesar(int(key))
    elif cipher == 'vigenere':
        encode_vigener(key)
    elif cipher == 'vernam':
        vernam(key)
    else:
        raise Exception('wrong parameter = cipher_name')

def reverse_for_decoding(key):
    new_key = ""
    for symbol in key:
        code = get_code(symbol)
        real_code = (-code)%ENGLISH_ALPHABET_SIZE
        if is_between(symbol, 'a', 'z'):
            new_key += chr(ord('a') + real_code)
        elif is_between(symbol, 'A', 'Z'):
            new_key += chr(ord('A') + real_code)
        else:
            raise Exception('wrong key')
    return new_key

def decode(namespace):
    try_redirect(True, True, namespace)
    key, cipher = namespace.key[0], namespace.cipher[0]
    if cipher == 'caesar':
        encode_caesar(-int(key))
    elif cipher == 'vigenere':
        encode_vigener(reverse_for_decoding(key))
    elif cipher == 'vernam':
        vernam(reverse_for_decoding(key))
    else:
        raise Exception('wrong parameter = cipher_name')

def is_letter(symbol):
    return is_between(symbol, 'a', 'z') or is_between(symbol, 'A', 'Z')

def analyse(text, hystogramm):
    for symbol in text:
        if not is_letter(symbol):
            continue
        if symbol not in hystogramm:
            hystogramm[symbol] = 0
        hystogramm[symbol] += 1
    sum = 0
    for element in hystogramm:
        sum += hystogramm[element]
    for element in hystogramm:
        hystogramm[element] /= sum

def train(namespace):
    try_redirect(True, False, namespace)
    sys.stdout = open(namespace.model_file[0], 'w')
    hystogramm = dict()
    text = read_text()
    analyse(text, hystogramm)
    for element in hystogramm:
        print(element, hystogramm[element])
    print("0")

def get_diff(hyst1, hyst2):
    res = 0
    union = set()
    for element in hyst1:
        union.add(element)
    for element in hyst2:
        union.add(element)
    for element in union:
        if element not in hyst1:
            hyst1[element] = 0
        if element not in hyst2:
            hyst2[element] = 0
        diff = hyst1[element] - hyst2[element]
        res += diff**2
    return res

def nxt(symbol):
    if is_between(symbol, 'a', 'z'):
        if symbol == 'z':
            return 'a'
        return chr(ord(symbol)+1)
    if symbol == 'Z':
        return 'A'
    return chr(ord(symbol) + 1)

def shift(dictionary):
    new_dictionary = dict()
    for element in dictionary:
        new_dictionary[nxt(element)] = dictionary[element]
    return new_dictionary

def hack(namespace):
    try_redirect(True, True, namespace)
    model = open(namespace.model_file[0], 'r')
    hystogramm = dict()
    while True:
        symbol = model.readline()[:-1]
        if symbol == '0':
            break
        line = symbol.split(' ')
        hystogramm[line[0]] = float(line[1])
    text = read_text()
    min_diff = INF
    need_code = -1
    var = encode_full_text_caesar(text, 0)
    this_hystogramm = dict()
    analyse(var, this_hystogramm)
    for i in range(ENGLISH_ALPHABET_SIZE):
        difference = get_diff(hystogramm, this_hystogramm)
        if difference < min_diff:
            min_diff = difference
            need_code = i
        this_hystogramm = shift(this_hystogramm)
    print(encode_full_text_caesar(text, need_code))




def run(parser):
    namespace = parser.parse_args()
    namespace.func(namespace)
    close_file()

def solve():
    parser = parse()
    run(parser)

if __name__ == "__main__":
    solve()
