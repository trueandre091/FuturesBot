import re

pattern = re.compile(r'[#$][A-z]+')


def scaler(word):
    word = word.uppercase()
    if '/' in word:
        word = word.split('/')[0]
    if '$' in word:
        word = word.replace("$", "#")
    return word

