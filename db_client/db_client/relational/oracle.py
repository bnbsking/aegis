import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import oracledb

from db_client.relational.base import BaseDBAccessor, ColumnConfig, ConditionCollection, build_where


logger = logging.getLogger(__name__)


class DBAccessor(BaseDBAccessor):
    def _connect(
            self,
            host: str = "172.17.0.1",
            port: int = 1521,
            service_name: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
        ):
        return oracledb.connect(
            host=host,
            port=port,
            service_name=service_name or os.environ.get("ORACLE_SERVICE_NAME", "FREEPDB1"),
            user=user or os.environ.get("ORACLE_USER", "system"),
            password=password or os.environ.get("ORACLE_PASSWORD", "123"),
        )

    def _apply_paramstyle(self, sql: str) -> str:
        # oracledb binds are positional-named (:1, :2, ...), unlike psycopg2's %s
        out, bind_index = [], 0
        for ch in sql:
            if ch == "?":
                bind_index += 1
                out.append(f":{bind_index}")
            else:
                out.append(ch)
        return "".join(out)


class SQLCommand:
    # explicit allow-list of zero-arg SQL literals that may be passed through as raw SQL
    # instead of being bound as a parameter (e.g. so a DB-side default like SYSDATE can be forced)
    _RAW_SQL_LITERALS = {"SYSDATE", "SYSTIMESTAMP", "SYS_GUID()"}

    @staticmethod
    def _to_placeholder_params_for_upsert(val: str | Dict | List[Dict]) -> Tuple[str, List]:
        if isinstance(val, str) and val in SQLCommand._RAW_SQL_LITERALS:
            return val, []
        if isinstance(val, dict) or (isinstance(val, list) and (not val or isinstance(val[0], dict))):
            # Oracle has no ::jsonb-style cast - a JSON/CLOB column just takes the text as-is
            return "?", [json.dumps(val)]
        if isinstance(val, list):
            # unlike psycopg2, oracledb has no automatic Python-list -> SQL-array adapter for a
            # plain scalar bind; binding one here would fail at execution time with an opaque
            # driver error, so fail fast with a clear message instead
            raise ValueError(f"oracle.py cannot bind a plain list value ({val!r}); use a list of dicts (JSON) instead")
        return "?", [val]

    @staticmethod
    def _escape_dynamic_sql(text: str) -> str:
        """Escape single quotes in DDL text that gets wrapped in EXECUTE IMMEDIATE '...'."""
        return text.replace("'", "''")

    @staticmethod
    def build_table(table_name: str, col_cfgs: List[ColumnConfig]) -> str:
        cmd_body_list = [f"{col_cfg.column} {col_cfg.sql_type} {col_cfg.additional}" for col_cfg in col_cfgs]
        joined_cols = ",\n".join(cmd_body_list)
        inner_ddl = SQLCommand._escape_dynamic_sql(f"CREATE TABLE {table_name} ({joined_cols})")
        # Oracle has no CREATE TABLE IF NOT EXISTS; ORA-00955 = name already used by an existing object
        return f"""
            BEGIN
                EXECUTE IMMEDIATE '{inner_ddl}';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """

    @staticmethod
    def build_view(view_name: str, table_name: str, cols: List[str]) -> str:
        return f"""CREATE OR REPLACE VIEW {view_name} AS
            SELECT {", ".join(cols)}
            FROM {table_name}
            """

    @staticmethod
    def drop_table(table_name: str) -> str:
        inner_ddl = SQLCommand._escape_dynamic_sql(f"DROP TABLE {table_name}")
        # ORA-00942 = table or view does not exist
        return f"""
            BEGIN
                EXECUTE IMMEDIATE '{inner_ddl}';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN
                        RAISE;
                    END IF;
            END;
            """

    @staticmethod
    def show_tables() -> str:
        return "SELECT table_name FROM user_tables"

    @staticmethod
    def select(
            table_name: str,
            cols: Optional[List[str]] = None,
            conditions: None | str | ConditionCollection = None,
            limit: Optional[int] = None,
        ) -> Tuple[str, List]:
        col_placeholder = ",".join(cols) if cols else "*"
        where_clause, params = build_where(conditions)
        limit_placeholder = f"FETCH FIRST {limit} ROWS ONLY" if limit else ""
        sql = f"SELECT {col_placeholder} FROM {table_name} {where_clause} {limit_placeholder}"
        return sql, params

    @staticmethod
    def insert(table_name: str, data_dict: Dict) -> Tuple[str, List]:
        # no `returning` param here: Postgres's RETURNING is a plain result set, but Oracle's
        # RETURNING clause needs an OUT bind variable through the driver API, so it can't be
        # expressed as a (sql, params) pair the same way - callers must do a separate SELECT
        keys, placeholders, params = [], [], []
        for key, val in data_dict.items():
            if val is None:
                continue
            placeholder, bound = SQLCommand._to_placeholder_params_for_upsert(val)
            keys.append(key)
            placeholders.append(placeholder)
            params.extend(bound)
        sql = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"
        return sql, params

    @staticmethod
    def update(
            table_name: str,
            data_dict: Dict,
            conditions: None | str | ConditionCollection = None,
        ) -> Tuple[str, List]:
        set_clauses, params = [], []
        for key, val in data_dict.items():
            if val is None:
                set_clauses.append(f"{key} = NULL")
                continue
            placeholder, bound = SQLCommand._to_placeholder_params_for_upsert(val)
            set_clauses.append(f"{key} = {placeholder}")
            params.extend(bound)
        where_clause, where_params = build_where(conditions)
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} {where_clause}"
        return sql, params + where_params

    @staticmethod
    def delete(table_name: str, conditions: None | str | ConditionCollection = None) -> Tuple[str, List]:
        where_clause, params = build_where(conditions)
        return f"DELETE FROM {table_name} {where_clause}", params

    @staticmethod
    def add_column(table_name: str, col_cfg: ColumnConfig) -> str:
        inner_ddl = SQLCommand._escape_dynamic_sql(
            f"ALTER TABLE {table_name} ADD ({col_cfg.column} {col_cfg.sql_type} {col_cfg.additional})"
        )
        # Oracle has no ADD COLUMN IF NOT EXISTS; ORA-01430 = column being added already exists
        return f"""
            BEGIN
                EXECUTE IMMEDIATE '{inner_ddl}';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -1430 THEN
                        RAISE;
                    END IF;
            END;
            """

    @staticmethod
    def drop_column(table_name: str, column_name: str) -> str:
        # Oracle has no DROP COLUMN IF EXISTS. Dropping a missing column raises ORA-00904
        # ("invalid identifier"), which is too generic to safely swallow like the other
        # idempotent DDL helpers above, so this one is not idempotent.
        return f"ALTER TABLE {table_name} DROP COLUMN {column_name}"

    @staticmethod
    def drop_all_data_in_a_table(table_name: str) -> str:
        return f"TRUNCATE TABLE {table_name}"


# Intentionally not ported from postgres.py - no reasonable Oracle equivalent:
#   - build_gin_index / select_gin / TagConfig: Oracle has no GIN index or the @>/&& array
#     containment operators; the nearest tools (Oracle Text, JSON_EXISTS/JSON_TABLE) are
#     different enough in shape that they aren't a drop-in replacement.
#   - show_databases: an Oracle instance is one database (schemas/PDBs, not separate
#     databases like Postgres), so there's nothing meaningful to list here.
