import requests


def test_cloud_api():
    response = requests.post(
        "http://localhost:8006/cloud_api",
        json={
            "key": "example",
            "base_text": "John Smith is an actor. What is the actor's name?",
            "raw_text": "",
        }
    )
    print(response.json())
    # {'succeed': True, 'deid_text': '', 'output': "The actor's name is John Smith."}


def test_cloud_api_deid():
    response = requests.post(
        "http://localhost:8006/cloud_api",
        json={
            "key": "example",
            "base_text": "{{ deid_text }}. What is the actor's name?",
            "raw_text": "John Smith is an actor.",
        }
    )
    print(response.json())
    # {'succeed': True, 'deid_text': '"[_] is an actor."', 'output': 'Could you please provide more context or specify which actor you are referring to?'}


def test_cloud_api_pydantic():
    response_format_dict = {
        "name": "str",
        "age": "int",
        "hobbies": ["str"]
    }
    response = requests.post(
        "http://localhost:8006/cloud_api",
        json={
            "key": "example",
            "base_text": "John Smith is 30 years old, and his hobbies are reading and coding. Summarize the info in json.",
            "raw_text": "",
            "response_format_dict": response_format_dict
        }
    )
    print(response.json())
    # {'succeed': True, 'deid_text': '', 'output': '{"name":"John Smith","age":30,"hobbies":["reading","coding"]}'}


def test_cloud_api_pydantic_deid():
    response_format_dict = {
        "name": "str",
        "age": "int",
        "hobbies": ["str"]
    }
    response = requests.post(
        "http://localhost:8006/cloud_api",
        json={
            "key": "example",
            "base_text": "Summarize the info in json: {{ deid_text }}",
            "raw_text": "John Smith is 30 years old, and his hobbies are reading and coding.",
            "response_format_dict": response_format_dict
        }
    )
    print(response.json())
    # {'succeed': True, 'deid_text': '"[_] is [_] years old, and his hobbies are reading and coding."', 'output': '{"name":null,"age":null,"hobbies":["reading","coding"]}'}


def test_async_cloud_api():
    response = requests.post(
        "http://localhost:8006/async_cloud_api",
        json=[
            {
                "key": "example",
                "base_text": "John Smith is an actor. What is the actor's name?",
                "raw_text": ""
            },
            {
                "key": "example",
                "base_text": "My phone number is 0912345678. What is my phone number?",
                "raw_text": ""
            }
        ]
    )
    print(response.json())
    # [{'succeed': True, 'deid_text': '', 'output': "The actor's name is John Smith."},
    # {'succeed': True, 'deid_text': '', 'output': 'Your phone number is 0912345678.'}]


def test_async_cloud_api_deid():
    response = requests.post(
        "http://localhost:8006/async_cloud_api",
        json=[
            {
                "key": "example",
                "base_text": "{{ deid_text }}. What is the actor's name?",
                "raw_text": "John Smith is an actor."
            },
            {
                "key": "example",
                "base_text": "{{ deid_text }}. What is my phone number?",
                "raw_text": "My phone number is 0912345678."
            }
        ]
    )
    print(response.json())
    # [{'succeed': True, 'deid_text': '"[_] is an actor."', 'output': 'Could you please provide more context or specify which actor you are referring to?'},
    # {'succeed': True, 'deid_text': '"[_] is [_]".', 'output': "I'm sorry, but I can't help with that."}]


def test_async_cloud_api_pydantic():
    response_format_dict = {
        "name": "str",
        "age": "int",
        "hobbies": ["str"]
    }
    response = requests.post(
        "http://localhost:8006/async_cloud_api",
        json=[
            {
                "key": "example",
                "base_text": "John Smith is 30 years old, and his hobbies are reading and coding. Summarize the info in json.",
                "raw_text": "",
                "response_format_dict": response_format_dict
            },
            {
                "key": "example",
                "base_text": "My name is William Parker, I am 25 years old, and my hobbies are hiking and swimming. Summarize the info in json.",
                "raw_text": "",
                "response_format_dict": response_format_dict
            }
        ]
    )
    print(response.json())
    # [{'succeed': True, 'deid_text': '', 'output': '{"name":"John Smith","age":30,"hobbies":["reading","coding"]}'},
    # {'succeed': True, 'deid_text': '', 'output': '{"name":"William Parker","age":25,"hobbies":["hiking","swimming"]}'}]
    

def test_async_cloud_api_pydantic_deid():
    response_format_dict = {
        "name": "str",
        "age": "int",
        "hobbies": ["str"]
    }
    response = requests.post(
        "http://localhost:8006/async_cloud_api",
        json=[
            {
                "key": "example",
                "base_text": "Summarize the info in json: {{ deid_text }}",
                "raw_text": "John Smith is 30 years old, and his hobbies are reading and coding.",
                "response_format_dict": response_format_dict
            },
            {
                "key": "example",
                "base_text": "Summarize the info in json: {{ deid_text }}",
                "raw_text": "My name is William Parker, I am 25 years old, and my hobbies are hiking and swimming.",
                "response_format_dict": response_format_dict
            }
        ]
    )
    print(response.json())
    # [{'succeed': True, 'deid_text': '"[_] is 30 years old, and his hobbies are reading and coding."', 'output': '{"name":null,"age":30,"hobbies":["reading","coding"]}'},
    #  {'succeed': True, 'deid_text': '"[_] is [_] and [_] and [_] and [_]".', 'output': '{"name":null,"age":null,"hobbies":[null,null,null,null]}'}]


if __name__ == "__main__":
    # test_cloud_api()
    # test_cloud_api_deid()
    
    # test_cloud_api_pydantic()
    # test_cloud_api_pydantic_deid()
    
    test_async_cloud_api()
    test_async_cloud_api_deid()
    
    # test_async_cloud_api_pydantic()
    # test_async_cloud_api_pydantic_deid()
    1
    