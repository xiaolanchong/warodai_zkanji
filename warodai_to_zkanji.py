# Script to convert Warodai RU-JP dictionary to ZKanji app import format
# Format description is at
# https://web.archive.org/web/20130712024620/http://zkanji.wordpress.com/2013/02/14/planned-exportimport-file-format/

# Problems with conversion:
# - Roman numbers in words: ああI (а:)〔1-001-1-03〕
# - Html formatting tags in definitions: 1) <i>межд.</i> ах!;
# - Multiple word notation:
#    1-to-1: あばずれ, あばずれおんな【阿婆擦れ, 阿婆擦れ女】
#    1-to-many: あばれまわる【暴れ回る･暴れ廻る】
# - Kanji which are not in ZKanji known list, thus skipped: 蝱 (zkanji bug)
# - Too long definitions (~700 symbols) break importing completely (zkanji bug)
# - Nonsense cyrillic text displaying even in UTF8 encoding, no font change helps (zkanji bug)

import re
from transliterate import translit


class Entry:
    def __init__(self, word, kanji, definitions):
        self.word = word
        self.kanji = kanji
        self.definitions = definitions

    def repr(self):
        return '({}, {}, {})'.format(self.word, self.kanji, self.definitions)


def transliterate(text):
    return translit(text, 'ru', reversed=True)


def get_word_record():
    with open('ewarodai.txt', encoding='utf16') as warodai_db:
        record_contents = []
        for line in warodai_db.readlines():
            if len(line.strip()) == 0:
                result = record_contents
                record_contents = []
                yield result
            else:
                record_contents.append(line.strip())
        if len(record_contents):
            yield record_contents

# Expression to extract record headers, word in kana + kanji
word_name = re.compile(
    """^(.+?)\s?       # word   あばずれ, あばずれおんな
       (?:【(.+?)】)?   # kanji  阿婆擦れ, 阿婆擦れ女
       \(.+?\)         # transcription
       (?:\s\[.+?\])?  # field of knowledge
       〔.+?〕          # reference to an article
       .*$
    """, re.X|re.UNICODE|re.S)


# Unacceptable symbol in a word
re_warning_char = re.compile('[・…]', re.UNICODE)


def process_word_kanji(word_part, kanji_part):
    """
    Gets word and kanji list for the dictionary record
    :param word_part: word part of the title
    :param kanji_part: kanji part of the title
    :return: list of pairs
    """
    stripped_word, roman_numbers = re.subn('[IVX]+$', '', word_part)
    if roman_numbers != 0:
        print('Multiple entry', word_part, stripped_word)
        word_part = stripped_word

    if kanji_part is None:
        return [(word_part, None)]

    stripped_kanji, roman_numbers = re.subn('[IVX]+$', '', kanji_part)
    if roman_numbers:
        print("Roman numbers in kanji: " + kanji_part)
        kanji_part = stripped_kanji

    if ',' in word_part:
        if ',' in kanji_part:
            words = [tok.strip() for tok in word_part.split(',')]
            kanji_for_words = [tok.strip() for tok in kanji_part.split(',')]
            assert(len(words) == len(kanji_for_words))
            print('a few words/kanji', word_part, kanji_part)
            return list(zip(words, kanji_for_words))
        else:
            print("No ',' in kanji " + kanji_part)

    if '･' in kanji_part:
        kanji_for_words = [tok.strip() for tok in kanji_part.split('･')]
        print('1 word/a few kanji', word_part, kanji_part)
        return [(word_part, kanji_tok) for kanji_tok in kanji_for_words]

    return [(word_part, stripped_kanji)]


# Expression to remove html tags
html_tag = re.compile('<.+?>')


def process_definitions(lines):
    assert(len(lines))
    definitions = ['']
    for line in lines:
        m = re.search('^(\d+)\)\s*(.+)', line)
        if m is not None:
            definitions.append(m.group(2))
        else:
            if(len(definitions[-1])) < 500:
                definitions[-1] += line
            else:
                print('>>>>>>>>>> Skip', lines[0])
    if len(definitions) > 1:
        header = definitions[0]
        definitions.pop(0)
        definitions[0] = header + (' ' if len(header) else '') + definitions[0]
    for i in range(len(definitions)):
        definitions[i] = html_tag.sub('', definitions[i])
    return definitions


dictionary_header = \
""";zkanji export file for version 0.73 and later.
;Warodai dictionary converted file.

[About]
*This dictionary is based on Warodai, and is a compilation of
*http://e-lib.ua/dic/download/ewarodai.zip

[Words]
"""


def dump_zkanji_file(dictionary):
    with open('warodai.zkanji.export', mode='w', encoding='utf8') as out:
        out.write(dictionary_header)
        dump_dictionary(dictionary, out)


black_list = {'𩺊', '𩸨', '𪻄', '𫒒', '猪口', '𩋡', '￮', '𩕄門', '𩸽'}


def dump_dictionary(dictionary, out_buffer):
    word_frequency = 0  # unknown frequency
    for entry in dictionary:
        kanji = entry.kanji if entry.kanji is not None else entry.word
        if kanji in black_list:
            print(kanji, 'definition skipped')
            continue
        translit_def = ( transliterate(definition) for definition in entry.definitions)
        defs = ' '.join( 'M{{\t{definition}\t}}M'.format(definition=definition) for definition in translit_def)
        line = '{kanji} {kana} F{frequency} {definitions}\n'.format(
            kanji=kanji, kana=entry.word, definitions=defs, frequency=word_frequency)
        out_buffer.write(line)


re_space = re.compile('\s')
re_no_symbol_in_definition = re.compile('[\t\r\n]')


def extract_word_kanji(line):
    m = word_name.match(line)
    if m is None:
        raise RuntimeError(line)
    word, kanji = m.groups()
    return word, kanji


def chunks(l, n):
    """Yields successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def process_word_record(lines, dictionary):
    if len(lines) < 2:
        raise RuntimeError(lines[0])
    word, kanji = extract_word_kanji(lines[0])

    words_and_kanji = process_word_kanji(word, kanji)
    definitions = process_definitions(lines[1:])
    for definition in definitions:
        assert (re_no_symbol_in_definition.search(definition) is None)

    for word, kanji in words_and_kanji:
        if re_space.search(word) is not None:
            print('White space in word:' + word)
            continue
        if kanji is not None and re_space.search(kanji) is not None:
            raise RuntimeError('White space in kanji:' + kanji)

        initial = (word, kanji)
        word, num = re_warning_char.subn('', word)
        if num:
            print('Removed chars in', initial[0])

        if kanji:
            kanji, num = re_warning_char.subn('', kanji)
            if num:
                print('Removed chars in', initial[1])

        chunk_num = 0
        for chunk_defs in chunks(definitions, 5):
            entry = Entry(word, kanji, chunk_defs)
            dictionary.append(entry)
            chunk_num += 1

        if chunk_num > 1:
            print('Split into ', word, 'into', chunk_num, 'parts')


def main():
    records = get_word_record()
    next(records)
    dictionary = []
    entry_num = 0
    for rec in records:
        process_word_record(rec, dictionary)
        entry_num += 1

    print('words', entry_num)

    dump_zkanji_file(dictionary)

if __name__ == '__main__':
    main()
