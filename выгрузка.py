import requests
from random import randint
from emoji import demojize, emojize


def emoji_search(text: str, neg_emoji_keywords: list, pos_emoji_keywords: list):
    """ searches for emoji in a given text
    :param
            text : a string in which emoji wanted to  be detected
            neg_emoji_keywords: list of keywords to detect negative emoji
            neg_emoji_keywords: list of keywords to detect negative emoji

    :returns
        a list with two elements in it: list of positive emoji and list of negative emoji
    :rtype
        list"""

    emoji = [[], []]
    text = demojize(text).split(':')
    for i in range(len(text)):
        part = text[i]
        pos = False

        # детектим эмоджи и проверяем его на тональность

        if len(part.split()) == 1:
            for word in pos_emoji_keywords:
                if word in part:
                    emoji[0].append(emojize(':' + part + ':'))
                    pos = True
                    break
            if not pos:
                for word in neg_emoji_keywords:
                    if word in part:
                        emoji[1].append(emojize(':' + part + ':'))
                        break
            text[i] = ''
    return emoji


def text_emoji_search(text: str, acceptable_symbols: list or str):
    """searches for text emoji in a given text
    :param
            text: string we want to scan
            acceptable_symbols: list or string of acceptable symbols which can be in a text emoji
    :returns
        a list of 2 lists with positive (1st list) and negative (2nd list) text emoticons if they are in a tweet
    :rtype
        list"""

    emoji =[[], []]
    text = ':'.join(text)
    twit_1 = text.replace(',', '').replace('.', ' ').replace(' ', '').replace('?', '').replace('!', '').replace(
            '/', '').replace('"', '').replace(chr(92), '')
    emote = ''
    for symbol in twit_1:
        if not symbol.isalpha() and symbol != ' ' and not symbol.isnumeric():
            emote += symbol
        elif len(emote) >= 2:
            if ')' in emote:
                emoji[0].append(emote)
                emote = ''
            elif '(' in emote:
                emoji[0].append(emote)
                emote = ''
            else:
                emote = ''
        else:
            emote = ''
    return emoji


def token_scan(text: str, dictionary: dict, positive_key: str, negative_key: str):
    """ finds negative and positive words and combinations in a given text"
    :param
            text: text we want to scan
            dictionary: a dictionary of positive and negative words
            positive_key: a key for positive words in a dictionary
            negative_key: a key for negative words in a dictionary
            positive_negative_key: a key for pos_neg_words
    :returns
        a list of 2 lists with positive (1st list) and negative (2nd list) words and word combinations if they are in a tweet
    :rtype
        list"""

    text = text.split()
    tokens = [[], []]
    for word in text:
        if word in ['не', "ни"]:
            dict_findings['negation'].append(word)
        elif word in dict_of_pos_neg_words['positive'] and len(word) > 3:
            dict_findings['pos_words'].append(word)
        elif word in dict_of_pos_neg_words['negative'] and len(word) > 3:
            dict_findings['neg_words'].append(word)
        elif word in dict_of_pos_neg_words['positive/negative'] and len(word) > 3:
            dict_findings['pos_neg_words'].append(word)

    # проверяем словосочетания (1-я итерация - словосочетания  с 2 словами, 2-я - с 3-мя)
    if dict_findings['pos_words'] == 0 or dict_findings['neg_words'] == 0:
        for j in range(2):
            for i in range(1 + j, len(text)):
                if (text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i]) in dict_of_pos_neg_words['positive']:
                    dict_findings['pos_words'].append(text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i])
                elif (text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i][:-2]) in dict_of_pos_neg_words['negative']:
                    dict_findings['neg_words'].append(text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i])
                elif (text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i]) in dict_of_pos_neg_words[
                    'positive/negative']:
                    dict_findings['pos_neg_words'].append(
                        text[i - 1 - j] + ' ' + text[i - 1] * j + ' ' * j + text[i])
    pass



def scan_a_tweet(tweet, dictionary):
    """ищет 5 разных категорий слов, чтобы потом  посмотреть что есть, чего нет и распределить по файлам"""

    tweet = tweet.replace(" ", ' ').lower().replace('@', '')

    # инициализирую переменные и пишу ключевые слова для эмоджи, чтобы определять их тональность
    # (вних включены топ 10 используемых эмоджи плюс ещё несколько с сердечками и поцелуями
    # и ещё несколько негативных, но это подавляющее большинство эмодзи с тональностью,
    # да и + сказать, что обычно пользователи твитера обычно плещут каким-либо разнообразием тяжело)

    pos_emoji_keywords = ['laugh', 'heart', 'kiss', 'smil', 'joy', 'up', 'fire', 'star']
    neg_emoji_keywords = ['angr', 'fear', 'rag', 'disap', 'sweat', 'down']
    dict_findings = {'neg_emoticons': [], "pos_emoticons": [], 'pos_words': [], 'neg_words': [], "negation": [], 'pos_neg_words': []}
    global dict_of_pos_neg_words

    # на этом этапе я смотрю на эмоджи

    tweet = demojize(tweet).split(':')
    for i in range(len(tweet)):
        part = tweet[i]
        pos = False

        # детектим эмоджи и проверяем его на тональность

        if len(part.split()) == 1:
            for word in pos_emoji_keywords:
                if word in part:
                    dict_findings["pos_emoticons"].append(emojize(':' + part + ':'))
                    pos = True
                    break
            if not pos:
                for word in neg_emoji_keywords:
                    if word in part:
                        dict_findings["neg_emoticons"].append(emojize(':' + part + ':'))
                        break
            tweet[i] = ''

