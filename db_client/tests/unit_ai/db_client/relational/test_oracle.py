import json

from db_client.relational.base import Condition, ColumnConfig, ConditionCollection
from db_client.relational.oracle import DBAccessor, SQLCommand


TABLE_NAME = "test_sql_command_tbl"


def test_build_table():
    col_cfgs = [
        ColumnConfig(column="id", sql_type="NUMBER", additional="PRIMARY KEY"),
        ColumnConfig(column="name", sql_type="VARCHAR2(100)"),
    ]
    sql = SQLCommand.build_table(TABLE_NAME, col_cfgs)
    assert f"CREATE TABLE {TABLE_NAME}" in sql
    assert "id NUMBER PRIMARY KEY" in sql
    assert "name VARCHAR2(100)" in sql
    assert "SQLCODE != -955" in sql
    # sql: BEGIN EXECUTE IMMEDIATE 'CREATE TABLE test_sql_command_tbl (id NUMBER PRIMARY KEY,
    # name VARCHAR2(100))'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
    # (ORA-00955 = name already used by an existing object, i.e. "IF NOT EXISTS")


def test_build_table_escapes_single_quotes_in_column_definition():
    # regression test: EXECUTE IMMEDIATE wraps the DDL in a single-quoted string, so an
    # embedded quote (e.g. a DEFAULT literal) must be escaped or it breaks out of the string
    # - PL/SQL syntax error at best, a dynamic-SQL injection surface at worst
    col_cfgs = [ColumnConfig(column="status", sql_type="VARCHAR2(20)", additional="DEFAULT 'active'")]
    sql = SQLCommand.build_table(TABLE_NAME, col_cfgs)
    assert "DEFAULT ''active''" in sql
    assert "DEFAULT 'active'" not in sql
    # sql: BEGIN EXECUTE IMMEDIATE 'CREATE TABLE test_sql_command_tbl (status VARCHAR2(20)
    # DEFAULT ''active'')'; EXCEPTION ... END;


def test_build_view():
    sql = SQLCommand.build_view("v_test", TABLE_NAME, ["id", "name"])
    assert "CREATE OR REPLACE VIEW v_test AS" in sql
    assert "SELECT id, name" in sql
    assert f"FROM {TABLE_NAME}" in sql
    # sql: CREATE OR REPLACE VIEW v_test AS SELECT id, name FROM test_sql_command_tbl


def test_drop_table():
    sql = SQLCommand.drop_table(TABLE_NAME)
    assert f"DROP TABLE {TABLE_NAME}" in sql
    assert "SQLCODE != -942" in sql
    # sql: BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_sql_command_tbl'; EXCEPTION WHEN OTHERS THEN
    # IF SQLCODE != -942 THEN RAISE; END IF; END;
    # (ORA-00942 = table or view does not exist, i.e. "IF EXISTS")


def test_show_tables():
    assert SQLCommand.show_tables() == "SELECT table_name FROM user_tables"
    # sql: SELECT table_name FROM user_tables


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
    assert "FETCH FIRST 10 ROWS ONLY" in sql
    assert params == [65, 18]
    # sql: SELECT id,name FROM test_sql_command_tbl WHERE (age <= 65 AND age >= 18) FETCH FIRST 10 ROWS ONLY


def test_insert_skips_none_and_serializes_dict_as_json_text():
    sql, params = SQLCommand.insert(TABLE_NAME, {"name": "alice", "age": None, "meta": {"a": 1}})
    assert "age" not in sql
    assert sql == f"INSERT INTO {TABLE_NAME} (name, meta) VALUES (?, ?)"
    assert params == ["alice", json.dumps({"a": 1})]
    # sql: INSERT INTO test_sql_command_tbl (name, meta) VALUES ('alice', '{"a": 1}')
    # (no ::jsonb-style cast like Postgres - the JSON/CLOB column just takes the text as-is)


def test_insert_allows_whitelisted_raw_sql_literal():
    sql, params = SQLCommand.insert(TABLE_NAME, {"created_at": "SYSDATE"})
    assert sql == f"INSERT INTO {TABLE_NAME} (created_at) VALUES (SYSDATE)"
    assert params == []
    # sql: INSERT INTO test_sql_command_tbl (created_at) VALUES (SYSDATE)


def test_insert_does_not_treat_arbitrary_paren_suffix_as_raw_sql():
    # a value that merely ends with "()" (e.g. SYS_GUID()-shaped but not actually whitelisted)
    # must still be bound as a parameter, not spliced into the SQL string
    sql, params = SQLCommand.insert(TABLE_NAME, {"name": "foo()"})
    assert sql == f"INSERT INTO {TABLE_NAME} (name) VALUES (?)"
    assert params == ["foo()"]
    # sql: INSERT INTO test_sql_command_tbl (name) VALUES ('foo()')  -- bound as a param, not raw SQL


def test_insert_empty_list_is_serialized_as_json_text():
    sql, params = SQLCommand.insert(TABLE_NAME, {"tags": []})
    assert sql == f"INSERT INTO {TABLE_NAME} (tags) VALUES (?)"
    assert params == [json.dumps([])]
    # sql: INSERT INTO test_sql_command_tbl (tags) VALUES ('[]')


