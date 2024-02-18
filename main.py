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

filepath = input('Enter the path of the .pdf file: ')
operation_type = int(input('Enter operation type (1=encrypt, 2=decrypt): '))
source = input('Enter the phrase you want to process (or a path to read): ')
if os.path.exists(source):
    with open(source) as handler:
        source = handler.read()

if operation_type == 1:
    function = encrypt
elif operation_type == 2:
    function = decrypt
else:
    print('The entered operation is not valid!')
    exit()

book = pdf.PdfFileReader(filepath)
if is_pdf_valid(book):
    content = list(map(extractor, book.pages))
    result = function(source, content)
    print("Result:", result)

    if path := input('If you want to save the result externally, enter the path, else just press <enter>: '):
        with open(path, 'w') as handler:
            handler.write(result)

else:
    print('Oops, the program could not detect any text in the loaded pdf')
