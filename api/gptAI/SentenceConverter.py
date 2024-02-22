import unicodedata
from janome.tokenizer import Tokenizer

class Kanji2Hiragana:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_kanji(ch):
        return 'CJK UNIFIED' in unicodedata.name(ch)

    @staticmethod
    def is_hiragana(ch):
        return 'HIRAGANA' in unicodedata.name(ch)

    @staticmethod
    def is_katakana(ch):
        return 'KATAKANA' in unicodedata.name(ch)

    @staticmethod
    def katakana_to_hiragana(katakana):
        return "".join([chr(ord(ch) - 0x60) if 'KATAKANA' in unicodedata.name(ch) else ch for ch in katakana])

    @staticmethod
    def convert(input_str:str):
        t = Tokenizer()
        tokens = t.tokenize(input_str)
        ret = ""
        for token in tokens:
            if token.surface.isdecimal():  # 数字の場合
                ret += token.surface
            elif token.surface.isascii():  # 英字の場合
                ret += token.surface
            elif all(Kanji2Hiragana.is_hiragana(ch) or Kanji2Hiragana.is_katakana(ch) for ch in token.surface):  # ひらがなやカタカナの場合
                ret += token.surface
            else:  # 漢字の場合
                ret += Kanji2Hiragana.katakana_to_hiragana(token.reading)
        return ret

import eng_to_ipa as ipa
from pykakasi import kakasi

def convert_to_katakana(word):
    # Convert English word to IPA
    ipa_word = ipa.convert(word)
    print(ipa_word)
    katakana_word = convert_ipa_to_katakana(ipa_word)


    return katakana_word

def convert_ipa_to_katakana(ipa_word):
    # Define the conversion dictionary
    conversion_dict = {
        'i': 'イ', 'ɪ': 'イ', 'e': 'エ', 'æ': 'エ', 'ɑ': 'ア', 'ɔ': 'オ', 'ʌ': 'ア', 'u': 'ウ', 'ʊ': 'ウ',
        'ɝ': 'アー', 'ə': 'ア', 'ɚ': 'アー', 'j': 'ヤ', 'r': 'ラ', 'l': 'ル', 'w': 'ウ', 'ʍ': 'ウ',
        'ɹ': 'ラ', 'm': 'ム', 'n': 'ン', 'ŋ': 'ン', 'θ': 'ス', 'ð': 'ズ', 's': 'ス', 'z': 'ズ',
        'f': 'フ', 'v': 'ヴ', 'ʃ': 'シ', 'ʒ': 'ジ', 'h': 'ハ', 'tʃ': 'チ', 'dʒ': 'ジ', 'p': 'プ',
        'b': 'ブ', 't': 'ト', 'd': 'ド', 'k': 'ク', 'g': 'グ'
    }

    # Convert the IPA word to Katakana
    katakana_word = ''
    i = 0
    while i < len(ipa_word):
        if i < len(ipa_word) - 1 and ipa_word[i:i+2] in conversion_dict:
            katakana_word += conversion_dict[ipa_word[i:i+2]]
            i += 2
        elif ipa_word[i] in conversion_dict:
            katakana_word += conversion_dict[ipa_word[i]]
            i += 1
        else:
            i += 1

    return katakana_word

"""ipa_word = "həˈloʊ"
katakana_word = convert_ipa_to_katakana(ipa_word)
print(katakana_word)"""




if __name__ == '__main__':
    str = """
    
携帯素解析 はとても難しい
 """
    english_word = "python code is very difficult"
    katakana_word = convert_to_katakana(english_word)
    print(katakana_word)