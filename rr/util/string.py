import re

from num2words import num2words


NUMBER_PATTERN = re.compile('[-+]?[0-9]+')

NEW_LINE = '\n'
DOUBLE_NEW_LINE = re.compile('\n\n')

# ACCENT_MARK_OCCURRENCE = re.compile(r'([^\s])\+([^\s])')
PLUS = '+'


def translate_numbers(text: str, lang: str = 'ru'):
    while (match := NUMBER_PATTERN.search(text)) is not None:
        number = match.group(0)
        text = text.replace(number, num2words(number, lang = lang), 1)

    return text


def drop_empty_lines(text: str):
    return DOUBLE_NEW_LINE.sub(NEW_LINE, text)


def drop_accent_marks(text: str):
    return text.replace(PLUS, '')
