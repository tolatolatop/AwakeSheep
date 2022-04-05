import os.path
import pathlib
import sqlite3

from git import Repo
from pydantic import ValidationError

from .core import CodeInfo, CommitInfo

__db = None


def get_db():
    if __db is None:
        return sqlite3.connect('db.sqlite3')
    return __db


def create_code_table():
    db = get_db()
    db.execute('''DROP TABLE IF EXISTS SRC_CODE;''')
    db.commit()
    db.execute('''
CREATE TABLE SRC_CODE (
    FILE_NAME    TEXT  NOT NULL,
    CODE         TEXT  NOT NULL,
    LINE_NUM     CHAR(8) NOT NULL,
    LOCAL_REPO_PATH CHAR(255) NOT NULL, 
    COMMIT_ID    CHAR(40) NOT NULL,
    KING_MARK    CHAR(40) PRIMARY KEY NOT NULL,
    KNIGHT_MARK  CHAR(40) NOT NULL
);''')
    db.commit()
    db.execute('''CREATE INDEX KNIGHT_MARK_INDEX ON SRC_CODE(KNIGHT_MARK)''')
    db.commit()


def create_commit_info_table():
    db = get_db()
    db.execute('''DROP TABLE IF EXISTS COMMIT_INFO;''')
    db.commit()
    db.execute('''
CREATE TABLE COMMIT_INFO (
    COMMIT_ID    CHAR(40) PRIMARY KEY NOT NULL,
    IS_RTOS INT NOT NULL,
    SUMMARY TEXT NOT NULL
);''')
    db.commit()


def query_code_info_by_knight_mark(knight_mark):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM SRC_CODE INDEXED BY KNIGHT_MARK_INDEX WHERE KNIGHT_MARK == ?', (knight_mark,))
    for data in cur.fetchall():
        yield CodeInfo(
            file_name=data[0],
            code=data[1],
            line_num=data[2],
            local_repo_path=data[3],
            commit_id=data[4],
            king_mark=data[5],
            knight_mark=data[6],
        )


def query_commit_info(repo: Repo, commit_id) -> CommitInfo:
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM COMMIT_INFO WHERE COMMIT_ID == ?', (commit_id,))
    res = tuple(cur.fetchall())
    cur.close()
    count = len(res)
    if count == 0:
        cur = db.cursor()
        commit_info = create_commit_info(repo, commit_id)
        cur.execute('INSERT INTO COMMIT_INFO VALUES (?, ?, ?);', tuple(commit_info.dict().values()))
        db.commit()
        cur.close()
        return commit_info
    elif count == 1:
        return res[0]
    else:
        raise ValueError('more then one commit')


def create_commit_info(repo: Repo, commit_id: str) -> CommitInfo:
    commit = repo.commit(commit_id)
    commit_info = CommitInfo(
        commit_id=commit_id,
        is_rtos='uawei' in commit.message,
        summary=commit.message
    )
    return commit_info


def load_code_info(repo_path: str):
    repo = Repo(path=repo_path)
    repo.iter_trees()
    db = get_db()
    create_code_table()
    cur = db.cursor()
    for file_path, file_name in list_all_file_in_traced(repo):
        code_info_list = get_code_info_from_repo(repo, file_path, file_name)
        code_info_iter = (tuple(code_info.dict().values()) for code_info in code_info_list)
        cur.executemany('INSERT INTO SRC_CODE VALUES (?, ?, ?, ?, ?, ?, ?);', code_info_iter)
    db.commit()
    cur.close()


def list_all_file_in_traced(repo: Repo):
    for entry in repo.commit().tree.traverse():
        if os.path.isfile(entry.abspath):
            yield entry.path, entry.name


def get_code_info_from_repo(repo, file_path, file_name):
    start = 1
    for commit_id, line_code_list in repo.blame(file=file_path, rev='HEAD'):
        for line_num, line_code in enumerate(line_code_list, start=start):
            try:
                code_info = CodeInfo(
                    file_name=file_name,
                    code=line_code,
                    line_num=line_num,
                    local_repo_path=repo.working_dir,
                    commit_id=str(commit_id)
                )
                yield code_info
            except ValidationError as e:
                break
        else:
            start += len(line_code_list)