def test_insert_list_of_dicts_is_serialized_as_json_text():
    sql, params = SQLCommand.insert(TABLE_NAME, {"items": [{"a": 1}, {"b": 2}]})
    assert sql == f"INSERT INTO {TABLE_NAME} (items) VALUES (?)"
    assert params == [json.dumps([{"a": 1}, {"b": 2}])]
    # sql: INSERT INTO test_sql_command_tbl (items) VALUES ('[{"a": 1}, {"b": 2}]')


def test_insert_rejects_plain_scalar_list():
    # regression guard: unlike Postgres (psycopg2 auto-adapts a Python list to an array
    # literal), oracledb has no scalar-bind adapter for a plain list - silently binding one
    # would fail at execution time with an opaque driver error, so this must fail fast instead
    try:
        SQLCommand.insert(TABLE_NAME, {"tags": ["x", "y"]})
    except ValueError:
        pass
    else:
        raise AssertionError("insert() should reject a plain scalar list on Oracle")


def test_insert_has_no_returning_param():
    # regression guard: Postgres's insert() takes a `returning` kwarg, but Oracle's RETURNING
    # needs an OUT bind variable through the driver API and can't be expressed as (sql, params),
    # so it must not be offered here
    try:
        SQLCommand.insert(TABLE_NAME, {"name": "alice"}, returning="RETURNING id")  # type: ignore[call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("insert() should not accept a `returning` kwarg on Oracle")


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


def test_add_column():
    col_cfg = ColumnConfig(column="score", sql_type="NUMBER", additional="DEFAULT 0")
    sql = SQLCommand.add_column(TABLE_NAME, col_cfg)
    assert f"ALTER TABLE {TABLE_NAME} ADD (score NUMBER DEFAULT 0)" in sql
    assert "SQLCODE != -1430" in sql
    # sql: BEGIN EXECUTE IMMEDIATE 'ALTER TABLE test_sql_command_tbl ADD (score NUMBER DEFAULT 0)';
    # EXCEPTION WHEN OTHERS THEN IF SQLCODE != -1430 THEN RAISE; END IF; END;
    # (ORA-01430 = column being added already exists, i.e. "IF NOT EXISTS")


def test_add_column_escapes_single_quotes_in_additional():
    col_cfg = ColumnConfig(column="status", sql_type="VARCHAR2(20)", additional="DEFAULT 'active'")
    sql = SQLCommand.add_column(TABLE_NAME, col_cfg)
    assert "DEFAULT ''active''" in sql
    assert "DEFAULT 'active'" not in sql
    # sql: BEGIN EXECUTE IMMEDIATE 'ALTER TABLE test_sql_command_tbl ADD (status VARCHAR2(20)
    # DEFAULT ''active'')'; EXCEPTION ... END;


def test_drop_column():
    assert SQLCommand.drop_column(TABLE_NAME, "score") == f"ALTER TABLE {TABLE_NAME} DROP COLUMN score"
    # sql: ALTER TABLE test_sql_command_tbl DROP COLUMN score
    # (not idempotent - Oracle has no DROP COLUMN IF EXISTS, and the error for a missing column,
    # ORA-00904 "invalid identifier", is too generic to safely swallow)


def test_drop_all_data_in_a_table():
    assert SQLCommand.drop_all_data_in_a_table(TABLE_NAME) == f"TRUNCATE TABLE {TABLE_NAME}"
    # sql: TRUNCATE TABLE test_sql_command_tbl


def test_apply_paramstyle_uses_positional_binds():
    # oracledb needs :1, :2, ... rather than psycopg2's %s
    db_accessor = object.__new__(DBAccessor)  # bypass __init__ - no real DB connection needed
    sql = db_accessor._apply_paramstyle("SELECT * FROM t WHERE id = ? AND name = ? AND x = ?")
    assert sql == "SELECT * FROM t WHERE id = :1 AND name = :2 AND x = :3"
    # sql: SELECT * FROM t WHERE id = :1 AND name = :2 AND x = :3


UNIT_TESTS = [
    test_build_table,
    test_build_table_escapes_single_quotes_in_column_definition,
    test_build_view,
    test_drop_table,
    test_show_tables,
    test_select_no_cols_no_conditions,
    test_select_with_cols_conditions_and_limit,
    test_insert_skips_none_and_serializes_dict_as_json_text,
    test_insert_allows_whitelisted_raw_sql_literal,
    test_insert_does_not_treat_arbitrary_paren_suffix_as_raw_sql,
    test_insert_empty_list_is_serialized_as_json_text,
    test_insert_list_of_dicts_is_serialized_as_json_text,
    test_insert_rejects_plain_scalar_list,
    test_insert_has_no_returning_param,
    test_update_sets_null_for_none_and_binds_other_values,
    test_delete_builds_where_clause,
    test_add_column,
    test_add_column_escapes_single_quotes_in_additional,
    test_drop_column,
    test_drop_all_data_in_a_table,
    test_apply_paramstyle_uses_positional_binds,
]


if __name__ == "__main__":
    for test in UNIT_TESTS:
        test()

    print("all tests passed")
