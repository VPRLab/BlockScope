"""
BlockScope aims to find unpatched vulnerabilities in forked blockchain projects.
If the vulnerability is indeed patched,
we also retrieve its patched date to determine the delay.
"""

from src.fetcher import fetch_hit_info, fetch_commit_info
from src.extractor import extract_patch_keyinfo
from src.searcher import basic_search
from src.blamer import get_blame_info, get_merge_info, get_release_info
from src.util import determine_hit_range, calc_code_sim, determine_overlap_hits
from src.util import correlate_hit_infos, determine_time_delay, select_best_searched
from src.configs import F_SIM_THRESHOLD, CALC_DELAY, IS_BITCOIN

if IS_BITCOIN:
    from src.inputs_bitcoin import patches, origin_repo, target_repos
else:
    from src.inputs_ethereum import patches, origin_repo, target_repos


def process_patches():
    """

    :return:
    """
    result = list()

    for patch in patches:
        sha = patch['sha']
        code_file = patch['file']

        func_info = None
        if 'func' in patch:
            func_info = patch['func']

        add_info = patch['add_info']
        del_info = patch['del_info']

        if add_info and del_info:
            patch_type = 'CHA'
        elif add_info and (not del_info):
            patch_type = 'ADD'
        elif (not add_info) and del_info:
            patch_type = 'DEL'
        else:
            print('* INCORRECT PATCH TYPE *')
            return None

        up_info = patch['up_info']
        down_info = patch['down_info']

        patch_info, general_info = fetch_commit_info(
            origin_repo,
            sha,
            code_file,
            del_info=del_info,
            add_info=add_info,
        )
        # print(patch_info)

        if ('up' not in patch_info) or ('down' not in patch_info):
            print('* NOT VALID COMMIT *')
            return None

        key_info = extract_patch_keyinfo(patch_info)
        # print(key_info)

        result.append(
            {
                'sha': sha,
                'code_file': code_file,
                'func_info': func_info,
                'patch_type': patch_type,
                'up_info': up_info,
                'down_info': down_info,
                'patch_info': patch_info,
                'general_info': general_info,
                'key_info': key_info
            }
        )

    return result


