import dataclasses
import json
from typing import List, Optional

import pytest
from braintrust_core.serializable_data_class import SerializableDataClass


@dataclasses.dataclass
class SimpleTestClass(SerializableDataClass):
    field1: str
    field2: int


@dataclasses.dataclass
class NestedTestClass(SerializableDataClass):
    name: str
    simple: SimpleTestClass


@dataclasses.dataclass
class ComplexTestClass(SerializableDataClass):
    field1: str
    nested: Optional[NestedTestClass]
    nested_list: List[SimpleTestClass]


def test_as_dict_simple():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_dict()
    assert result == {"field1": "test", "field2": 123}


def test_as_dict_nested():
    simple = SimpleTestClass(field1="inner", field2=456)
    nested = NestedTestClass(name="outer", simple=simple)
    result = nested.as_dict()
    assert result == {"name": "outer", "simple": {"field1": "inner", "field2": 456}}


def test_as_dict_empty_list():
    obj = ComplexTestClass(field1="test", nested=None, nested_list=[])
    result = obj.as_dict()
    assert result == {"field1": "test", "nested": None, "nested_list": []}


def test_as_dict_complex():
    simple1 = SimpleTestClass(field1="s1", field2=1)
    simple2 = SimpleTestClass(field1="s2", field2=2)
    nested = NestedTestClass(name="nested", simple=simple1)
    obj = ComplexTestClass(field1="test", nested=nested, nested_list=[simple1, simple2])
    result = obj.as_dict()
    assert result == {
        "field1": "test",
        "nested": {"name": "nested", "simple": {"field1": "s1", "field2": 1}},
        "nested_list": [{"field1": "s1", "field2": 1}, {"field1": "s2", "field2": 2}],
    }


def test_as_json_simple():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_json()
    assert json.loads(result) == {"field1": "test", "field2": 123}


def test_as_json_with_indent():
    obj = SimpleTestClass(field1="test", field2=123)
    result = obj.as_json(indent=2)
    expected = """{
  "field1": "test",
  "field2": 123
}"""
    assert result == expected


def test_as_json_complex():
    simple1 = SimpleTestClass(field1="s1", field2=1)
    simple2 = SimpleTestClass(field1="s2", field2=2)
    nested = NestedTestClass(name="nested", simple=simple1)
    obj = ComplexTestClass(field1="test", nested=nested, nested_list=[simple1, simple2])
    result = json.loads(obj.as_json())

    assert result == {
        "field1": "test",
        "nested": {"name": "nested", "simple": {"field1": "s1", "field2": 1}},
        "nested_list": [{"field1": "s1", "field2": 1}, {"field1": "s2", "field2": 2}],
    }


def test_as_json_with_none():
    obj = ComplexTestClass(field1="test", nested=None, nested_list=[])
    result = json.loads(obj.as_json())
    assert result == {"field1": "test", "nested": None, "nested_list": []}


def test_as_json_with_special_chars():
    obj = SimpleTestClass(field1='test\nwith\tspecial"chars', field2=123)
    result = obj.as_json()
    parsed = json.loads(result)
    assert parsed["field1"] == 'test\nwith\tspecial"chars'


def test_as_json_with_unicode():
    obj = SimpleTestClass(field1="测试", field2=123)
    result = obj.as_json()
    parsed = json.loads(result)
    assert parsed["field1"] == "测试"
