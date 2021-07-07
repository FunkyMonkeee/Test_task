import requests
from random import randint
from emoji import demojize, emojize


def main():
    req = requests.get("https://www.labinform.ru/pub/rusentilex/rusentilex_2017.txt").text
    dict_of_pos_neg_words = create_a_dictionary(req)
    print("и" in dict_of_pos_neg_words['positive'] or "и" in dict_of_pos_neg_words['negative'] or "и" in dict_of_pos_neg_words['positive/negative'])
    ser = open(input('enter a path to a csv')).readlines()
    for tweet in ser:
        move_to_correct_files(tweet, dict_of_pos_neg_words)


def move_to_correct_files(tweet: str, dictionary: dict, key_for_pos='positive', key_for_neg='negative', key_for_positive_neg="positive/negative" ):
    """scans a tweet and moves it into the correct file
    :param
        tweet: text of a tweet
        dictionary: a dictionary of toned words and emoticons"""

    # сначала мы сканируем твит

    tweet = tweet.replace('\n', ' ')
    check = scan_a_tweet(tweet.replace('\n', ''), dictionary, key_for_pos, key_for_neg, key_for_positive_neg)

    # теперь в зависимости от того что мы там нашли записываем в нужный файл
    # ну например если в твите нашлись позитивные и негативные слова, то запишем его в two_token

    if (len(check['pos_words']) != 0 and len(check['neg_emoticons']) != 0) or (
            len(check['neg_words']) != 0 and len(check['pos_emoticons']) != 0):
        if len(check['pos_words']) != 0 and len(check['neg_emoticons']) != 0:
            construct = tweet + ',' + check['pos_words'][0] + ',' + check['neg_emoticons'][0]
            with open('emoticon_token.csv', 'a') as f:
                f.write(construct)
        elif len(check['neg_words']) != 0 and len(check['pos_emoticons']) != 0:
            construct = tweet + ',' + check['neg_words'][0] + ',' + check['pos_emoticons'][0] + "\n"
            with open('emoticon_token.csv', 'a') as f:
                f.write(construct)
    if len(check['neg_words']) != 0 and len(check['pos_words']) != 0:
        construct = tweet + ',' + check['neg_words'][0] + ',' + check['pos_words'][0] + "\n"
        with open('two_tokens.csv', 'a') as f:
            f.write(construct)
    if len(check['neg_emoticons']) != 0 and len(check['pos_emoticons']) != 0:
        construct = tweet + ',' + check['neg_emoticons'][0] + ',' + check['pos_emoticons'][0] + '\n'
        with open('Two_emoticons.csv', 'a') as f:
            f.write(construct)
    if len(check['neg_emoticons']) != 0 or len(check['pos_emoticons']) != 0 and len(
            check['pos_words'] + check['neg_words']) == 0:
        emotes = check['neg_emoticons'] + check['pos_emoticons']
        construct = tweet + ',' + emotes[0] + "\n"
        with open('emoticon_no_token.csv', 'a') as f:
            f.write(construct)
    if len(check['negation']) != 0 and len(check['pos_emoticons'] + check['neg_emoticons']) != 0:
        words = check['neg_emoticons'] + check['pos_emoticons']
        construct = tweet + ',' + check['negation'][0] + ',' + words[0] + '\n'
        with open('not_token.csv', 'a') as f:
            f.write(construct)


