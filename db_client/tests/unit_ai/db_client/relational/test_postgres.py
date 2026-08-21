import json

from db_client.relational.base import Condition, ColumnConfig, ConditionCollection
from db_client.relational.postgres import SQLCommand, TagConfig


TABLE_NAME = "test_sql_command_tbl"


def test_build_table():
    col_cfgs = [
        ColumnConfig(column="id", sql_type="SERIAL", additional="PRIMARY KEY"),
        ColumnConfig(column="name", sql_type="TEXT"),
    ]
    sql = SQLCommand.build_table(TABLE_NAME, col_cfgs)
    assert f"CREATE TABLE IF NOT EXISTS {TABLE_NAME}" in sql
    assert "id SERIAL PRIMARY KEY" in sql
    assert "name TEXT" in sql
    # sql: CREATE TABLE IF NOT EXISTS test_sql_command_tbl (id SERIAL PRIMARY KEY, name TEXT);


def test_build_view():
    sql = SQLCommand.build_view("v_test", TABLE_NAME, ["id", "name"])
    assert "CREATE OR REPLACE VIEW v_test AS" in sql
    assert "SELECT id, name" in sql
    assert f"FROM {TABLE_NAME}" in sql
    # sql: CREATE OR REPLACE VIEW v_test AS SELECT id, name FROM test_sql_command_tbl;


def test_build_gin_index():
    sql = SQLCommand.build_gin_index("idx_test", TABLE_NAME, "tags")
    assert "CREATE INDEX IF NOT EXISTS idx_test" in sql
    assert f"ON {TABLE_NAME}" in sql
    assert "USING GIN (tags)" in sql
    # sql: CREATE INDEX IF NOT EXISTS idx_test ON test_sql_command_tbl USING GIN (tags);


def test_drop_table():
    assert SQLCommand.drop_table(TABLE_NAME) == f"DROP TABLE IF EXISTS {TABLE_NAME} CASCADE"
    # sql: DROP TABLE IF EXISTS test_sql_command_tbl CASCADE


def test_show_databases():
    assert SQLCommand.show_databases() == "SELECT datname FROM pg_database;"
    # sql: SELECT datname FROM pg_database;


def test_show_tables():
    sql = SQLCommand.show_tables()
    assert "information_schema.tables" in sql
    assert "table_schema = 'public'" in sql
    # sql: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';


def test_select_no_cols_no_conditions():
    sql, params = SQLCommand.select(TABLE_NAME)
    assert sql.strip() == f"SELECT * FROM {TABLE_NAME}"
    assert params == []
    # sql: SELECT * FROM test_sql_command_tbl


def test_select_with_cols_conditions_and_limit():
    conditions = ConditionCollection(and_list=[Condition(key="age", match_type="range", lb=18, ub=65)], or_list=[])
    sql, params = SQLCommand.select(TABLE_NAME, cols=["id", "name"], conditions=conditions, limit=10)
    assert f"SELECT id,name FROM {TABLE_NAME}" in sql
    assert "WHERE (age <= ? AND age >= ?)" in sql
    assert "LIMIT 10" in sql
    assert params == [65, 18]
    # sql: SELECT id,name FROM test_sql_command_tbl WHERE (age <= 65 AND age >= 18) LIMIT 10


def test_insert_skips_none_and_casts_dict_to_jsonb():
    sql, params = SQLCommand.insert(TABLE_NAME, {"name": "alice", "age": None, "meta": {"a": 1}})
    assert "age" not in sql
    assert "?::jsonb" in sql
    assert params == ["alice", json.dumps({"a": 1})]
    # sql: INSERT INTO test_sql_command_tbl (name, meta) VALUES ('alice', '{"a": 1}'::jsonb)


def test_insert_allows_whitelisted_raw_sql_literal():
    sql, params = SQLCommand.insert(TABLE_NAME, {"created_at": "NOW()"})
    assert "VALUES (NOW())" in sql
    assert params == []
    # sql: INSERT INTO test_sql_command_tbl (created_at) VALUES (NOW())


def test_insert_does_not_treat_arbitrary_paren_suffix_as_raw_sql():
    # regression test: a plain data value that happens to end with "()" must still be bound
    # as a parameter, not spliced into the SQL string
    sql, params = SQLCommand.insert(TABLE_NAME, {"name": "foo()"})
    assert "VALUES (?)" in sql
    assert params == ["foo()"]
    # sql: INSERT INTO test_sql_command_tbl (name) VALUES ('foo()')  -- bound as a param, not raw SQL


def test_insert_empty_list_is_cast_to_jsonb():
    # regression test: an empty list must still get an ::jsonb cast, not fall through
    # to an untyped placeholder that Postgres can't resolve
    sql, params = SQLCommand.insert(TABLE_NAME, {"tags": []})
    assert "?::jsonb" in sql
    assert params == [json.dumps([])]
    # sql: INSERT INTO test_sql_command_tbl (tags) VALUES ('[]'::jsonb)


