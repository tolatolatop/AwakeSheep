#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 4:17
# @Author  : tolatolatop
# @File    : git.py
import asyncio
import pathlib
import re


async def shell(cmd, cwd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )

    stdout, stderr = await proc.communicate()

    return proc.returncode, stdout, stderr


async def git_log_repo(repo_path: pathlib.Path, since=None):
    cmd = get_git_log_cmd(None, since)

    ret, stdout, stderr = await shell(cmd, repo_path)
    if ret == 0:
        return get_commit_info(stdout)
    else:
        raise RuntimeError(cmd, stderr)


async def get_log_all_file(repo_path: pathlib.Path, since=None):
    all_file_info = {}
    for file in repo_path.glob('**/*'):
        commit_info = await git_log_file(file, repo_path, since)
        if len(commit_info) > 0:
            all_file_info[file] = commit_info
    return all_file_info


async def git_log_file(file_path: pathlib.Path, repo_path: pathlib.Path, since=None):
    cmd = get_git_log_cmd(file_path, since)

    ret, stdout, stderr = await shell(cmd, repo_path)
    if ret == 0:
        return get_commit_info(stdout)
    else:
        raise RuntimeError(cmd, stderr)


def get_commit_info(stdout_string):
    regex = re.compile(rb'###([a-z0-9]+):([^:]+):(\d+)\n(.*?)(?=###|$)', re.DOTALL)
    result = regex.findall(stdout_string)
    return result


def get_git_log_cmd(file_path: pathlib.Path, since=None):
    pretty = "###%H:%ae:%ct%n%B"
    if file_path is None:
        file_path_args = ''
    else:
        file_path_args = file_path

    if since:
        if since.isdigit():
            since_args = f'-{since}'
        else:
            since_args = f"--since={since}"
    else:
        since_args = ""
    cmd = f'git log {since_args} --pretty={pretty} {file_path_args}'
    return cmd


if __name__ == "__main__":
    f = get_log_all_file(pathlib.Path('.'))
    res = asyncio.run(f)
    print(res)
