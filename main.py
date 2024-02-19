from argparse import ArgumentParser
import PyPDF2 as pdf  # 1.26.0
import operator
import os

def encrypt_word(word, contents: list[str]):
    word = word.lower()
    for page_idx, page_text in enumerate(map(lower, contents)):
        if word in page_text:
            for line_idx, line in enumerate(page_text.split('\n')):
                words = line.split()
                if word in words:
                    return f"{page_idx}-{line_idx}-{words.index(word)}"
    return '#'

def encrypt(text, contents: list[str]):
    result = ''
    for sentence in text.split('\n'):
        result +=  '|'.join(map(lambda word: encrypt_word(word, contents), sentence.split())) + '\n'
    return result.strip('\n')

def decrypt_code(code, contents: list[str]):
    page_idx, line_idx, word_idx = list(map(int, code.split('-')))
    page_text = contents[page_idx].lower()
    lines = page_text.split('\n')
    words = lines[line_idx].split()
    return words[word_idx]

def decrypt(phrase, content: list[str]):
    words = []
    for code in phrase.split('|'):
        if code == '#':
            words.append(code)
        else:
            words.append(decrypt_code(code, content))
    return ' '.join(words)

def is_pdf_valid(pdf_obj):
    """ Has the program detected any text in pdf or not """
    for page_text in map(extractor, pdf_obj.pages):
        if page_text.strip():
            return True
    return False

lower = operator.methodcaller('lower')
extractor = operator.methodcaller('extractText')

_description = "This program encrypts your intended text by a book."

if __name__ == "__main__":
    parser = ArgumentParser(prog='BCipher', description=_description)
    parser.add_argument('source', help='desired pdf book')
    parser.add_argument('data', help='either a text between " or path of a text file')
    parser.add_argument('-e', '--encrypt', action='store_true', help='do encryption')
    parser.add_argument('-d', '--decrypt', action='store_true', help='do decryption')
    parser.add_argument('-o', '--output', help='export the result in this path')

    args = parser.parse_args()
    if os.path.exists(args.data):
        with open(args.data) as handler:
            args.data = handler.read()

    book = pdf.PdfFileReader(args.source)
    if is_pdf_valid(book):
        content = list(map(extractor, book.pages))
        if args.decrypt:
            result = decrypt(args.data, content)
        else:
            result = encrypt(args.data, content)
        print("Result:", result)

        if args.output:
            with open(args.output, 'w') as handler:
                handler.write(result)

    else:
        print('Oops, the program could not detect any text in the loaded pdf')