def test_insert_list_of_dicts_is_cast_to_jsonb():
    sql, params = SQLCommand.insert(TABLE_NAME, {"items": [{"a": 1}, {"b": 2}]})
    assert "?::jsonb" in sql
    assert params == [json.dumps([{"a": 1}, {"b": 2}])]
    # sql: INSERT INTO test_sql_command_tbl (items) VALUES ('[{"a": 1}, {"b": 2}]'::jsonb)


def test_insert_plain_list_is_not_cast_to_jsonb():
    sql, params = SQLCommand.insert(TABLE_NAME, {"tags": ["x", "y"]})
    assert "?::jsonb" not in sql
    assert params == [["x", "y"]]
    # sql: INSERT INTO test_sql_command_tbl (tags) VALUES (ARRAY['x','y'])  -- psycopg2 adapts the
    # Python list to a Postgres array literal since there is no ::jsonb cast here


def test_update_sets_null_for_none_and_binds_other_values():
    sql, params = SQLCommand.update(TABLE_NAME, {"age": None, "name": "bob"})
    assert "age = NULL" in sql
    assert "name = ?" in sql
    assert params == ["bob"]
    # sql: UPDATE test_sql_command_tbl SET age = NULL, name = 'bob'


def test_delete_builds_where_clause():
    conditions = ConditionCollection(and_list=[Condition(key="id", match_type="exact", content=1)], or_list=[])
    sql, params = SQLCommand.delete(TABLE_NAME, conditions)
    assert sql.strip() == f"DELETE FROM {TABLE_NAME} WHERE id = ?"
    assert params == [1]
    # sql: DELETE FROM test_sql_command_tbl WHERE id = 1


def test_select_gin_and_logic_uses_containment_operator():
    tag_cfg = TagConfig(key="tags", tags=["a", "b"], match_logic="and")
    sql, params = SQLCommand.select_gin(TABLE_NAME, tag_cfg)
    assert "WHERE tags @> ?" in sql
    assert params == [["a", "b"]]
    # sql: SELECT * FROM test_sql_command_tbl WHERE tags @> ARRAY['a','b']


def test_select_gin_or_logic_uses_overlap_operator():
    tag_cfg = TagConfig(key="tags", tags=["a", "b"], match_logic="or")
    sql, _ = SQLCommand.select_gin(TABLE_NAME, tag_cfg)
    assert "WHERE tags && ?" in sql
    # sql: SELECT * FROM test_sql_command_tbl WHERE tags && ARRAY['a','b']


def test_select_gin_requires_tag_cfg():
    # regression test: tag_cfg used to default to None and crash inside the method with an
    # unhelpful AttributeError; it must now be a required argument
    try:
        SQLCommand.select_gin(TABLE_NAME)  # type: ignore[call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("select_gin() should require tag_cfg")
    # sql: (none — raises TypeError for a missing tag_cfg before any SQL is built)


def test_add_column():
    col_cfg = ColumnConfig(column="score", sql_type="INT", additional="DEFAULT 0")
    assert SQLCommand.add_column(TABLE_NAME, col_cfg) == (
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS score INT DEFAULT 0"
    )
    # sql: ALTER TABLE test_sql_command_tbl ADD COLUMN IF NOT EXISTS score INT DEFAULT 0


def test_drop_column():
    assert SQLCommand.drop_column(TABLE_NAME, "score") == (
        f"ALTER TABLE {TABLE_NAME} DROP COLUMN IF EXISTS score CASCADE"
    )
    # sql: ALTER TABLE test_sql_command_tbl DROP COLUMN IF EXISTS score CASCADE


def test_drop_all_data_in_a_table():
    assert SQLCommand.drop_all_data_in_a_table(TABLE_NAME) == f"TRUNCATE {TABLE_NAME} CASCADE"
    # sql: TRUNCATE test_sql_command_tbl CASCADE


UNIT_TESTS = [
    test_build_table,
    test_build_view,
    test_build_gin_index,
    test_drop_table,
    test_show_databases,
    test_show_tables,
    test_select_no_cols_no_conditions,
    test_select_with_cols_conditions_and_limit,
    test_insert_skips_none_and_casts_dict_to_jsonb,
    test_insert_allows_whitelisted_raw_sql_literal,
    test_insert_does_not_treat_arbitrary_paren_suffix_as_raw_sql,
    test_insert_empty_list_is_cast_to_jsonb,
    test_insert_list_of_dicts_is_cast_to_jsonb,
    test_insert_plain_list_is_not_cast_to_jsonb,
    test_update_sets_null_for_none_and_binds_other_values,
    test_delete_builds_where_clause,
    test_select_gin_and_logic_uses_containment_operator,
    test_select_gin_or_logic_uses_overlap_operator,
    test_select_gin_requires_tag_cfg,
    test_add_column,
    test_drop_column,
    test_drop_all_data_in_a_table,
]


if __name__ == "__main__":
    for test in UNIT_TESTS:
        test()

    print("all tests passed")
