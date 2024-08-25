import time

import requests
import git
from github import Github
from github.GithubException import UnknownObjectException

from src.fetcher import fetch_commit_info
from src.configs import REPO_GITHUB, GITHUB_TOKEN
from src.util import get_commit_tags, get_commit_pr, calc_code_sim


def get_blame_info(repo_dir, file_path, code_lines, key_line):
    """

    :param repo_dir:
    :param file_path:
    :param code_lines:
    :param key_line:
    :return:
    """
    result = dict()

    repo = git.Repo(repo_dir)
    try:
        raw_output = repo.git.blame(file_path)
        # print(raw_output)
    except git.exc.GitCommandError:
        # print('* NO RESULT FOUND *')
        return result
    else:
        raw_output = raw_output.split('\n')

        key_sha = None
        most_sim = None
        for code_line in code_lines:
            raw_output_line = raw_output[code_line[0] - 1]
            output_sha = raw_output_line.split(' ', 1)[0]
            line_sim = calc_code_sim([key_line], [code_line])
            if not key_sha:
                key_sha = output_sha
                most_sim = line_sim
            else:
                if line_sim >= most_sim:
                    key_sha = output_sha
                    most_sim = line_sim

        _, _, commit_info = fetch_commit_info(repo_dir, key_sha, general_only=True)

        result = commit_info

    return result


def get_merge_info(repo_dir, sha):
    """

    :param repo_dir:
    :param sha:
    :return:
    """
    result = None

    repo_name = REPO_GITHUB[repo_dir]

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)

    commit_url = repo.get_commit(sha).html_url
    pr_number = get_commit_pr(commit_url)

    if pr_number:
        result = repo.get_pull(pr_number)

    return result


def get_release_info(repo_dir, sha):
    """

    :param repo_dir:
    :param sha:
    :return:
    """
    result = None

    repo_name = REPO_GITHUB[repo_dir]

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)

    commit_url = repo.get_commit(sha).html_url
    tag_list = get_commit_tags(commit_url)

    early_release = None
    for tag in tag_list:
        try:
            release_info = repo.get_release(tag)
        except UnknownObjectException:
            continue
        except requests.exceptions.ReadTimeout:
            time.sleep(10)
            release_info = repo.get_release(tag)
        else:
            if not early_release:
                early_release = release_info
            else:
                if release_info.published_at <= early_release.published_at:
                    early_release = release_info

    result = early_release
    return result