def main(target_repo, patch):
    """

    :return:
    """
    func_info = patch['func_info']
    patch_type = patch['patch_type']
    up_info = patch['up_info']
    down_info = patch['down_info']
    patch_info = patch['patch_info']
    general_info = patch['general_info']
    key_info = patch['key_info']
    code_file = patch['code_file']

    valid_up_hit_infos = list()
    if up_info:
        patch_up_start = key_info['up']['start']
        patch_up_end = key_info['up']['end']
        patch_up_key = key_info['up']['key']

        search_result = list()
        for i in patch_up_key:
            search_result += basic_search(target_repo, i, code_file)
        up_result = select_best_searched(search_result)
        up_hits = determine_hit_range(up_result, patch_up_start, patch_up_end)

        for up_hit in up_hits:
            up_hit_info = fetch_hit_info(up_hit, func_info)
            if up_hit_info is None:
                continue
            up_similarity = calc_code_sim(patch_info['up'], up_hit_info['mid'])
            if up_similarity >= F_SIM_THRESHOLD:
                valid_up_hit_infos.append(up_hit_info)

    valid_down_hit_infos = list()
    if down_info:
        patch_down_start = key_info['down']['start']
        patch_down_end = key_info['down']['end']
        patch_down_key = key_info['down']['key']

        search_result = list()
        for j in patch_down_key:
            search_result += basic_search(target_repo, j, code_file)
        down_result = select_best_searched(search_result)
        down_hits = determine_hit_range(down_result, patch_down_start, patch_down_end)

        for down_hit in down_hits:
            down_hit_info = fetch_hit_info(down_hit, func_info)
            if down_hit_info is None:
                continue
            down_similarity = calc_code_sim(patch_info['down'], down_hit_info['mid'])
            if down_similarity >= F_SIM_THRESHOLD:
                valid_down_hit_infos.append(down_hit_info)

    pair_result = correlate_hit_infos(valid_up_hit_infos, valid_down_hit_infos)

    found_result = False

    # have delete lines and add lines
    if patch_type == 'CHA':

        cha_result_list = list()

        if len(pair_result):
            for key in pair_result:
                cha_hit_list = list()
                if up_info and down_info:
                    for pair in pair_result[key]['pairs']:
                        cha_hit_list.append(
                            {
                                'repo_dir': target_repo,
                                'file_path': key,
                                'func_info': (0, pair[0][2]),
                                'up_line': (pair[0][1], ''),
                                'down_line': (pair[1][0], '')
                            }
                        )
                else:
                    if up_info:
                        for up in pair_result[key]['ups']:
                            cha_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, up[2]),
                                    'up_line': (up[1], ''),
                                    'down_line': None
                                }
                            )
                    if down_info:
                        for down in pair_result[key]['downs']:
                            cha_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, down[2]),
                                    'up_line': None,
                                    'down_line': (down[0], '')
                                }
                            )
                for cha_hit in cha_hit_list:
                    cha_length = max(len(patch_info['add']), len(patch_info['del']))
                    cha_hit_info = fetch_hit_info(cha_hit, func_info, cha_length)
                    if cha_hit_info is None:
                        continue
                    add_similarity = calc_code_sim(patch_info['add'], cha_hit_info['mid'])
                    del_similarity = calc_code_sim(patch_info['del'], cha_hit_info['mid'])
                    if max(add_similarity, del_similarity) >= F_SIM_THRESHOLD \
                            and add_similarity >= del_similarity:
                        found_result = True
                        cha_result_list.append((cha_hit_info, 'F', add_similarity - F_SIM_THRESHOLD))
                    elif max(add_similarity, del_similarity) >= F_SIM_THRESHOLD \
                            and add_similarity < del_similarity:
                        found_result = True
                        cha_result_list.append((cha_hit_info, 'V', del_similarity - F_SIM_THRESHOLD))

        if not found_result:
            if key_info['del'] is None:
                print("* NO KEYWORD FOR DEL")
                print('* DONE *')
                return None

            patch_del_start = key_info['del']['start']
            patch_del_end = key_info['del']['end']
            patch_del_key = key_info['del']['key']

            search_result = list()
            for i in patch_del_key:
                search_result += basic_search(target_repo, i, code_file)
            del_result = select_best_searched(search_result)
            del_hits = determine_hit_range(del_result, patch_del_start, patch_del_end)

            if key_info['add'] is None:
                print("* NO KEYWORD FOR ADD")
                print('* DONE *')
                return None

            patch_add_start = key_info['add']['start']
            patch_add_end = key_info['add']['end']
            patch_add_key = key_info['add']['key']

            search_result = list()
            for i in patch_add_key:
                search_result += basic_search(target_repo, i, code_file)
            add_result = select_best_searched(search_result)
            add_hits = determine_hit_range(add_result, patch_add_start, patch_add_end)

            del_hits, add_hits, lap_hits = determine_overlap_hits(del_hits, add_hits)

            for del_hit in del_hits:
                del_hit_info = fetch_hit_info(del_hit, func_info)
                if del_hit_info is None:
                    continue
                del_similarity = calc_code_sim(patch_info['del'], del_hit_info['mid'])
                if del_similarity >= F_SIM_THRESHOLD:
                    cha_result_list.append((del_hit_info, 'V', del_similarity - F_SIM_THRESHOLD))
            for add_hit in add_hits:
                add_hit_info = fetch_hit_info(add_hit, func_info)
                if add_hit_info is None:
                    continue
                add_similarity = calc_code_sim(patch_info['add'], add_hit_info['mid'])
                if add_similarity >= F_SIM_THRESHOLD:
                    cha_result_list.append((add_hit_info, 'F', add_similarity - F_SIM_THRESHOLD))
            for lap_hit in lap_hits:
                lap_hit_info = fetch_hit_info(lap_hit, func_info)
                if lap_hit_info is None:
                    continue
                add_similarity = calc_code_sim(patch_info['add'], lap_hit_info['mid'])
                del_similarity = calc_code_sim(patch_info['del'], lap_hit_info['mid'])
                if add_similarity >= del_similarity:
                    cha_result_list.append((lap_hit_info, 'F', add_similarity - F_SIM_THRESHOLD))
                else:
                    cha_result_list.append((lap_hit_info, 'V', del_similarity - F_SIM_THRESHOLD))

        if len(cha_result_list):
            final_cha_result = sorted(cha_result_list, key=lambda tup: tup[2])[-1]
            cha_hit_info = final_cha_result[0]
            fix_or_vuln = final_cha_result[1]
            if fix_or_vuln == 'F':
                if CALC_DELAY:
                    blame_info = get_blame_info(
                        target_repo,
                        cha_hit_info['file_path'], cha_hit_info['mid'],
                        key_info['add']['key']
                    )
                    merger_info = get_merge_info(target_repo, blame_info['sha'])
                    release_info = get_release_info(target_repo, blame_info['sha'])
                    print('* VULN FIXED *')
                    print(determine_time_delay(blame_info, merger_info, release_info, general_info))
                else:
                    print('* VULN FIXED *')
                print('=================================')
                print(target_repo, cha_hit_info['file_path'])
                print('@@', cha_hit_info['func_name'], '@@')
                for item in cha_hit_info['mid']:
                    print(item)
                print('=================================')
            else:
                print('* VULN DETECTED *')
                print('=================================')
                print(target_repo, cha_hit_info['file_path'])
                print('@@', cha_hit_info['func_name'], '@@')
                for item in cha_hit_info['up']:
                    print(item)
                for item in cha_hit_info['mid']:
                    print(item)
                for item in cha_hit_info['down']:
                    print(item)
                print('=================================')

        print('* DONE *')
        return None

    # only have add lines
    if patch_type == 'ADD':

        add_result_list = list()

        if len(pair_result):
            for key in pair_result:
                add_hit_list = list()
                if up_info and down_info:
                    for pair in pair_result[key]['pairs']:
                        add_hit_list.append(
                            {
                                'repo_dir': target_repo,
                                'file_path': key,
                                'func_info': (0, pair[0][2]),
                                'up_line': (pair[0][1], ''),
                                'down_line': (pair[1][0], '')
                            }
                        )
                else:
                    if up_info:
                        for up in pair_result[key]['ups']:
                            add_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, up[2]),
                                    'up_line': (up[1], ''),
                                    'down_line': None
                                }
                            )
                    if down_info:
                        for down in pair_result[key]['downs']:
                            add_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, down[2]),
                                    'up_line': None,
                                    'down_line': (down[0], '')
                                }
                            )
                for add_hit in add_hit_list:
                    add_hit_info = fetch_hit_info(add_hit, func_info, len(patch_info['add']))
                    if add_hit_info is None:
                        continue
                    add_similarity = calc_code_sim(patch_info['add'], add_hit_info['mid'])
                    if add_similarity >= F_SIM_THRESHOLD:
                        found_result = True
                        add_result_list.append((add_hit_info, 'F', add_similarity - F_SIM_THRESHOLD))
                    else:
                        found_result = True
                        add_result_list.append((add_hit_info, 'V', F_SIM_THRESHOLD - add_similarity))

        if not found_result:
            if key_info['add'] is None:
                print("* NO KEYWORD FOR ADD")
                print('* DONE *')
                return None

            patch_add_start = key_info['add']['start']
            patch_add_end = key_info['add']['end']
            patch_add_key = key_info['add']['key']

            search_result = list()
            for i in patch_add_key:
                search_result += basic_search(target_repo, i, code_file)
            add_result = select_best_searched(search_result)
            add_hits = determine_hit_range(add_result, patch_add_start, patch_add_end)

            for add_hit in add_hits:
                add_hit_info = fetch_hit_info(add_hit, func_info)
                if add_hit_info is None:
                    continue
                add_similarity = calc_code_sim(patch_info['add'], add_hit_info['mid'])
                if add_similarity >= F_SIM_THRESHOLD:
                    add_result_list.append((add_hit_info, 'F', add_similarity - F_SIM_THRESHOLD))

        if len(add_result_list):
            final_add_result = sorted(add_result_list, key=lambda tup: tup[2])[-1]
            add_hit_info = final_add_result[0]
            fix_or_vuln = final_add_result[1]
            if fix_or_vuln == 'F':
                if CALC_DELAY:
                    blame_info = get_blame_info(
                        target_repo,
                        add_hit_info['file_path'], add_hit_info['mid'],
                        key_info['add']['key']
                    )
                    merger_info = get_merge_info(target_repo, blame_info['sha'])
                    release_info = get_release_info(target_repo, blame_info['sha'])
                    print('* VULN FIXED *')
                    print(determine_time_delay(blame_info, merger_info, release_info, general_info))
                else:
                    print('* VULN FIXED *')
                print('=================================')
                print(target_repo, add_hit_info['file_path'])
                print('@@', add_hit_info['func_name'], '@@')
                for item in add_hit_info['mid']:
                    print(item)
                print('=================================')
            else:
                print('* VULN DETECTED *')
                print('=================================')
                print(target_repo, add_hit_info['file_path'])
                print('@@', add_hit_info['func_name'], '@@')
                for item in add_hit_info['up']:
                    print(item)
                for item in add_hit_info['mid']:
                    print(item)
                for item in add_hit_info['down']:
                    print(item)
                print('=================================')

        print('* DONE *')
        return None

    # only have delete lines
    if patch_type == 'DEL':

        del_result_list = list()

        if len(pair_result):
            for key in pair_result:
                del_hit_list = list()
                if up_info and down_info:
                    for pair in pair_result[key]['pairs']:
                        del_hit_list.append(
                            {
                                'repo_dir': target_repo,
                                'file_path': key,
                                'func_info': (0, pair[0][2]),
                                'up_line': (pair[0][1], ''),
                                'down_line': (pair[1][0], '')
                            }
                        )
                else:
                    if up_info:
                        for up in pair_result[key]['ups']:
                            del_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, up[2]),
                                    'up_line': (up[1], ''),
                                    'down_line': None
                                }
                            )
                    if down_info:
                        for down in pair_result[key]['downs']:
                            del_hit_list.append(
                                {
                                    'repo_dir': target_repo,
                                    'file_path': key,
                                    'func_info': (0, down[2]),
                                    'up_line': None,
                                    'down_line': (down[0], '')
                                }
                            )
                for del_hit in del_hit_list:
                    del_hit_info = fetch_hit_info(del_hit, func_info, len(patch_info['del']))
                    if del_hit_info is None:
                        continue
                    del_similarity = calc_code_sim(patch_info['del'], del_hit_info['mid'])
                    if del_similarity >= F_SIM_THRESHOLD:
                        del_result_list.append((del_hit_info, 'V', del_similarity - F_SIM_THRESHOLD))
                    else:
                        del_result_list.append((del_hit_info, 'F', F_SIM_THRESHOLD - del_similarity))

        else:
            if key_info['del'] is None:
                print("* NO KEYWORD FOR DEL")
                print('* DONE *')
                return None

            patch_del_start = key_info['del']['start']
            patch_del_end = key_info['del']['end']
            patch_del_key = key_info['del']['key']

            search_result = list()
            for i in patch_del_key:
                search_result += basic_search(target_repo, i, code_file)
            del_result = select_best_searched(search_result)
            del_hits = determine_hit_range(del_result, patch_del_start, patch_del_end)

            for del_hit in del_hits:
                del_hit_info = fetch_hit_info(del_hit, func_info)
                if del_hit_info is None:
                    continue
                del_similarity = calc_code_sim(patch_info['del'], del_hit_info['mid'])
                if del_similarity >= F_SIM_THRESHOLD:
                    del_result_list.append((del_hit_info, 'V', del_similarity - F_SIM_THRESHOLD))

        if len(del_result_list):
            final_del_result = sorted(del_result_list, key=lambda tup: tup[2])[-1]
            del_hit_info = final_del_result[0]
            fix_or_vuln = final_del_result[1]
            if fix_or_vuln == 'F':
                print('* VULN FIXED *')
                print('=================================')
                print(target_repo, del_hit_info['file_path'])
                print('@@', del_hit_info['func_name'], '@@')
                for item in del_hit_info['mid']:
                    print(item)
                print('=================================')
            else:
                print('* VULN DETECTED *')
                print('=================================')
                print(target_repo, del_hit_info['file_path'])
                print('@@', del_hit_info['func_name'], '@@')
                for item in del_hit_info['up']:
                    print(item)
                for item in del_hit_info['mid']:
                    print(item)
                for item in del_hit_info['down']:
                    print(item)
                print('=================================')

        print('* DONE *')
        return None


def run(p_patches):
    """
    :return:
    """
    for repo in target_repos:
        print('REPO:', repo)
        print('=================================')
        print()
        
        for patch in patches:
            print('SHA:', patch['sha'])
            print('FILE:', patch['file'])
            print('TYPE:', patch['type'])
            print('*********************************')
            main(target_repos[repo], patch)
            print()


if __name__ == '__main__':
    processed_patches = process_patches()
    run(processed_patches)