def create_a_dictionary(dictionary_text: str, key_for_pos='positive', key_for_neg='negative', key_for_positive_neg="positive/negative"):
    """creates a dictionary of 3 sets for positive, negative and ambivalent words
    :param
        dictionary_text: string from which we create a dictionary
        key_for_pos: a key for positive words in a return dictionary(positive is a default)
        key_for_neg: a key for negative words in a return dictionary(negative is a default)
        key_for_positive_neg: a key for pos_negative words in a return dictionary(positive/negative is a default)
        """
    v_endings = ['ешь', 'ет', 'ем', 'ете', 'ут', 'ют', 'ишь', 'ит', 'им', 'ите', 'aт', 'ят', 'л', 'ла', 'ло']
    n_endings = ['ы', "и", 'а', 'я', 'у', 'ов', 'ей', 'е', 'ам', 'ям', 'ю', 'ом', 'ой', 'ою', 'ью', 'ами', 'ями', 'ми',
                 'ах', 'ях']
    adj_endings = ['ой', "ей", "ий" "ая", "яя", "ья", "ые", "ие", "ом", "ем", "ую", "юю", "ое", "ее", "ому", "ему",
                   "ыми", "ими", "ему"]

    # в зависимости от части речи мы устанавливаем возможные окончания для слов и словосочетаний
    # и добавляет в словарь все возможные случаи

    intonations = {"positive": set([]), 'negative': set([]), 'positive/negative': set([])}
    for line in dictionary_text.split("\r\n")[19:-1]:
        if line.split(", ")[3] in ['positive', 'negative', 'positive/negative']:
            if line.split(", ")[1] == 'Verb':
                if line.split(", ")[0][-2:] in ['ся', "сь"]:
                    for ending in v_endings:
                        intonations[line.split(", ")[3]].add(
                            line.split(", ")[0][:-4] + ending + line.split(", ")[0][-2:])
                    intonations[line.split(", ")[3]].add(line.split(", ")[0])
                else:
                    for ending in v_endings:
                        intonations[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
                    intonations[line.split(", ")[3]].add(line.split(", ")[0])
            elif line.split(", ")[1] == 'Noun':
                for ending in n_endings:
                    intonations[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
                intonations[line.split(", ")[3]].add(line.split(", ")[0])
            elif line.split(', ')[1] == 'Adj':
                for ending in adj_endings:
                    intonations[line.split(", ")[3]].add(line.split(", ")[0][:-2] + ending)
                intonations[line.split(", ")[3]].add(line.split(", ")[0])

    # Подчищаем словарь от слов с одной буквой
    # (просто если у слова с 3-мя буквами убрать последние 2 и поставить нулевое окончание, то
    # будет одна буква в словаре и будет находить союзы как тональные слова

    for letter in "йцукенгшщзхъфывапролджэёячсмитьбю":
        for letter_2 in "йцукенгшщзхъфывапролджэёячсмитьбю":
            if letter in intonations["positive"]:
                intonations["positive"].remove(letter)
            if letter in intonations["negative"]:
                intonations['negative'].remove(letter)
            if letter in intonations["positive/negative"]:
                intonations['positive/negative'].remove(letter)
            if letter+letter_2 in intonations["positive"]:
                intonations["positive"].remove(letter+letter_2)
            if letter+letter_2 in intonations["negative"]:
                intonations['negative'].remove(letter+letter_2)
            if letter+letter_2 in intonations["positive/negative"]:
                intonations['positive/negative'].remove(letter+letter_2)


    return intonations

def emoji_search(text: str, pos_emoji_keywords: list, neg_emoji_keywords: list):
    """ searches for emoji in a given text
    :param
            text: a string in which emoji wanted to be detected
            neg_emoji_keywords: list of keywords or parts to detect negative emoji
            neg_emoji_keywords: list of keywords or parts to detect negative emoji

    :returns
        a list with two elements in it: list of positive emoji and list of negative emoji
    :rtype
        list"""

    emoji = [[], []]
    text = demojize(text).split(':')
    for i in range(len(text)):
        part = text[i]
        pos = False

        # детектим эмоджи и проверяем его на тональность в зависимости от ключевых слов,
        # которые мы указали ранее как параметры

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

    # в твите ищем несколько подряд символов которые мы указали в acceptable symbols
    # если наберётся несколько подряд мы нашли текстовый эмоджи
    # и если там есть "(" - эмоджи негативный, если ")" - негативный


    emoji =[[], []]
    twit_1 = text.replace('::', '')
    emote = ''
    for symbol in twit_1:
        if symbol in acceptable_symbols:
            emote += symbol
        elif len(emote) >= 2:
            if ')' in emote:
                emoji[0].append(emote)
                emote = ''
            elif '(' in emote:
                emoji[1].append(emote)
                emote = ''
            else:
                emote = ''
        else:
            emote = ''
    return emoji


def token_scan(text: str, positive_key: str, negative_key: str, positive_negative_key: str, dict_of_pos_neg_words: dict, num_of_pos_emote=0,  num_of_neg_emote=0):
    """ finds negative and positive words and combinations in a given text"
    :param
            text: text we want to scan
            positive_key: a key for positive words in a dictionary
            negative_key: a key for negative words in a dictionary
            positive_negative_key: a key for pos_neg_words
            dict_of_pos_neg_words: dictionary of toned words
            num_of_neg_emote: number of negative emoticons (0 is a default value)
            num_of_pos_emote: number of positive emotes (0 is a default value)
    :returns
        a list of 2 lists with positive (1st list), negative (2nd list), and negations (3rd list) words and word combinations if they are in a tweet
    :rtype
        list"""

    message = text
    for character in message:
        if not character.isalpha():
            text.replace(character, '')

    text = text.split()
    positive_negative = []
    tokens = [[], [], []]
    for word in text:
        if word in ['не', "ни"]:
            tokens[2].append(word)
        elif word in dict_of_pos_neg_words[positive_key]:
            tokens[0].append(word)
        elif word in dict_of_pos_neg_words[negative_key]:
            tokens[1].append(word)
        elif word in dict_of_pos_neg_words[positive_negative_key]:
            positive_negative.append(word)

    # если тон слова зависит от контекста проверяем больше ли в твите поpитивных или негативных эиотиконов

    if (len(tokens[0]) == 0 or len(tokens[1]) == 0) and len(tokens[2]) != 0:
        if len(tokens[0]) + num_of_pos_emote > len(tokens[1]) + num_of_neg_emote:
            tokens[0].append(tokens[2][0])
        elif len(tokens[0]) + num_of_pos_emote < len(tokens[1]) + num_of_neg_emote:
            tokens[1].append(tokens[2][0])
        else:
            r = randint(0, 1)
            if r == 1:
                tokens[1].append(tokens[2][0])
            else:
                tokens[0].append(tokens[2][0])
    return tokens


def scan_a_tweet(tweet: str, dictionary:dict, positive_key: str, negative_key: str, positive_negative_key: str):
    """finds positive and negative words and emoticons in a tweet
    :param
        tweet: text of a tweet
        dictionary: dictionary of toned words
        positive_key: key for positive words in a dictionary
        negative_key:  key for negative words words in a ditcionary
        :returns
            a dictionary with positive words, negative words, negation words, positive emoticons, negative emoticons with keys:
             pos_words, neg_words, negation, pos_emoticons, neg_emoticons, respectively"""

    emotes = emoji_search(tweet, ['laugh', 'heart', 'kiss', 'smil', 'joy', 'up', 'fire', 'star'], ['angr', 'fear', 'rag', 'disap', 'sweat', 'down'])
    text_emotes = text_emoji_search(tweet,':)(;')
    tokens = token_scan(tweet, positive_key, negative_key, positive_negative_key, dictionary, num_of_pos_emote=len(text_emotes[0]) + len(emotes[0]), num_of_neg_emote=len(emotes[1])+len(text_emotes[1]))
    return {"pos_words": tokens[0], "neg_words": tokens[1], 'negation': tokens[2], 'pos_emoticons': emotes[0] + text_emotes[0], 'neg_emoticons': emotes[1]+text_emotes[1]}


if __name__ == "__main__":
    main()
