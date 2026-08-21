from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import traceback
from typing import List, Literal, Sequence, Tuple

import pandas as pd


logger = logging.getLogger(__name__)


class BaseDBAccessor(ABC):
    def __init__(self, **conn_kwargs):
        try:
            self.connect = self._connect(**conn_kwargs)
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    @abstractmethod
    def _connect(self, **conn_kwargs):
        ...

    @abstractmethod
    def _apply_paramstyle(self, sql: str) -> str:
        """
        當 placeholder (例如 f"{self.key} = ?"). 但 ? 只是我們自己約定的「通用符號」，实际的 DB driver 不一定吃這個語法：
        - postgres 要的是 %s
        - oracle 要的是 :1, :2, :3...
        - sqlite3 才是真的吃 ?
        這在 PEP 249 (Python DB API 標準)裡叫 paramstyle,不同 driver 各自定義。
        所以如果你直接把 "age >= ?" 丟給 psycopg2 執行，它會把 ? 當成 SQL 語法本身去解析，直接噴 syntax error —— 完全不會幫你做參數替換。
        """
        ...

    def run(self, sql: str, params: Sequence | None = None) -> List:
        native_sql = self._apply_paramstyle(sql)
        try:
            with self.connect.cursor() as cursor:
                cursor.execute(native_sql, params) if params else cursor.execute(native_sql)
                self.connect.commit()
                out = cursor.fetchall() if cursor.description else None
            return out
        except Exception as e:
            logger.error(f"Error executing SQL command: {sql}\ne={str(e)}. Traceback={traceback.format_exc()}")
            self.connect.rollback()
            return []

    def run_output_df(self, sql: str, params: Sequence | None = None) -> pd.DataFrame:
        try:
            native_sql = self._apply_paramstyle(sql)
            with self.connect.cursor() as cursor:
                cursor.execute(native_sql, params) if params else cursor.execute(native_sql)
                self.connect.commit()
                out = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(out, columns=columns)
            return df
        except Exception as e:
            logger.error(f"Error executing SQL command: {sql}\nException: {str(e)}")
            self.connect.rollback()
            return pd.DataFrame()

    def close(self):
        self.connect.close()


@dataclass
class ColumnConfig:
    """For each backend's build_table/add_column DDL builders"""
    column: str
    sql_type: str
    additional: str = ""


@dataclass
class Condition:
    """A single leaf condition, e.g. `key = value`."""
    key: str
    match_type: Literal["exact", "like", "range"]
    content: None | str | int | float = None
    lb: None | int | float = None
    ub: None | int | float = None

    def _to_placeholder_params(self) -> Tuple[str, List[str | int | float]]:
        if self.match_type == "exact":
            assert self.content is not None
            return f"{self.key} = ?", [self.content]
        elif self.match_type == "like":
            assert self.content is not None
            return f"{self.key} LIKE ?", [f"%{self.content}%"]
        elif self.match_type == "range":
            assert self.lb is not None or self.ub is not None
            if self.lb is None:
                return f"{self.key} <= ?", [self.ub]
            elif self.ub is None:
                return f"{self.key} >= ?", [self.lb]
            else:
                return f"({self.key} <= ? AND {self.key} >= ?)", [self.ub, self.lb]
        else:
            raise ValueError


@dataclass
class ConditionCollection:
    and_list: List[Condition]
    or_list: List[Condition]
    concat_op: Literal["AND", "OR"] = "AND"

    def _merge_list_of_conditions(self, conditions: List[Condition], concat_op: str) -> Tuple[str, List[str | int | float]]:
        placeholders = []
        params = []
        for cond in conditions:
            placeholder, param = cond._to_placeholder_params()
            placeholders.append(placeholder)
            params.extend(param)
        return f" {concat_op} ".join(placeholders), params

    def _merge(self) -> Tuple[str, List[str | int | float]]:
        and_placeholder, and_params = self._merge_list_of_conditions(self.and_list, "AND")
        or_placeholder, or_params = self._merge_list_of_conditions(self.or_list, "OR")

        if and_placeholder and or_placeholder:
            return (
                f"({and_placeholder}) {self.concat_op} ({or_placeholder})",
                and_params + or_params
            )
        elif and_placeholder:
            return and_placeholder, and_params
        elif or_placeholder:
            return or_placeholder, or_params
        else:
            return "", []

    
def build_where(conditions: None | str | ConditionCollection = None) -> Tuple[str, List[str | int | float]]:
    """
    conditions support either:
        1. None                       -> ("", [])
        2. raw "WHERE ..." str        -> (that str, []) — escape hatch for anything the tree can't express
        3. ConditionCollection -> ("WHERE ...", [...]) — the tree of conditions to be converted into a WHERE clause
    """
    if conditions is None:
        return "", []
    elif isinstance(conditions, str):
        assert conditions.startswith("WHERE ")
        return conditions, []
    else:
        assert conditions.and_list or conditions.or_list, "ConditionCollection must have at least one condition"
        placeholder, params = conditions._merge()
        return f"WHERE {placeholder}", params
