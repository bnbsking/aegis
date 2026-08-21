from dataclasses import dataclass
import json
import logging
import os
from typing import Dict, List, Literal, Optional, Tuple

import psycopg2

from db_client.relational.base import BaseDBAccessor, ColumnConfig, ConditionCollection, build_where


logger = logging.getLogger(__name__)


class DBAccessor(BaseDBAccessor):
    def _connect(
            self,
            host: str = "172.17.0.1",
            port: int = 5432,
            dbname: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
        ):
        return psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname or os.environ.get("POSTGRES_DB", "mydb"),
            user=user or os.environ.get("POSTGRES_USER", "myuser"),
            password=password or os.environ.get("POSTGRES_PASSWORD", "mypassword"),
        )

    def _apply_paramstyle(self, sql: str) -> str:
        return sql.replace("?", "%s")


@dataclass
class TagConfig:
    key: str
    tags: List[str]
    match_logic: Literal["and", "or"]


class SQLCommand:
    # explicit allow-list of zero-arg SQL function calls that may be passed through as raw SQL
    # instead of being bound as a parameter (e.g. so a DB-side default like NOW() can be forced)
    _RAW_SQL_LITERALS = {"NOW()", "gen_random_uuid()"}

    @staticmethod
    def _to_placeholder_params_for_upsert(val: str | Dict | List[Dict]) -> Tuple[str, List]:
        if isinstance(val, str) and val in SQLCommand._RAW_SQL_LITERALS:
            return val, []
        if isinstance(val, dict) or (isinstance(val, list) and (not val or isinstance(val[0], dict))):
            return "?::jsonb", [json.dumps(val)]
        return "?", [val]

    @staticmethod
    def build_table(table_name: str, col_cfgs: List[ColumnConfig]) -> str:
        cmd_body_list = [f"{col_cfg.column} {col_cfg.sql_type} {col_cfg.additional}" for col_cfg in col_cfgs]
        return f"""CREATE TABLE IF NOT EXISTS {table_name} (\n
                {",\n".join(cmd_body_list)}
            );
            """

    @staticmethod
    def build_view(view_name: str, table_name: str, cols: List[str]) -> str:
        return f"""CREATE OR REPLACE VIEW {view_name} AS
            SELECT {", ".join(cols)}
            FROM {table_name};
            """

    @staticmethod
    def build_gin_index(index_name: str, table_name: str, column_name: str) -> str:
        return f"""CREATE INDEX IF NOT EXISTS {index_name}
            ON {table_name}
            USING GIN ({column_name});
            """

    @staticmethod
    def drop_table(table_name: str) -> str:
        return f"DROP TABLE IF EXISTS {table_name} CASCADE"

    @staticmethod
    def show_databases() -> str:
        return "SELECT datname FROM pg_database;"

    @staticmethod
    def show_tables() -> str:
        return """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """

    @staticmethod
    def select(
            table_name: str,
            cols: Optional[List[str]] = None,
            conditions: None | str | ConditionCollection = None,
            limit: Optional[int] = None,
        ) -> Tuple[str, List]:
        col_placeholder = ",".join(cols) if cols else "*"
        where_clause, params = build_where(conditions)
        limit_placeholder = f"LIMIT {limit}" if limit else ""
        sql = f"SELECT {col_placeholder} FROM {table_name} {where_clause} {limit_placeholder}"
        return sql, params

    @staticmethod
    def insert(table_name: str, data_dict: Dict, returning: str = "") -> Tuple[str, List]:
        keys, placeholders, params = [], [], []
        for key, val in data_dict.items():
            if val is None:
                continue
            placeholder, bound = SQLCommand._to_placeholder_params_for_upsert(val)
            keys.append(key)
            placeholders.append(placeholder)
            params.extend(bound)
        sql = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({', '.join(placeholders)}) {returning}"
        return sql, params

    @staticmethod
    def update(
            table_name: str,
            data_dict: Dict,
            conditions: None | str | ConditionCollection = None,
            returning: str = "",
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
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} {where_clause} {returning}"
        return sql, params + where_params

    @staticmethod
    def delete(table_name: str, conditions: None | str | ConditionCollection = None) -> Tuple[str, List]:
        where_clause, params = build_where(conditions)
        return f"DELETE FROM {table_name} {where_clause}", params

    @staticmethod
    def select_gin(
            table_name: str,
            tag_cfg: TagConfig,
            cols: Optional[List[str]] = None,
        ) -> Tuple[str, List]:
        col_placeholder = ",".join(cols) if cols else "*"
        sign = "@>" if tag_cfg.match_logic.lower() == "and" else "&&"
        sql = f"SELECT {col_placeholder} FROM {table_name} WHERE {tag_cfg.key} {sign} ?"
        return sql, [tag_cfg.tags]

    @staticmethod
    def add_column(table_name: str, col_cfg: ColumnConfig) -> str:
        return f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_cfg.column} {col_cfg.sql_type} {col_cfg.additional}"

    @staticmethod
    def drop_all_data_in_a_table(table_name: str) -> str:
        return f"TRUNCATE {table_name} CASCADE"

    @staticmethod
    def drop_column(table_name: str, column_name: str) -> str:
        return f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name} CASCADE"


def get_table_size(dbaccessor: DBAccessor, table_name: str) -> int:
    dbaccessor.run(f"ANALYZE {table_name}")
    out = dbaccessor.run("SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname = ?", [table_name])
    return out[0][0] if len(out) > 0 and len(out[0]) > 0 else 0
