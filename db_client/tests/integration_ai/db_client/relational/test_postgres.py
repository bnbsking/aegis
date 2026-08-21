from datetime import datetime

from db_client.relational.base import Condition, ColumnConfig, ConditionCollection
from db_client.relational.postgres import DBAccessor, SQLCommand, TagConfig, get_table_size


class TestDBAccessor:
    TABLE = "test_db_accessor_tbl"

    def __init__(self):
        self.dba = DBAccessor(host="172.17.0.1")

    def test_run(self):
        result = self.dba.run("SELECT 1;")
        assert result == [(1,)]

    def setup(self):
        self.dba.run(SQLCommand.drop_table(self.TABLE))
        col_cfgs = [
            ColumnConfig(column="id", sql_type="SERIAL", additional="PRIMARY KEY"),
            ColumnConfig(column="name", sql_type="TEXT"),
            ColumnConfig(column="meta", sql_type="JSONB"),
            ColumnConfig(column="tags", sql_type="TEXT[]"),
            ColumnConfig(column="created_at", sql_type="TIMESTAMP"),
        ]
        self.dba.run(SQLCommand.build_table(self.TABLE, col_cfgs))

    def teardown(self):
        self.dba.run(SQLCommand.drop_table(self.TABLE))
        self.dba.close()

    def test_insert_select_update_delete_roundtrip(self):
        sql, params = SQLCommand.insert(
            self.TABLE,
            {"name": "alice", "meta": {"role": "admin"}, "tags": ["x", "y"]},
            returning="RETURNING id",
        )
        row_id = self.dba.run(sql, params)[0][0]

        conditions = ConditionCollection(and_list=[Condition(key="id", match_type="exact", content=row_id)], or_list=[])
        sql, params = SQLCommand.select(self.TABLE, conditions=conditions)
        row = self.dba.run(sql, params)[0]
        assert row[1] == "alice"
        assert row[2] == {"role": "admin"}
        assert row[3] == ["x", "y"]

        sql, params = SQLCommand.update(self.TABLE, {"name": "bob"}, conditions=conditions)
        self.dba.run(sql, params)
        sql, params = SQLCommand.select(self.TABLE, cols=["name"], conditions=conditions)
        assert self.dba.run(sql, params)[0][0] == "bob"

        sql, params = SQLCommand.delete(self.TABLE, conditions)
        self.dba.run(sql, params)
        sql, params = SQLCommand.select(self.TABLE, conditions=conditions)
        assert self.dba.run(sql, params) == []

    def test_insert_raw_sql_literal_and_empty_jsonb_list(self):
        sql, params = SQLCommand.insert(
            self.TABLE,
            {"name": "empty_meta", "meta": [], "created_at": "NOW()"},
            returning="RETURNING id",
        )
        row_id = self.dba.run(sql, params)[0][0]
        conditions = ConditionCollection(and_list=[Condition(key="id", match_type="exact", content=row_id)], or_list=[])
        sql, params = SQLCommand.select(self.TABLE, cols=["meta", "created_at"], conditions=conditions)
        meta, created_at = self.dba.run(sql, params)[0]
        assert meta == []
        # NOW() must be executed server-side as a function call, not stored as the literal string "NOW()"
        assert isinstance(created_at, datetime)

    def test_select_gin_matches_via_gin_index(self):
        self.dba.run(SQLCommand.build_gin_index("idx_test_db_accessor_tags", self.TABLE, "tags"))
        sql, params = SQLCommand.insert(self.TABLE, {"name": "tagged", "tags": ["red", "blue"]})
        self.dba.run(sql, params)

        and_cfg = TagConfig(key="tags", tags=["red"], match_logic="and")
        sql, params = SQLCommand.select_gin(self.TABLE, and_cfg, cols=["name"])
        assert ("tagged",) in self.dba.run(sql, params)

        missing_cfg = TagConfig(key="tags", tags=["green"], match_logic="and")
        sql, params = SQLCommand.select_gin(self.TABLE, missing_cfg, cols=["name"])
        assert self.dba.run(sql, params) == []

    def test_get_table_size(self):
        size = get_table_size(self.dba, self.TABLE)
        assert isinstance(size, int)


if __name__ == "__main__":
    obj = TestDBAccessor()
    obj.test_run()
    obj.setup()
    try:
        obj.test_insert_select_update_delete_roundtrip()
        obj.test_insert_raw_sql_literal_and_empty_jsonb_list()
        obj.test_select_gin_matches_via_gin_index()
        obj.test_get_table_size()
    finally:
        obj.teardown()

    print("all tests passed")
