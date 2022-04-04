import os.path
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


def main():
    from awake_sheep.db import create_commit_info_table, load_code_info
    if sys.argv[1] == 'init':
        repo_path = sys.argv[2]
        create_commit_info_table()
        load_code_info(repo_path)


if __name__ == "__main__":
    main()
