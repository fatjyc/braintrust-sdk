import os
import sys
import urllib.parse
from unittest.mock import Mock, patch

import pytest
from requests import HTTPError, Response

from braintrust.util import (
    AugmentedHTTPError,
    LazyValue,
    MarkAsyncWrapper,
    add_azure_blob_headers,
    bt_iscoroutinefunction,
    coalesce,
    encode_uri_component,
    eprint,
    get_caller_location,
    merge_dicts,
    merge_dicts_with_paths,
    response_raise_for_status,
)


def test_eprint(capsys):
    eprint("test error")
    captured = capsys.readouterr()
    assert captured.err == "test error\n"


def test_coalesce():
    assert coalesce(None, None, "a", "b") == "a"
    assert coalesce(None, None, None) is None
    assert coalesce(1, 2, 3) == 1
    assert coalesce("", None) == ""


def test_merge_dicts_with_paths():
    merge_into = {"a": 1, "b": {"c": 2, "d": 3}}
    merge_from = {"b": {"c": 4, "e": 5}, "f": 6}
    paths = {("b", "c")}

    result = merge_dicts_with_paths(merge_into, merge_from, (), paths)

    assert result == {"a": 1, "b": {"c": 4, "d": 3, "e": 5}, "f": 6}


def test_merge_dicts_with_paths_invalid_input():
    with pytest.raises(ValueError):
        merge_dicts_with_paths("not a dict", {}, (), set())

    with pytest.raises(ValueError):
        merge_dicts_with_paths({}, "not a dict", (), set())


def test_merge_dicts():
    merge_into = {"a": 1, "b": {"c": 2}}
    merge_from = {"b": {"d": 3}, "e": 4}

    result = merge_dicts(merge_into, merge_from)

    assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}


def test_encode_uri_component():
    assert encode_uri_component("test/path") == "test%2Fpath"
    assert encode_uri_component("hello world") == "hello%20world"
    assert encode_uri_component("!@#$%^&*()") == "%21%40%23%24%25%5E%26%2A%28%29"
    assert encode_uri_component("üñîçødé") == "%C3%BC%C3%B1%C3%AE%C3%A7%C3%B8d%C3%A9"


def test_response_raise_for_status():
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error")
    mock_response.text = "Error details"

    with pytest.raises(AugmentedHTTPError) as exc_info:
        response_raise_for_status(mock_response)

    assert "Error details" in str(exc_info.value)


def test_get_caller_location():
    def wrapper():
        return get_caller_location()

    result = wrapper()

    assert result is not None
    assert "test_util.py" in result["caller_filename"]
    assert result["caller_functionname"] == "test_get_caller_location"


def test_lazy_value():
    counter = 0
    def expensive_computation():
        nonlocal counter
        counter += 1
        return "result"

    lazy = LazyValue(expensive_computation, use_mutex=True)

    assert not lazy.has_succeeded
    assert lazy.value is None

    result1 = lazy.get()
    assert result1 == "result"
    assert counter == 1

    result2 = lazy.get()
    assert result2 == "result"
    assert counter == 1  # Should not recompute


def test_lazy_value_no_mutex():
    lazy = LazyValue(lambda: "result", use_mutex=False)
    assert lazy.get() == "result"


async def async_func():
    return "async result"

def sync_func():
    return "sync result"

def test_bt_iscoroutinefunction():
    assert bt_iscoroutinefunction(async_func)
    assert not bt_iscoroutinefunction(sync_func)

    wrapped = MarkAsyncWrapper(sync_func)
    assert bt_iscoroutinefunction(wrapped)


def test_add_azure_blob_headers():
    headers = {}
    url = "https://myaccount.blob.core.windows.net/container/blob"

    add_azure_blob_headers(headers, url)
    assert headers.get("x-ms-blob-type") == "BlockBlob"

    # Should not add headers for non-Azure URLs
    headers = {}
    url = "https://example.com/path"
    add_azure_blob_headers(headers, url)
    assert "x-ms-blob-type" not in headers
