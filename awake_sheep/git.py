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

    return proc.returncode, stdout.decode(), stderr.decode()


async def git_log_repo(repo_path: pathlib.Path, since=None):
    pretty = "###%H:%ae:%ct%n%B"
    if since:
        cmd = f'git log --pretty={pretty} --since="{since}" '
    else:
        cmd = f'git log --pretty={pretty}'

    ret, stdout, stderr = await shell(cmd, repo_path)
    if ret == 0:
        return get_commit_info(stdout)
    else:
        raise RuntimeError(cmd, stderr)


def get_commit_info(stdout_string):
    regex = r'###([a-z0-9]+):([^:]+):(\d+)\n(.*?)(?=###)'
    result = re.findall(regex, stdout_string, re.DOTALL)
    return result



