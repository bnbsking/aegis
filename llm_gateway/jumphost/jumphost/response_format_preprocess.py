from typing import List, Dict, Optional

from pydantic import create_model


type_map = {
    "str": Optional[str],
    "int": Optional[int],
    "float": Optional[float],
    "bool": Optional[bool]
}  # allow null


def schema_to_model(name: str, schema) -> type:
    if isinstance(schema, str) and schema in type_map:
        return type_map[schema]
    elif isinstance(schema, List):
        assert len(schema) == 1
        return List[schema_to_model(name, schema[0])]
    elif isinstance(schema, Dict):
        fields = {}
        for key, val in schema.items():
            fields[key] = (schema_to_model(key, val), ...)
        return create_model(name, **fields)
    else:
        raise ValueError(f"Unkown type {schema}")
