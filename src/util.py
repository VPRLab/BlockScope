import os
import time
import pytz

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

from src.configs import S_SIM_THRESHOLD, CODE_SIM_WEIGHT, CONTEXT_LINES, ENDS_TUPLE, DRIVER_PATH


def select_code_lines(code_lines, line_num, up_or_down, lines=CONTEXT_LINES, end=None):
    """
    This function fetch the surrounding code lines of the given code line,
    excluding comments, empty lines, and single brackets.
    :param code_lines:
    :param line_num:
    :param up_or_down:
    :param lines:
    :param end:
    :return:
    """
    result = list()

    current_line = line_num - 1
    is_block_comment = False

    if up_or_down == 'up':

        while (len(code_lines) > current_line - 1) and (code_lines[current_line - 1].strip().endswith(ENDS_TUPLE)):
            current_line += 1

        while len(result) < lines and current_line > 0:
            current_line -= 1
            fetch_line = code_lines[current_line].strip()
            fetch_line = fetch_line.strip(';')
            fetch_line = fetch_line.strip()

            # check whether empty
            if len(fetch_line) <= 0:
                continue

            # check whether single bracket
            if fetch_line in ['{', '}']:
                continue

            # check whether single comment
            if fetch_line.startswith('//'):
                continue

            # check whether block comment
            if fetch_line.startswith('/*') and fetch_line.endswith('*/'):
                continue
            if fetch_line.endswith('*/'):
                is_block_comment = True
                continue
            if fetch_line.startswith('/*') and is_block_comment:
                is_block_comment = False
                continue
            if is_block_comment:
                continue

            # hit is in the block comment
            if fetch_line.startswith('/*') and not is_block_comment:
                # print('* HIT BLOCK COMMENT *')
                result = list()
                continue

            # remove inline comment
            if '//' in fetch_line:
                fetch_line = fetch_line[:fetch_line.find('//')]
            while '/*' in fetch_line and '*/' in fetch_line:
                fetch_line = fetch_line[:fetch_line.find('/*')] + fetch_line[fetch_line.find('*/') + 2:]

            if len(result) and fetch_line.strip().endswith(ENDS_TUPLE):
                result[-1] = (result[-1][0], fetch_line + result[-1][1])
            else:
                result.append(
                    (current_line + 1, fetch_line)
                )

    elif up_or_down == 'down':

        if end:
            lines = 99999
            while code_lines[end].strip().endswith(ENDS_TUPLE):
                end += 1
            code_lines = code_lines[:end]

        while (len(code_lines) > current_line) and (code_lines[current_line].strip().endswith(ENDS_TUPLE)):
            current_line -= 1

        is_whole_line = True

        while len(result) < lines and current_line < len(code_lines) - 1:
            current_line += 1
            fetch_line = code_lines[current_line].strip()
            fetch_line = fetch_line.strip(';')
            fetch_line = fetch_line.strip()

            # check whether empty
            if len(fetch_line) <= 0:
                continue

            # check whether single bracket
            if fetch_line in ['{', '}']:
                continue

            # check whether single comment
            if fetch_line.startswith('//'):
                continue

            # check whether block comment
            if fetch_line.startswith('/*') and fetch_line.endswith('*/'):
                continue
            if fetch_line.startswith('/*'):
                is_block_comment = True
                continue
            if fetch_line.endswith('*/') and is_block_comment:
                is_block_comment = False
                continue
            if is_block_comment:
                continue

            # hit is in the block comment
            if fetch_line.endswith('*/') and not is_block_comment:
                # print('* HIT BLOCK COMMENT *')
                result = list()
                continue

            # remove inline comment
            if '//' in fetch_line:
                fetch_line = fetch_line[:fetch_line.find('//')]
            while '/*' in fetch_line and '*/' in fetch_line:
                fetch_line = fetch_line[:fetch_line.find('/*')] + fetch_line[fetch_line.find('*/') + 2:]

            if is_whole_line:
                result.append(
                    (current_line + 1, fetch_line)
                )
                if fetch_line.strip().endswith(ENDS_TUPLE):
                    is_whole_line = False
                    lines += 1
            else:
                if len(result):
                    result[-1] = (current_line + 1, result[-1][1] + fetch_line)
                else:
                    result.append(
                        (current_line + 1, fetch_line)
                    )
                if not fetch_line.strip().endswith(ENDS_TUPLE):
                    is_whole_line = True

        if len(result) and result[-1][1].endswith(ENDS_TUPLE):
            result.pop()

    # print(result)
    return result


