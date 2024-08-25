from nltk import RegexpTokenizer
from src.configs import COMMON_KEYWORDS


def extract_patch_keyinfo(patch_info):
    """
    :param patch_info:
    :return:
    """
    result = dict()

    for key in patch_info:
        if patch_info[key]:
            start = patch_info[key][0]
            end = patch_info[key][-1]
            keywords = list()

            for idx, line in enumerate(patch_info[key]):
                tokens = set(RegexpTokenizer(r'[a-zA-Z0-9_.~!]+').tokenize(line[1]))

                temp_token_list = list()
                if len(tokens):
                    for token in tokens:
                        if (len(token) < 5) or (all(c.islower() for c in token)) or (token.lower() in COMMON_KEYWORDS):
                            continue
                        else:
                            temp_token_list.append(token)

                if len(temp_token_list):
                    long_token = sorted(temp_token_list, key=lambda tok: len(tok))[-1]
                    keyword_tup = (long_token, line, (idx, len(patch_info[key]) - idx - 1))
                    keywords.append(keyword_tup)

            if len(keywords):
                result[key] = {
                    'start': start,
                    'end': end,
                    'key': keywords
                }
            else:
                result[key] = None
        else:
            result[key] = None

    # print(result)
    return result
