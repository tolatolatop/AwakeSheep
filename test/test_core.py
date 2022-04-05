import unittest

from git import Repo
from awake_sheep.core import BaseCodeInfo, main
from awake_sheep.db import load_code_info, query_code_info_by_knight_mark, query_commit_info, create_commit_info_table
from awake_sheep.db import init_code_table


class TestCoreCase(unittest.TestCase):

    def setUp(self) -> None:
        init_code_table()
        create_commit_info_table()

    def test_load_code_info(self):
        repo_path = r'E:\python_project\f_page'

        repo = Repo(path=repo_path)
        load_code_info(repo_path)

        base_code_info = BaseCodeInfo(file_name='index.html', code='</body>')
        for code_info in query_code_info_by_knight_mark(base_code_info.knight_mark):
            self.assertEqual(base_code_info.knight_mark, code_info.knight_mark)
            self.assertEqual('b5c6047c1d3e59823a8a3353902f929738ec8216', code_info.commit_id)

        commit_info = query_commit_info(repo, 'b5c6047c1d3e59823a8a3353902f929738ec8216')
        self.assertEqual('测试工程\n', commit_info.summary)

    def test_core(self):
        cmd = ['', 'init', '--all', r'E:\python_project']
        main(cmd)
        cmd = ['', 'query', 'index.html', '</body>']
        main(cmd)


if __name__ == '__main__':
    unittest.main()
