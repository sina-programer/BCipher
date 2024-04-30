from argparse import ArgumentParser
from functools import partial
import PyPDF2 as pdf  # 3.0.1
import operator
import time
import os


def _encrypt_word(word, contents):
    for page_idx, page_text in enumerate(contents):
        if word in page_text:
            for line_idx, line in enumerate(page_text.splitlines()):
                words = line.split()
                if word in words:
                    return page_idx, line_idx, words.index(word)

def encrypt_word(word, contents: list[str]):
    if coords := _encrypt_word(word, contents):
        return '-'.join(map(str, coords))
    return '#'

def encrypt(text, contents: list[str], delimiter=','):
    encrypter = partial(encrypt_word, contents=contents)
    return '\n'.join(
        [
            delimiter.join(
                map(
                    encrypter,
                    line
                )
            )
            for line in splitter(text)
        ]
    )


def is_code_valid(code, seperator='-'):
    parts = code.split(seperator)
    if len(parts) != 3:
        return False
    for part in parts:
        if not part.isnumeric():
            return False
    return True

def decrypt_code(code, contents: list[str]):
    if not is_code_valid(code):
        return '#'
    page_idx, line_idx, word_idx = list(map(int, code.split('-')))
    page_text = contents[page_idx]
    lines = page_text.splitlines()
    words = lines[line_idx].split()
    return words[word_idx]

def decrypt(phrase, contents: list[str], delimiter='.'):
    decrypter = partial(decrypt_code, contents=contents)
    return ' '.join(map(decrypter, phrase.split(delimiter)))

def check(clause, contents):
    result = []
    for line in splitter(clause):
        _result = []
        for word in line:
            if fetch_word_pos(word, contents):
                _result.append(word)
            else:
                _result.append('#')
        result.append(' '.join(_result))
    return '\n'.join(result)

def is_pdf_valid(pdf_obj):
    """ Has the program detected any text in pdf or not """
    for page_text in map(textractor, pdf_obj.pages):
        if page_text.strip():
            return True
    return False

def splitter(text):
    result = []
    for line in text.splitlines():
        result.append(line.split())
    return result

def print_figlet():
    for line in FIGLET.splitlines():
        print(line)
        time.sleep(.2)

lower = operator.methodcaller('lower')
textractor = operator.methodcaller('extract_text')

DESCRIPTION = "This program encrypts your intended text by a book."
FIGLET = '''\n
   _____ _               ____
  / ____(_)             |  __|
 | (___  _ _ __   __ _  | |__ 
  \___ \| | '_ \ / _` | |  __|
  ____) | | | | | (_| |_| |  
 |_____/|_|_| |_|\__,_(_)_| 
\n\n'''


if __name__ == "__main__":
    parser = ArgumentParser(prog='BCipher', description=DESCRIPTION)
    parser.add_argument('source', help='desired pdf book')
    parser.add_argument('data', help='either a text between " or path of a text file. words separated by space')
    parser.add_argument('-c', '--check', action='store_true', help='do checking operation | check the presence of <data> values & put # for unaccessables')
    parser.add_argument('-e', '--encrypt', action='store_true', help='do encrypt operation | convert each word into a 3-part encoded clause')
    parser.add_argument('-d', '--decrypt', action='store_true', help='do decrypt operation | retrieve each encoded clause into a word')
    parser.add_argument('-o', '--output', help='export the result in this path')
    parser.add_argument('--delimiter', default='|', help='the separator between encoded phrase')
    parser.add_argument('-ls', '--lower-source', action='store_true', help='lower the content of <source>')
    parser.add_argument('-ld', '--lower-data', action='store_true', help='lower the content of <data>')

    args = parser.parse_args()
    if not os.path.exists(args.source):
        parser.error(f"the entered source is not valid: <{args.source}>")

    if os.path.exists(args.data):
        print(f"loading the file you entered as data: <{args.data}>")
        with open(args.data) as handler:
            args.data = handler.read()

    book = pdf.PdfReader(args.source)
    if is_pdf_valid(book):
        content = list(map(textractor, book.pages))

        if args.lower_source:
            content = list(map(lower, content))
        if args.lower_data:
            args.data = args.data.lower()

        if args.check:
            result = check(args.data, content)
        if args.decrypt:
            result = decrypt(args.data, content, delimiter=args.delimiter)
        elif args.encrypt:
            result = encrypt(args.data, content, delimiter=args.delimiter)
        else:
            print("you didn't set the operation, encryption is running by default")
            result = encrypt(args.data, content, delimiter=args.delimiter)
        print("Result:", result)

        if args.output:
            with open(args.output, 'w') as handler:
                handler.write(result)
            print(f"the result is written in output: <{args.output}>")

    else:
        print('Oops, the program could not detect any text in the loaded pdf')

    print_figlet()
