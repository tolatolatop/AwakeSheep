import os.path
import pathlib
import sys
from hashlib import md5
import sqlite3

from git import Repo
from pydantic import BaseModel


class BaseCodeInfo(BaseModel):
    file_name: str
    code: str

    @property
    def knight_mark(self) -> str:
        mark = md5()
        mark.update(self.file_name.encode('utf-8'))
        mark.update(self.code.encode('utf-8'))
        return mark.hexdigest()

    def dict(self, *arg, **kwargs):
        orig = super(BaseCodeInfo, self).dict(*arg, **kwargs)
        for key in self.Config.export_properties:
            orig[key] = self.__getattribute__(key)
        return orig

    class Config:
        allow_mutation = False
        export_properties = ['knight_mark']


class CodeInfo(BaseCodeInfo):
    line_num: str
    local_repo_path: str
    commit_id: str

    @property
    def king_mark(self) -> str:
        mark = md5()
        mark.update(self.knight_mark.encode('utf-8'))
        mark.update(self.commit_id.encode('utf-8'))
        mark.update(self.line_num.encode('utf-8'))
        return mark.hexdigest()

    class Config:
        allow_mutation = False
        export_properties = ['king_mark', 'knight_mark']


class CommitInfo(BaseModel):
    commit_id: str
    is_rtos: bool
    summary: str


def get_all_git_repo(path):
    repo_list = []
    for repo_path in pathlib.Path(path).glob('**/.git'):
        repo_list.append(Repo(repo_path))
    return repo_list


def query_code_info(file_path, code_snippet):
    from awake_sheep.db import query_code_info_by_knight_mark
    file_name = os.path.basename(file_path)
    code_info = BaseCodeInfo(file_name=file_name, code=code_snippet)
    return query_code_info_by_knight_mark(code_info.knight_mark)


def local_repo_in_dir(path):
    from awake_sheep.db import load_code_info

    for repo_path in pathlib.Path(path).glob('**/.git'):
        load_code_info(str(repo_path.parent))


def main(args=None):
    if args is None:
        args = sys.argv.copy()

    from awake_sheep.db import create_commit_info_table, load_code_info, init_code_table
    from awake_sheep.db import query_commit_info

    if args[1] == 'init':
        init_code_table()
        create_commit_info_table()
        if args[2] == '--all':
            local_repo_in_dir(args[3])
        else:
            repo_path = args[2]
            load_code_info(repo_path)

    if args[1] == 'query':
        file_path = args[2]
        code_snippet = args[3]
        code_info_iter = query_code_info(file_path, code_snippet)
        for code_info in code_info_iter:
            print(code_info)
            repo = Repo(code_info.local_repo_path)
            commit_info = query_commit_info(repo, code_info.commit_id)
            print(commit_info)


if __name__ == "__main__":
    main()
