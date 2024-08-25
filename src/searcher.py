import re
import git
from nltk import RegexpTokenizer

from src.util import calc_code_sim
from src.configs import S_SIM_THRESHOLD, ENDS_TUPLE


def basic_search(repo_dir, key_tup, origin_file, sim_thres=S_SIM_THRESHOLD):
    """
    This function does the basic search,
    which takes a regular expression as the input,
    and search for all the hits in the given repo.
    :param origin_file:
    :param repo_dir:
    :param key_tup:
    :param sim_thres:
    :return:
    """
    result = list()

    keyword = key_tup[0]
    origin_line = key_tup[1]
    key_offset = key_tup[2]

    repo = git.Repo(repo_dir)
    try:
        raw_output = repo.git.grep('-Epni', keyword)
        # print(raw_output)
    except git.exc.GitCommandError:
        # print('* NO RESULT FOUND *')
        return result
    else:
        origin_suffix = origin_file.split('.')[-1].lower()
        raw_output = raw_output.split('\n')
        func_name = None
        func_line = None
        for temp_str in raw_output:
            is_func_str = re.search(r'(.+?)=(\d+)=(.+?)', temp_str)
            is_hit_str = re.search(r'(.+?):(\d+):(.+?)', temp_str)
            if is_func_str:
                func_items = temp_str.split('=', 2)
                try:
                    func_line = int(func_items[1])
                    func_name = func_items[2].split('(')[0]
                except ValueError:
                    continue
            elif is_hit_str:
                hit_items = temp_str.split(':', 2)
                file_path = hit_items[0]
                file_suffix = file_path.split('.')[-1].lower()

                # only consider code files
                if (file_suffix == origin_suffix) \
                        and ('test' not in file_path.lower()):
                    raw_line = hit_items[2].strip()

                    # exclude test func
                    if func_name and 'test' in func_name.lower():
                        continue

                    # exclude comments
                    if raw_line.startswith('//') \
                            or raw_line.startswith('/*') \
                            or raw_line.endswith('*/'):
                        continue

                    # remove inline comment
                    if '//' in raw_line:
                        raw_line = raw_line[:raw_line.find('//')]
                    while '/*' in raw_line and '*/' in raw_line:
                        raw_line = raw_line[:raw_line.find('/*')] + raw_line[raw_line.find('*/') + 2:]

                    # only consider exact token
                    r_tokens = set(RegexpTokenizer(r'[a-zA-Z0-9_.~!]+').tokenize(raw_line.lower()))
                    if keyword.lower() not in r_tokens:
                        continue

                    # exclude different statement type
                    type_set = {'if', 'for', 'while',
                                'return', 'assert', 'throw',
                                'explicit', 'char', 'else'}
                    o_tokens = set(RegexpTokenizer(r'[a-zA-Z0-9_.~!]+').tokenize(origin_line[1].lower()))
                    o_type = type_set.intersection(o_tokens)
                    r_type = type_set.intersection(r_tokens)
                    if o_type != r_type:
                        continue

                    # calculate similarity of hit line and original line
                    line_info = (int(hit_items[1]), raw_line)
                    # if line ends with ',', only consider the same length
                    if raw_line.endswith(ENDS_TUPLE) \
                            and len(raw_line) <= len(origin_line[1]):
                        line_sim = calc_code_sim([(origin_line[0], origin_line[1][:len(raw_line)])], [line_info])
                    else:
                        line_sim = calc_code_sim([origin_line], [line_info])

                    # only consider lines have high similarity
                    if line_sim >= sim_thres:
                        result.append(
                            {
                                'repo_dir': repo_dir,
                                'file_path': hit_items[0],
                                'func_info': (func_line, func_name),
                                'line_info': line_info,
                                'line_sim': line_sim,
                                'key_offset': key_offset
                            }
                        )

    # print(result)
    return result
