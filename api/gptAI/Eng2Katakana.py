import eng_to_ipa as ipa

def convert_to_katakana(word):
    # Convert English word to IPA
    ipa_word = ipa.convert(word)
    print(ipa_word)
    romaji_word = convert_ipa_to_romaji(ipa_word)
    print(romaji_word)
    katakana_word = convert_romaji_to_katakana(romaji_word)
    print(katakana_word)

def convert_ipa_to_romaji(ipa_word):
    # Define the conversion dictionary
    conversion_dict = {
        'i': 'i', 'ɪ': 'i', 'e': 'e', 'æ': 'a', 'ɑ': 'a', 'ɔ': 'o', 'ʌ': 'a', 'u': 'u', 'ʊ': 'u',
        'ɝ': 'a', 'ə': 'a', 'ɚ': 'a', 'j': 'ya', 'r': 'ra', 'l': 'ru', 'w': 'u', 'ʍ': 'u',
        'ɹ': 'ra', 'm': 'mu', 'n': 'n', 'ŋ': 'n', 'θ': 'su', 'ð': 'zu', 's': 'su', 'z': 'zu',
        'f': 'fu', 'v': 'vu', 'ʃ': 'shi', 'ʒ': 'ji', 'h': 'ha', 'tʃ': 'chi', 'dʒ': 'ji', 'p': 'pa',
        'b': 'bu', 't': 'to', 'd': 'do', 'k': 'ku', 'g': 'gu'
    }

    # Convert the IPA word to Romaji
    romaji_word = ''
    i = 0
    while i < len(ipa_word):
        if i < len(ipa_word) - 1 and ipa_word[i:i+2] in conversion_dict:
            romaji_word += conversion_dict[ipa_word[i:i+2]]
            i += 2
        elif ipa_word[i] in conversion_dict:
            romaji_word += conversion_dict[ipa_word[i]]
            i += 1
        else:
            i += 1

    return romaji_word

def convert_romaji_to_katakana(romaji_word):
    # Define the conversion dictionary
    conversion_dict = {
        'a': 'ア', 'i': 'イ', 'u': 'ウ', 'e': 'エ', 'o': 'オ',
        'ka': 'カ', 'ki': 'キ', 'ku': 'ク', 'ke': 'ケ', 'ko': 'コ',
        'sa': 'サ', 'shi': 'シ', 'su': 'ス', 'se': 'セ', 'so': 'ソ',
        'ta': 'タ', 'chi': 'チ', 'tsu': 'ツ', 'te': 'テ', 'to': 'ト',
        'na': 'ナ', 'ni': 'ニ', 'nu': 'ヌ', 'ne': 'ネ', 'no': 'ノ',
        'ha': 'ハ', 'hi': 'ヒ', 'fu': 'フ', 'he': 'ヘ', 'ho': 'ホ',
        'ma': 'マ', 'mi': 'ミ', 'mu': 'ム', 'me': 'メ', 'mo': 'モ',
        'ya': 'ヤ', 'yu': 'ユ', 'yo': 'ヨ',
        'ra': 'ラ', 'ri': 'リ', 'ru': 'ル', 're': 'レ', 'ro': 'ロ',
        'wa': 'ワ', 'wo': 'ヲ', 'n': 'ン',
        'ga': 'ガ', 'gi': 'ギ', 'gu': 'グ', 'ge': 'ゲ', 'go': 'ゴ',
        'za': 'ザ', 'ji': 'ジ', 'zu': 'ズ', 'ze': 'ゼ', 'zo': 'ゾ',
        'da': 'ダ', 'di': 'ヂ', 'du': 'ヅ', 'de': 'デ', 'do': 'ド',
        'ba': 'バ', 'bi': 'ビ', 'bu': 'ブ', 'be': 'ベ', 'bo': 'ボ',
        'pa': 'パ', 'pi': 'ピ', 'pu': 'プ', 'pe': 'ペ', 'po': 'ポ',
        'kya': 'キャ', 'kyu': 'キュ', 'kyo': 'キョ',
        'sha': 'シャ', 'shu': 'シュ', 'sho': 'ショ',
        'cha': 'チャ', 'chu': 'チュ', 'cho': 'チョ',
        'nya': 'ニャ', 'nyu': 'ニュ', 'nyo': 'ニョ',
        'hya': 'ヒャ', 'hyu': 'ヒュ', 'hyo': 'ヒョ',
        'mya': 'ミャ', 'myu': 'ミュ', 'myo': 'ミョ',
        'rya': 'リャ', 'ryu': 'リュ', 'ryo': 'リョ',
        'gya': 'ギャ', 'gyu': 'ギュ', 'gyo': 'ギョ',
        'ja': 'ジャ', 'ju': 'ジュ', 'jo': 'ジョ',
        'bya': 'ビャ', 'byu': 'ビュ', 'byo': 'ビョ',
        'pya': 'ピャ', 'pyu': 'ピュ', 'pyo': 'ピョ',
        'fa': 'ファ', 'fi': 'フィ', 'fe': 'フェ', 'fo': 'フォ',
        'va': 'ヴァ', 'vi': 'ヴィ', 'vu': 'ヴ','ve': 'ヴェ', 'vo': 'ヴォ',
        'ti': 'ティ', 'di': 'ディ',
        'she': 'シェ', 'je': 'ジェ', 'che': 'チェ',

    }

    # Convert the Romaji word to Katakana
    katakana_word = ''
    i = 0
    while i < len(romaji_word):
        if i < len(romaji_word) - 2 and romaji_word[i:i+3] in conversion_dict:
            katakana_word += conversion_dict[romaji_word[i:i+3]]
            i += 3
        elif i < len(romaji_word) - 1 and romaji_word[i:i+2] in conversion_dict:
            katakana_word += conversion_dict[romaji_word[i:i+2]]
            i += 2
        elif romaji_word[i] in conversion_dict:
            katakana_word += conversion_dict[romaji_word[i]]
            i += 1
        else:
            i += 1

    return katakana_word

katakana = convert_to_katakana("""
while i < len(romaji_word):
        if i < len(romaji_word) - 2 and romaji_word[i:i+3] in conversion_dict:
""")
