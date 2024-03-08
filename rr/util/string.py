import re
from math import floor

from num2words import num2words


NUMBER_PATTERN = re.compile('[-+]?[0-9]+')

NEW_LINE = '\n'
DOUBLE_NEW_LINE = re.compile('\n\n')

# ACCENT_MARK_OCCURRENCE = re.compile(r'([^\s])\+([^\s])')
PLUS = '+'

DELETED_TRAILERS = ('"', "'", '`')

SPACE_TEMPLATE = re.compile(r'\s+')
SPACE = ' '

ALPHANUM_CHARACTER_TEMPLATE = re.compile(r'[a-zA-Z0-9\s]')
MAX_TRANSLATION_LENGTH = 200


def translate_numbers(text: str, lang: str = 'ru'):
    while (match := NUMBER_PATTERN.search(text)) is not None:
        number = match.group(0)
        text = text.replace(number, num2words(number, lang = lang), 1)

    return text


def drop_empty_lines(text: str):
    return DOUBLE_NEW_LINE.sub(NEW_LINE, text)


def drop_accent_marks(text: str):
    return text.replace(PLUS, '')


def normalize(string: str):
    return SPACE_TEMPLATE.sub(SPACE, string).strip()


def post_process_summary(text: str, min_duplicate_fraction: float = 0.25):
    input_text = text
    min_match_size = floor(len(text) * min_duplicate_fraction)

    # 1. Delete undesired headers / trailers

    for trailer in DELETED_TRAILERS:
        if text.startswith(trailer):
            text = text[1:]

        if text.endswith(trailer):
            text = text[:-1]

    # 2. Delete repeating chunks of text

    i = 0
    j = 0

    length = len(text)

    i_matches = []
    j_matches = []

    for i in range(length):
        for j in range(length):
            if i != j and text[i].lower() == text[j].lower():
                i_ = i + 1
                j_ = j + 1

                while i_ < length and j_ < length and text[i_].lower() == text[j_].lower():
                    i_ += 1
                    j_ += 1

                if j_ - j >= min_match_size:
                    i_match = (i, i_)
                    j_match = (j, j_)

                    if i_match not in j_matches:
                        for match in i_matches:
                            if match[0] <= i_match[0] and i_match[1] <= match[1]:
                                break
                        else:
                            for match in j_matches:
                                if match[0] <= i_match[0] and i_match[1] <= match[1]:
                                    break
                            else:
                                i_matches.append(i_match)
                                j_matches.append(j_match)

    if len(j_matches) > 0:
        longest_match = sorted(j_matches, key = lambda item: item[1] - item[0], reverse = True)[0]

        text = text[:longest_match[0]] + text[longest_match[1] + 1:]

    if input_text == text:
        return text.strip()

    return post_process_summary(text.strip(), min_duplicate_fraction = min_duplicate_fraction)


def truncate_translation(text: str):
    truncated_text = []

    for char in normalize(text.lower()).strip():
        if ALPHANUM_CHARACTER_TEMPLATE.fullmatch(char):
            truncated_text.append(char)

    # return '-'.join(''.join(truncated_text).split(' '))
    return ''.join(truncated_text)[:MAX_TRANSLATION_LENGTH]
