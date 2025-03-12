import json
import dataclasses
from typing import List, Optional

import pytest

from braintrust_core.serializable_data_class import SerializableDataClass


@dataclasses.dataclass
class SimpleTestClass(SerializableDataClass):
    field1: str
    field2: int


@dataclasses.dataclass
class NestedTestClass(SerializableDataClass):
    nested: SimpleTestClass
    other_field: str


@dataclasses.dataclass
class ListTestClass(SerializableDataClass):
    items: List[SimpleTestClass]
    name: str


@dataclasses.dataclass
class OptionalTestClass(SerializableDataClass):
    optional_field: Optional[SimpleTestClass]
    required_field: str


def test_as_dict_simple():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_dict()
    assert result == {"field1": "test", "field2": 123}


def test_as_dict_empty_string():
    obj = SimpleTestClass(field1="", field2=0)
    result = obj.as_dict()
    assert result == {"field1": "", "field2": 0}


def test_as_json_simple():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_json()
    assert json.loads(result) == {"field1": "test", "field2": 123}


def test_as_json_with_indent():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_json(indent=2)
    expected = '''{
  "field1": "test",
  "field2": 123
}'''
    assert result == expected


def test_as_json_with_special_chars():
    obj = SimpleTestClass(field1="test\nwith\ttabs", field2=123)
    result = obj.as_json()
    assert json.loads(result) == {"field1": "test\nwith\ttabs", "field2": 123}


def test_as_json_empty_string():
    obj = SimpleTestClass(field1="", field2=0)
    result = obj.as_json()
    assert json.loads(result) == {"field1": "", "field2": 0}


def test_as_dict_nested():
    nested = SimpleTestClass(field1="inner", field2=456)
    obj = NestedTestClass(nested=nested, other_field="outer")
    result = obj.as_dict()
    assert result == {
        "nested": {"field1": "inner", "field2": 456},
        "other_field": "outer"
    }


def test_as_json_nested():
    nested = SimpleTestClass(field1="inner", field2=456)
    obj = NestedTestClass(nested=nested, other_field="outer")
    result = obj.as_json()
    assert json.loads(result) == {
        "nested": {"field1": "inner", "field2": 456},
        "other_field": "outer"
    }


def test_as_dict_list():
    items = [
        SimpleTestClass(field1="one", field2=1),
        SimpleTestClass(field1="two", field2=2)
    ]
    obj = ListTestClass(items=items, name="test_list")
    result = obj.as_dict()
    assert result == {
        "items": [
            {"field1": "one", "field2": 1},
            {"field1": "two", "field2": 2}
        ],
        "name": "test_list"
    }


def test_as_json_list():
    items = [
        SimpleTestClass(field1="one", field2=1),
        SimpleTestClass(field1="two", field2=2)
    ]
    obj = ListTestClass(items=items, name="test_list")
    result = obj.as_json()
    assert json.loads(result) == {
        "items": [
            {"field1": "one", "field2": 1},
            {"field1": "two", "field2": 2}
        ],
        "name": "test_list"
    }


def test_as_dict_optional_none():
    obj = OptionalTestClass(optional_field=None, required_field="test")
    result = obj.as_dict()
    assert result == {
        "optional_field": None,
        "required_field": "test"
    }


def test_as_dict_optional_value():
    nested = SimpleTestClass(field1="inner", field2=789)
    obj = OptionalTestClass(optional_field=nested, required_field="test")
    result = obj.as_dict()
    assert result == {
        "optional_field": {"field1": "inner", "field2": 789},
        "required_field": "test"
    }