# как только почистили от обычных эмоджи так как нам нужен один или меньше эмоджи
# мы проверим есть ли смысл искать текстовые эмоджи
# я очищаю твит от ненужных символов, если набирается несколько не букв подряд
# эту комбинацию я добавляю в свой словарь
# этот метод часто регистрирует шумы вместе с эмоджи, но эмоджи ведь он тоже регистрирует,


    tweet = ':'.join(tweet)
    if len(dict_findings["neg_emoticons"]) == 0 or len(dict_findings["pos_emoticons"]) == 0:
        twit_1 = tweet.replace(',', '').replace('.', ' ').replace(' ', '').replace('?', '').replace('!', '').replace('/', '').replace('"', '').replace(chr(92), '')
        emote = ''
        for symbol in twit_1:
            if not symbol.isalpha() and symbol != ' ' and not symbol.isnumeric():
                emote += symbol
            elif len(emote) >= 2:
                if ')' in emote:
                    dict_findings['pos_emoticons'].append(emote)
                    emote = ''
                elif '(' in emote:
                    dict_findings['neg_emoticons'].append(emote)
                    emote = ''
                else:
                    emote = ''
            else:
                emote = ''
# оставляем в твите только буквы и пробелы

    for symbol in tweet:
        if (ord(symbol) < ord('А') or ord(symbol) > ord('я')) and symbol != ' ':
            tweet = tweet.replace(symbol, '')

# сейчас проверим твит на тональные слова и словосочетания

    tweet = tweet.split()
    for word in tweet:
        if word in ['не', "ни"]:
            dict_findings['negation'].append(word)
        elif word in dict_of_pos_neg_words['positive'] and len(word) > 3:
            dict_findings['pos_words'].append(word)
        elif word in dict_of_pos_neg_words['negative'] and len(word) > 3:
            dict_findings['neg_words'].append(word)
        elif word in dict_of_pos_neg_words['positive/negative'] and len(word) > 3:
            dict_findings['pos_neg_words'].append(word)

# проверяем словосочетания (1-я итерация - словосочетания  с 2 словами, 2-я - с 3-мя)
    if dict_findings['pos_words'] == 0 or dict_findings['neg_words'] == 0:
        for j in range(2):
            for i in range(1+j, len(tweet)):
                if (tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i]) in dict_of_pos_neg_words['positive']:
                    dict_findings['pos_words'].append(tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i])
                elif (tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i][:-2]) in dict_of_pos_neg_words['negative']:
                    dict_findings['neg_words'].append(tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i])
                elif (tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i]) in dict_of_pos_neg_words['positive/negative']:
                    dict_findings['pos_neg_words'].append(tweet[i - 1 - j] + ' ' + tweet[i - 1] * j + ' ' * j + tweet[i])

# теперь, если трбуется работаем со словами где тональность зависит от контекста
# идея простейшая: если больше негатива в твите скорее всего слово будет негативным
# иначе слово будет позитивным
# если равное количество, то выбираем случайно

    if (len(dict_findings['pos_words']) == 0 or len(dict_findings['neg_words']) == 0) and len(dict_findings['pos_neg_words']) != 0:
        if len(dict_findings['pos_words']) + len(dict_findings["pos_emoticons"]) > len(dict_findings['neg_words']) + len(dict_findings["neg_emoticons"]):
            dict_findings['pos_words'].append(dict_findings['pos_neg_words'][0])
        elif len(dict_findings['pos_words']) + len(dict_findings["pos_emoticons"]) < len(dict_findings['neg_words']) + len(dict_findings["neg_emoticons"]):
            dict_findings['neg_words'].append(dict_findings['pos_neg_words'][0])
        elif len(dict_findings['pos_words']) + len(dict_findings["pos_emoticons"]) == len(dict_findings['neg_words']) + len(dict_findings["neg_emoticons"]):
            r = randint(0, 1)
            if r == 1:
                dict_findings['neg_words'].append(dict_findings['pos_neg_words'][0])
            else:
                dict_findings['pos_words'].append(dict_findings['pos_neg_words'][0])

# возвращаем что нашли

    return (dict_findings)

# забрутфорсил словарь с разными формами слов
# я сначала сравнивал только основы, но точность очень сильно падала
# особенно для слов с 4-мя буквами, поэтому переделал


v_endings = ['ешь', 'ет', 'ем', 'ете', 'ут', 'ют', 'ишь', 'ит', 'им', 'ите', 'aт', 'ят', 'л', 'ла', 'ло']
n_endings = ['ы', "и", 'а', 'я', 'у', 'ов', 'ей', 'е', 'ам', 'ям', 'ю', 'ом', 'ой', 'ою', 'ью', 'ами', 'ями', 'ми', 'ах', 'ях']
adj_endings = ['ой', "ей", "ий" "ая", "яя", "ья", "ые", "ие", "ом", "ем", "ую", "юю", "ое", "ее", "ому", "ему", "ыми", "ими", "ему"]


