import os
import pydriller
import re

from src.util import select_code_lines, calc_code_sim


def fetch_hit_info(hit, origin_func, add_del_lines=None):
    """
    This function fetches the contexts of the hit,
    which takes the hit dict as input,
    and outputs the 'meaningful' surrounding code lines.
    :param origin_func:
    :param hit:
    :param add_del_lines:
    :return:
    """
    hit_repo = hit['repo_dir']
    hit_file = hit['file_path']
    hit_func = hit['func_info']
    hit_up = hit['up_line']
    hit_down = hit['down_line']

    # exclude non-similar-func
    if hit_func and origin_func:
        t_func = re.split(r' |::', hit_func[1])[-1].lower()
        # t_func = hit_func[1].split(' ')[-1].lower()
        func_sim = calc_code_sim([(0, origin_func)], [(0, t_func)])
        if func_sim < 0.7:
            return None

    abs_path = os.path.join(hit_repo, hit_file)
    with open(abs_path, 'r', encoding='utf-8') as f:
        code_lines = f.readlines()

    if not hit_up:
        down_lines = select_code_lines(code_lines, hit_down[0], 'up', lines=add_del_lines)
        hit_up = (min(down_lines)[0] - 1, '')
    if not hit_down:
        up_lines = select_code_lines(code_lines, hit_up[0], 'down', lines=add_del_lines)
        hit_down = (max(up_lines)[0] + 1, '')

    up_code_lines = select_code_lines(code_lines, hit_up[0] + 1, 'up')
    result = {
        'repo_dir': hit_repo,
        'file_path': hit_file,
        'func_name': hit_func[1],
        'up': sorted(up_code_lines, key=lambda tup: tup[0]),
        'down': select_code_lines(code_lines, hit_down[0] - 1, 'down'),
        'mid': select_code_lines(code_lines, hit_up[0], 'down', end=hit_down[0] - 1)
    }

    # print(result)
    return result


def fetch_commit_info(repo_dir, sha, file_path=None, del_info=None, add_info=None, general_only=False):
    """
    This function fetches the contexts of the commit,
    which takes the sha, file path, and code hunk range as input,
    and outputs the 'meaningful' surrounding code lines.
    :param repo_dir:
    :param sha:
    :param file_path:
    :param del_info:
    :param add_info:
    :param general_only:
    :return:
    """
    result = dict()
    general_result = dict()

    commit_result = pydriller.Repository(repo_dir, single=sha, only_no_merge=True).traverse_commits()
    commits = [commit for commit in commit_result]

    if len(commits) < 1:
        # print('* NO COMMIT FOUND *')
        return result, general_result

    general_result = {
        'sha': commits[0].hash,
        'author': commits[0].author,
        'author_date': commits[0].author_date,
        'author_timezone': commits[0].author_timezone,
        'committer': commits[0].committer,
        'committer_date': commits[0].committer_date,
        'committer_timezone': commits[0].committer_timezone
    }

    if general_only:
        return result, general_result

    for m in commits[0].modified_files:
        if (m.old_path and os.path.normpath(m.old_path) == os.path.normpath(file_path)) \
                or (m.new_path and os.path.normpath(m.new_path) == os.path.normpath(file_path)):
            old_code_lines = m.source_code_before.split('\n')
            new_code_lines = m.source_code.split('\n')

            if del_info and add_info:
                up_code_lines = select_code_lines(old_code_lines, del_info[0], 'up')
                result = {
                    'del': select_code_lines(old_code_lines, del_info[0] - 1, 'down', end=del_info[1]),
                    'add': select_code_lines(new_code_lines, add_info[0] - 1, 'down', end=add_info[1]),
                    'up': sorted(up_code_lines, key=lambda tup: tup[0]),
                    'down': select_code_lines(new_code_lines, add_info[1], 'down')
                }

            elif del_info and (not add_info):
                up_code_lines = select_code_lines(old_code_lines, del_info[0], 'up')
                result = {
                    'del': select_code_lines(old_code_lines, del_info[0] - 1, 'down', end=del_info[1]),
                    'add': None,
                    'up': sorted(up_code_lines, key=lambda tup: tup[0]),
                    'down': select_code_lines(old_code_lines, del_info[1], 'down')
                }

            elif (not del_info) and add_info:
                up_code_lines = select_code_lines(new_code_lines, add_info[0], 'up')
                result = {
                    'del': None,
                    'add': select_code_lines(new_code_lines, add_info[0] - 1, 'down', end=add_info[1]),
                    'up': sorted(up_code_lines, key=lambda tup: tup[0]),
                    'down': select_code_lines(new_code_lines, add_info[1], 'down')
                }

            break

    return result, general_result