def correlate_hit_infos(up_hit_infos, down_hit_infos):
    """

    :param up_hit_infos:
    :param down_hit_infos:
    :return:
    """
    result = dict()

    temp_dict = dict()
    for up_hit_info in up_hit_infos:
        temp_key = up_hit_info['file_path']
        if temp_key in temp_dict:
            temp_dict[temp_key]['up'].append(
                (min(up_hit_info['mid'])[0], max(up_hit_info['mid'])[0], up_hit_info['func_name'])
            )
        else:
            temp_dict[temp_key] = {'up': [
                (min(up_hit_info['mid'])[0], max(up_hit_info['mid'])[0], up_hit_info['func_name'])
            ]}
    for down_hit_info in down_hit_infos:
        temp_key = down_hit_info['file_path']
        if temp_key in temp_dict:
            if 'down' in temp_dict[temp_key]:
                temp_dict[temp_key]['down'].append(
                    (min(down_hit_info['mid'])[0], max(down_hit_info['mid'])[0], down_hit_info['func_name'])
                )
            else:
                temp_dict[temp_key]['down'] = [
                    (min(down_hit_info['mid'])[0], max(down_hit_info['mid'])[0], down_hit_info['func_name'])
                ]
        else:
            temp_dict[temp_key] = {'down': [
                (min(down_hit_info['mid'])[0], max(down_hit_info['mid'])[0], down_hit_info['func_name'])
            ]}

    for key in temp_dict:
        f_pairs = list()
        f_ups = list()
        f_downs = list()

        if 'up' in temp_dict[key] and 'down' in temp_dict[key]:
            temp_list = list()
            for i in temp_dict[key]['up']:
                for j in temp_dict[key]['down']:
                    if i[1] <= j[0]:
                        temp_list.append(
                            (j[0] - i[1], (i, j))
                        )

            temp_list_copy = temp_list.copy()
            while len(temp_list):
                temp_item = min(temp_list)
                f_pairs.append(temp_item[1])
                for i in temp_list_copy:
                    if i[1][0] in temp_item[1] or i[1][1] in temp_item[1]:
                        if i in temp_list:
                            temp_list.remove(i)

            all_pair_ups = [i[0] for i in f_pairs]
            all_pair_downs = [i[1] for i in f_pairs]
            for i in temp_dict[key]['up']:
                if i not in all_pair_ups:
                    f_ups.append(i)
            for i in temp_dict[key]['down']:
                if i not in all_pair_downs:
                    f_downs.append(i)

        else:
            for up_down in temp_dict[key]:
                for i in temp_dict[key][up_down]:
                    if up_down == 'up':
                        f_ups.append(i)
                    else:
                        f_downs.append(i)

        result[key] = {
            'pairs': f_pairs,
            'ups': f_ups,
            'downs': f_downs
        }

    # print(result)
    return result


def determine_overlap_hits(del_hits, add_hits):
    """

    :param del_hits:
    :param add_hits:
    :return:
    """
    f_del_hits = del_hits.copy()
    f_add_hits = add_hits.copy()
    f_lap_hits = list()

    for add_hit in add_hits:
        for del_hit in del_hits:
            if del_hit['repo_dir'] == add_hit['repo_dir'] \
                    and del_hit['file_path'] == add_hit['file_path']:

                del_range = set(range(del_hit['up_line'][0], del_hit['down_line'][0] + 1))
                add_range = set(range(add_hit['up_line'][0], add_hit['down_line'][0] + 1))

                if len(del_range.intersection(add_range)):
                    if del_hit in f_del_hits and add_hit in f_add_hits:
                        f_lap_hits.append(add_hit)
                        f_del_hits.remove(del_hit)
                        f_add_hits.remove(add_hit)
                        break

    return f_del_hits, f_add_hits, f_lap_hits


def determine_hit_range(hits, patch_start, patch_end, lines=CONTEXT_LINES, sim_thres=S_SIM_THRESHOLD):
    """

    :param hits:
    :param patch_start:
    :param patch_end:
    :param lines:
    :param sim_thres:
    :return:
    """
    result = list()

    for hit in hits:
        hit_repo = hit['repo_dir']
        hit_file = hit['file_path']
        hit_func = hit['func_info']
        hit_line = hit['line_info']
        hit_key_offset = hit['key_offset']

        max_up_attempts = hit_key_offset[0] + lines
        max_down_attempts = hit_key_offset[1] + lines

        abs_path = os.path.join(hit_repo, hit_file)
        with open(abs_path, 'r', encoding='utf-8') as f:
            code_lines = f.readlines()

        up_hit_lines = select_code_lines(code_lines, hit_line[0] + 1, 'up', lines=max_up_attempts)
        down_hit_lines = select_code_lines(code_lines, hit_line[0] - 1, 'down', lines=max_down_attempts)

        up_temp_list = list()
        for up_hit_line in up_hit_lines[:-1]:
            up_temp_list.append(
                (up_hit_line, calc_code_sim([up_hit_line], [patch_start]))
            )
        up_temp_list = sorted(up_temp_list, key=lambda tup: tup[1])
        if len(up_temp_list) and up_temp_list[-1][1] >= sim_thres:
            line_index = up_hit_lines.index(up_temp_list[-1][0])
            up_line = up_hit_lines[line_index + 1]
        else:
            continue

        down_temp_list = list()
        for down_hit_line in down_hit_lines[:-1]:
            down_temp_list.append(
                (down_hit_line, calc_code_sim([down_hit_line], [patch_end]))
            )
        down_temp_list = sorted(down_temp_list, key=lambda tup: tup[1])
        if len(down_temp_list) and down_temp_list[-1][1] >= sim_thres:
            line_index = down_hit_lines.index(down_temp_list[-1][0])
            down_line = down_hit_lines[line_index + 1]
        else:
            continue

        temp_dict = {
                'repo_dir': hit_repo,
                'file_path': hit_file,
                'func_info': hit_func,
                'up_line': up_line,
                'down_line': down_line,
            }

        if temp_dict not in result:
            result.append(temp_dict)

    # print(result)
    return result


