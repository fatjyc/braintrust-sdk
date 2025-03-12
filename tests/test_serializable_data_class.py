import json
import pytest
import dataclasses
from typing import List, Optional, Union

from braintrust_core.serializable_data_class import SerializableDataClass

@dataclasses.dataclass
class SimpleDataClass(SerializableDataClass):
    name: str
    age: int

@dataclasses.dataclass
class NestedDataClass(SerializableDataClass):
    id: int
    simple: SimpleDataClass
    optionals: Optional[SimpleDataClass] = None
    items: List[SimpleDataClass] = dataclasses.field(default_factory=list)

def test_as_dict_simple():
    obj = SimpleDataClass(name="test", age=25)
    result = obj.as_dict()
    assert result == {"name": "test", "age": 25}

def test_as_dict_nested():
    simple = SimpleDataClass(name="nested", age=30)
    obj = NestedDataClass(id=1, simple=simple)
    result = obj.as_dict()
    expected = {
        "id": 1,
        "simple": {"name": "nested", "age": 30},
        "optionals": None,
        "items": []
    }
    assert result == expected

def test_as_json_simple():
    obj = SimpleDataClass(name="test", age=25)
    result = obj.as_json()
    expected = '{"name": "test", "age": 25}'
    assert json.loads(result) == json.loads(expected)

def test_as_json_with_kwargs():
    obj = SimpleDataClass(name="test", age=25)
    result = obj.as_json(indent=2)
    expected = '''{
  "name": "test",
  "age": 25
}'''
    assert result == expected

def test_as_json_nested():
    simple = SimpleDataClass(name="nested", age=30)
    items = [SimpleDataClass(name="item1", age=1), SimpleDataClass(name="item2", age=2)]
    obj = NestedDataClass(id=1, simple=simple, items=items)

    result = obj.as_json()
    expected = {
        "id": 1,
        "simple": {"name": "nested", "age": 30},
        "optionals": None,
        "items": [
            {"name": "item1", "age": 1},
            {"name": "item2", "age": 2}
        ]
    }
    assert json.loads(result) == expected
