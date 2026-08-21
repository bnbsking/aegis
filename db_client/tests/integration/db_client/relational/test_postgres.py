from db_client.relational.base import ColumnConfig, ConditionCollection, Condition
from db_client.relational.postgres import (
    DBAccessor,
    SQLCommand,
    TagConfig
)


class TestSQLCommand:
    def __init__(self):
        self.dbaccessor = DBAccessor()
        self.dbaccessor.run("DROP TABLE IF EXISTS test_table;")

    def _test_build_table(self):
        cmd = SQLCommand.build_table(
            "test_table",
            [
                ColumnConfig("resume_id", "UUID", "PRIMARY KEY"),
                ColumnConfig("name", "TEXT", ""),
                ColumnConfig("age", "INT", "")
            ]
        )
        self.dbaccessor.run(cmd)
        assert self.dbaccessor.run("SELECT * FROM test_table") == []

    def _test_insert(self):
        cmd, params = SQLCommand.insert(
           "test_table",
            {
                "resume_id": "gen_random_uuid()",
                "name": "歐巴馬",
                "age": 40
            }
        )
        self.dbaccessor.run(cmd, params)
        _, name, age = self.dbaccessor.run("SELECT * FROM test_table", [])[0]
        assert name == '歐巴馬' and age == 40

    def _test_update(self):
        cmd, params = SQLCommand.update(
            "test_table",
            {
                "name": "川普",
            },
            "WHERE name = '歐巴馬'"
        )
        self.dbaccessor.run(cmd, params)
        _, name, age = self.dbaccessor.run("SELECT * FROM test_table", [])[0]
        assert name == '川普' and age == 40

    def _test_select(self):
        cond_collect = ConditionCollection(
            and_list = [
                Condition(key="name", match_type="exact", content="川普"),
                Condition(key="age", match_type="range", lb=30, ub=50)
            ],
            or_list = [],
            concat_op = "AND"
        )
        cmd, params = SQLCommand.select("test_table", conditions=cond_collect)
        _, name, age = self.dbaccessor.run(cmd, params)[0]
        assert name == '川普' and age == 40

    def _test_delete(self):
        cond_collect = ConditionCollection(
            and_list = [
                Condition(key="name", match_type="exact", content="川普")
            ],
            or_list = [],
            concat_op = "AND"
        )
        cmd, params = SQLCommand.delete("test_table", conditions=cond_collect)
        self.dbaccessor.run(cmd, params)
        self.dbaccessor.run(cmd, params)
        assert self.dbaccessor.run("SELECT * FROM test_table", []) == []

    def test_run_all(self):
        self._test_build_table()
        self._test_insert()
        self._test_update()
        self._test_select()
        self._test_delete()
        self.dbaccessor.run("DROP TABLE test_table;")


class TestSQLCommandGIN:
    def __init__(self):
        self.dbaccessor = DBAccessor()
        self.dbaccessor.run("DROP TABLE IF EXISTS test_table;")

        # create table
        cmd = SQLCommand.build_table(
            "test_table",
            [
                ColumnConfig("name", "TEXT", ""),
                ColumnConfig("tags", "TEXT[]", "")
            ]
        )
        self.dbaccessor.run(cmd)
        
        # insert data
        cmd, params = SQLCommand.insert(
           "test_table",
            {
                "name": "歐巴馬",
                "tags": ["Python", "C++", "Java"]
            }
        )
        self.dbaccessor.run(cmd, params)
        cmd, params = SQLCommand.insert(
           "test_table",
            {
                "name": "川普",
                "tags": ["Python", "C++", "JS"]
            }
        )
        self.dbaccessor.run(cmd, params)
        cmd, params = SQLCommand.insert(
           "test_table",
            {
                "name": "拜登",
                "tags": ["Python", "Java", "JS"]
            }
        )
        self.dbaccessor.run(cmd, params)

        # create gin index
        cmd = SQLCommand.build_gin_index(
            "test_table_gin",
            "test_table",
            "tags"
        )
        self.dbaccessor.run(cmd)

    def _test_select_gin_and(self):
        tag_cfg = TagConfig(key="tags", tags=["C++", "Python"], match_logic="and")
        cmd, params = SQLCommand.select_gin("test_table", tag_cfg=tag_cfg)
        out = self.dbaccessor.run(cmd, params)
        assert out == [
            ('歐巴馬', ['Python', 'C++', 'Java']),
            ('川普', ['Python', 'C++', 'JS'])
        ]

    def _test_select_gin_or(self):
        tag_cfg = TagConfig(key="tags", tags=["C++", "Python"], match_logic="or")
        cmd, params = SQLCommand.select_gin("test_table", tag_cfg=tag_cfg)
        out = self.dbaccessor.run(cmd, params)
        assert out == [
            ('歐巴馬', ['Python', 'C++', 'Java']),
            ('川普', ['Python', 'C++', 'JS']),
            ('拜登', ["Python", "Java", "JS"])
        ]

    def test_run_all(self):
        self._test_select_gin_and()
        self._test_select_gin_or()
        self.dbaccessor.run("DROP TABLE test_table;")


if __name__ == "__main__":
    TestSQLCommand().test_run_all()
    TestSQLCommandGIN().test_run_all()
