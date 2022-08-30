#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/31 4:17
# @Author  : tolatolatop
# @File    : git.py
import asyncio
import pathlib


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
    pretty = "%H%ae%ct%s"
    if since:
        cmd = f'git log --since="{since}" --pretty={pretty}'
    else:
        cmd = f'git log'