def select_best_searched(search_results):
    """

    :param search_results:
    :return:
    """
    temp_dict = dict()
    for s_result in search_results:
        temp_key = (s_result['file_path'], s_result['func_info'])
        if temp_key in temp_dict:
            if s_result['line_sim'] >= temp_dict[temp_key]['line_sim']:
                temp_dict[temp_key] = s_result
        else:
            temp_dict[temp_key] = s_result

    result = [temp_dict[key] for key in temp_dict]
    return result


def calc_code_sim(origin, target, r=CODE_SIM_WEIGHT):
    """
    This function calculates the two inputs' "weighted" similarity,
    specifically, the two inputs contain ordered list of code lines, i.e.,
    origin: [0, 1, 2, 3, ...], and
    target: [0, 1, 2, 3, ...],
    their similarity is measured by:
    SUM(SIM(i, j) * r ^ |i - j|) / LEN(origin),
    where SIM is the similarity between origin[i] and target[j]
    r is a parameter of weight, default 0.8
    The output is a float value from 0 ~ 1.
    :param origin:
    :param target:
    :param r:
    :return:
    """
    leven_sim = NormalizedLevenshtein().similarity

    result = 0
    if len(origin) and len(target):
        for i in range(len(origin)):
            high_index = 0
            high_sim = 0
            for j in range(len(target)):
                temp_sim = leven_sim(origin[i][1], target[j][1])
                if temp_sim >= high_sim:
                    high_sim = temp_sim
                    high_index = j
            weight_sim = high_sim * pow(r, abs(i - high_index))
            result += weight_sim
        # normalize similarity to [0, 1]
        result /= len(origin)

    # print(result)
    return result


def determine_time_delay(blame_info, merge_info, release_info, original_info):
    """

    :param blame_info:
    :param merge_info:
    :param release_info:
    :param original_info:
    :return:
    """
    result = dict()

    if not blame_info:
        commit_delay_days = None
        commit_sha = None
    else:
        commit_sha = blame_info['sha']
        commit_delay = blame_info['committer_date'] - original_info['committer_date']
        commit_delay_days = commit_delay.total_seconds() / (60 * 60 * 24)

    if not merge_info:
        merge_delay_days = None
        merge_pr = None
    else:
        merge_time = pytz.utc.localize(merge_info.merged_at)
        merge_pr = merge_info.number
        merge_delay = merge_time - original_info['committer_date']
        merge_delay_days = merge_delay.total_seconds() / (60 * 60 * 24)

    if not release_info:
        release_delay_days = None
        release_tag = None
    else:
        release_time = pytz.utc.localize(release_info.published_at)
        release_tag = release_info.tag_name
        release_delay = release_time - original_info['committer_date']
        release_delay_days = release_delay.total_seconds() / (60 * 60 * 24)

    result = {
        'SHA': commit_sha,
        'COMMIT DELAY': commit_delay_days,
        'PR': merge_pr,
        'MERGE DELAY': merge_delay_days,
        'TAG': release_tag,
        'RELEASE DELAY': release_delay_days
    }
    return result


def get_commit_pr(commit_url):
    """

    :param commit_url:
    :return:
    """
    result = None

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)

    commit_url = commit_url.replace('commit', 'branch_commits')

    driver.get(commit_url)
    time.sleep(3)

    try:
        pr_class = driver.find_element(By.XPATH, '//ul[@class="branches-list"]')
        pr_item = pr_class.find_element(By.CLASS_NAME, 'pull-request')
        pr_number = pr_item.find_element(By.TAG_NAME, 'a')

        result = int(pr_number.text[1:])

    except NoSuchElementException:
        print('ERR', commit_url)
    except ValueError:
        print('ERR', commit_url)

    driver.quit()
    return result


def get_commit_tags(commit_url):
    """

    :param commit_url:
    :return:
    """
    result = list()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)

    commit_url = commit_url.replace('commit', 'branch_commits')

    driver.get(commit_url)
    time.sleep(3)

    try:
        tag_class = driver.find_element(By.XPATH, '//ul[@class="branches-tag-list js-details-container"]')
        tag_list = tag_class.find_elements(By.TAG_NAME, 'li')
        for tag in tag_list:
            tag_text = tag.text
            if tag_text and tag_text != '…':
                result.append(tag_text)

    except NoSuchElementException:
        print('ERR', commit_url)

    driver.quit()
    return result
