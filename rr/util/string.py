import re

from num2words import num2words


NUMBER_PATTERN = re.compile('[-+]?[0-9]+')


def translate_numbers(text: str, lang: str = 'ru'):
    while (match := NUMBER_PATTERN.search(text)) is not None:
        number = match.group(0)
        text = text.replace(number, num2words(number, lang = lang), 1)

    return text
