from typing import Dict, List, Optional


class BaseResponseFormatConverter:
    def convert(self, response_format: Dict) -> Dict:
        raise NotImplementedError("Subclasses must implement the convert method.")


class PropertiesResponseFormatConverter(BaseResponseFormatConverter):
    type_map = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean"
    }

    def schema_to_dict(self, schema: str | List | Dict) -> Dict:
        if isinstance(schema, str) and schema in self.type_map:
            return {"type": self.type_map[schema]}
        elif isinstance(schema, List):
            assert len(schema) == 1
            return {"type": "array", "items": self.schema_to_dict(schema[0])}
        elif isinstance(schema, Dict):
            properties = {}
            for key, val in schema.items():
                properties[key] = self.schema_to_dict(val)
            return {"type": "object", "properties": properties}
        else:
            raise ValueError(f"Unknown type {schema}")

    def convert(self, response_format: Dict) -> Dict:
        if response_format.get("type", "") == "object" and "properties" in response_format:
            return response_format
        else:
            return self.schema_to_dict(response_format)


class PromptHintResponseFormatConverter(BaseResponseFormatConverter):
    type_map = {
        "str": Optional[str],
        "int": Optional[int],
        "float": Optional[float],
        "bool": Optional[bool]
    }  # allow null

    def schema_to_json_str(self, schema: Dict) -> str:
        out = {}
        for key, val in schema.items():
            if isinstance(val, str):
                out[key] = self.type_map[val]
            elif isinstance(val, List):
                assert len(val) == 1
                if isinstance(val[0], str):
                    out[key] = [self.type_map[val[0]]]
                else:
                    out[key] = [self.schema_to_json_str(val[0])]
            elif isinstance(val, Dict):
                out[key] = self.schema_to_json_str(val)
            else:
                raise ValueError(f"Unkown type {val}")
        return str(out)

    def convert(self, response_format: Dict) -> str:
       return self.schema_to_json_str(response_format)
