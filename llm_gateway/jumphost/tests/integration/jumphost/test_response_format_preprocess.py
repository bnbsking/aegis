from jumphost.response_format_preprocess import schema_to_model


def test_schema_to_model():
    schema = {
        "name": "str",
        "age": "int",
        "hobbies": ["str"]
    }
    model = schema_to_model("Person", schema)
    obj = model(name="Alice", age=30, hobbies=["reading", "coding"])
    assert obj.name == "Alice"
    assert obj.age == 30
    assert obj.hobbies == ["reading", "coding"]
    print(obj)
    # name='Alice' age=30 hobbies=['reading', 'coding']


def test_schema_to_model_nested():
    schema = {
        "name": "str",
        "age": "int",
        "addresses": [
            {
                "street": "str",
                "city": "str",
                "zip_code": "int"
            }
        ]
    }
    model = schema_to_model("PersonWithAddress", schema)
    obj = model(name="Bob", age=25, addresses=[{"street": "123 Main St", "city": "Anytown", "zip_code": 12345}])
    assert obj.name == "Bob"
    assert obj.age == 25
    assert obj.addresses[0].street == "123 Main St"
    assert obj.addresses[0].city == "Anytown"
    assert obj.addresses[0].zip_code == 12345
    print(obj)
    # name='Bob' age=25 addresses=[addresses(street='123 Main St', city='Anytown', zip_code=12345)]


if __name__ == "__main__":
    test_schema_to_model()
    test_schema_to_model_nested()