dict_of_pos_neg_words = {"positive": set([]), 'negative': set([]), 'positive/negative': set([])}
req = requests.get("https://www.labinform.ru/pub/rusentilex/rusentilex_2017.txt").text
for line in req.split("\r\n")[19:-1]:
    if line.split(", ")[3] in ['positive', 'negative', 'positive/negative']:
        if line.split(", ")[1] == 'VG':
            words = line.split(", ")[0].split(' ')
            if words[-1][:-2] in ['сь', 'ся']:
                for ending_noun in n_endings:
                    for ending_verb in v_endings:
                        words[0] = words[0][:-2] + ending_noun
                        words[-1] = words[-1][:-4] + ending_verb + words[-1][:-2]
                        dict_of_pos_neg_words[line.split(", ")[3]].add(' '.join(words))
            else:
                for ending_noun in n_endings:
                    for ending_verb in v_endings:
                        words[0] = words[0][:-2] + ending_noun
                        words[-1] = words[-1][:-2] + ending_verb
                        dict_of_pos_neg_words[line.split(", ")[3]].add(' '.join(words))
        elif line.split(", ")[1] == 'VG':
            words = line.split(", ")[0].split(' ')
            for ending_adjective in adj_endings:
                for ending_noun in n_endings:
                    words[0] = words[0][:-2] + ending_adjective
                    words[-1] = words[-1][:-2] + ending_noun
                    dict_of_pos_neg_words[line.split(", ")[3]].add(' '.join(words))
        elif line.split(", ")[1] == 'Verb':
            if line.split(", ")[0][-2:] in ['ся', "сь"]:
                for ending in v_endings:
                    dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0][:-4] + ending + line.split(", ")[0][-2:])
                dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0])
            else:
                for ending in v_endings:
                    dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
                dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0])
        elif line.split(", ")[1] == 'Noun':
            for ending in n_endings:
                dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
            dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0])
        elif line.split(', ')[1] == 'Adj':
            for ending in adj_endings:
                dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
            dict_of_pos_neg_words[line.split(", ")[3]].add(line.split(", ")[0])


# Я честно пытался в workbench sql script запустить, я фиксил баг за багом
# я, честно, иногда поражаюсь какие дебри в настройках существуют
# но когда workbench просто крашился с неизвестной ошибкой
# я, мои друзья с индийским акцентом и stack overflow сдались
# поэтому я просто проитерировал текстовый файл и выписал в отдельный CSV файл все твиты
ser = open('output.csv').readlines()

# теперь распределяю по файлам
# в зависимости от того, что мы в твите нашли
# мы определяем в какой файл пойдёь
# делиметр для твита и того что нашли: $$
# чтобы потом легче можно было бы прочитать

for tweet in ser:
    tweet = tweet.replace('\n', ' ')
    check = scan_a_tweet(tweet.replace('\n', ''))
    if (len(check['pos_words']) != 0 and len(check['neg_emoticons'])!=0) or (len(check['neg_words']) != 0 and len(check['pos_emoticons']) != 0):
        if len(check['pos_words']) != 0 and len(check['neg_emoticons']) != 0:
             construct = tweet + '$$' + check['pos_words'][0] + '$$' + check['neg_emoticons'][0]
             with open('emoticon_token.csv', 'a') as f:
                f.write(construct)
        elif len(check['neg_words']) != 0 and len(check['pos_emoticons']) != 0:
            construct = tweet + '$$' + check['neg_words'][0] + '$$' + check['pos_emoticons'][0] + "\n"
            with open('emoticon_token.csv', 'a') as f:
                f.write(construct)
    if len(check['neg_words']) != 0 and len(check['pos_words']) != 0:
        construct = tweet + '$$' + check['neg_words'][0] + '$$' + check['pos_words'][0] + "\n"
        with open('two_tokens.csv', 'a') as f:
            f.write(construct)
    if len(check['neg_emoticons']) != 0 and len(check['pos_emoticons']) != 0:
        construct = tweet + '$$' + check['neg_emoticons'][0] + '$$' + check['pos_emoticons'][0] + '\n'
        with open('Two_emoticons.csv', 'a') as f:
            f.write(construct)
    if len(check['neg_emoticons']) != 0 or len(check['pos_emoticons']) != 0 and len(check['pos_words']+check['neg_words']) == 0:
        emotes = check['neg_emoticons'] + check['pos_emoticons']
        construct = tweet + '$$' + emotes[0] + "\n"
        with open('emoticon_no_token.csv', 'a') as f:
            f.write(construct)
    if len(check['negation']) != 0 and len(check['pos_emoticons'] + check['neg_emoticons']) != 0:
        words = check['neg_emoticons'] + check['pos_emoticons']
        construct = tweet + '$$' + check['negation'][0] + '$$' + words[0] + '\n'
        with open('not_token.csv', 'a') as f:
            f.write(construct)
