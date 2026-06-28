from typing import List, Dict, Optional, Union

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
        raise ValueError(f"Unkown type {val}")


def schema_to_json_str(schema: Dict, to_str: bool = True) -> Union[str, Dict]:
    new_dict = {}
    for key, val in schema.items():
        if isinstance(val, str):
            new_dict[key] = type_map[val]
        elif isinstance(val, List):
            assert len(val) == 1
            if isinstance(val[0], str):
                new_dict[key] = [type_map[val[0]]]
            else:
                new_dict[key] = [schema_to_json_str(val[0], to_str=False)]
        elif isinstance(val, Dict):
            new_dict[key] = schema_to_json_str(val, to_str=False)
        else:
            raise ValueError(f"Unkown type {val}")
    return str(new_dict) if to_str else new_dict
