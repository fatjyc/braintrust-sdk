import os
import sys
import threading
from unittest.mock import MagicMock, patch

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
    merge_paths = {("b", "c")}

    result = merge_dicts_with_paths(merge_into, merge_from, (), merge_paths)

    assert result == {"a": 1, "b": {"c": 4, "d": 3, "e": 5}, "f": 6}

    # Test invalid inputs
    with pytest.raises(ValueError):
        merge_dicts_with_paths([], {}, (), set())
    with pytest.raises(ValueError):
        merge_dicts_with_paths({}, [], (), set())


def test_merge_dicts():
    merge_into = {"a": 1, "b": {"c": 2}}
    merge_from = {"b": {"d": 3}, "e": 4}

    result = merge_dicts(merge_into, merge_from)

    assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}


def test_encode_uri_component():
    assert encode_uri_component("test/path") == "test%2Fpath"
    assert encode_uri_component("hello world") == "hello%20world"
    assert encode_uri_component("test@example.com") == "test%40example.com"
    assert encode_uri_component("") == ""


def test_response_raise_for_status():
    mock_response = MagicMock(spec=Response)
    mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
    mock_response.text = "Not Found"

    with pytest.raises(AugmentedHTTPError) as exc_info:
        response_raise_for_status(mock_response)
    assert "Not Found" in str(exc_info.value)

    # Test successful response
    mock_response = MagicMock(spec=Response)
    mock_response.raise_for_status.return_value = None
    response_raise_for_status(mock_response)


def test_get_caller_location():
    def nested_function():
        return get_caller_location()

    location = nested_function()
    assert location is not None
    assert "test_util.py" in location["caller_filename"]
    assert location["caller_functionname"] == "test_get_caller_location"


def test_lazy_value():
    counter = 0

    def expensive_computation():
        nonlocal counter
        counter += 1
        return "result"

    # Test without mutex
    lazy = LazyValue(expensive_computation, use_mutex=False)
    assert lazy.get() == "result"
    assert lazy.get() == "result"
    assert counter == 1

    # Test with mutex
    counter = 0
    lazy = LazyValue(expensive_computation, use_mutex=True)
    assert lazy.get() == "result"
    assert lazy.get() == "result"
    assert counter == 1

    # Test thread safety
    counter = 0
    lazy = LazyValue(expensive_computation, use_mutex=True)
    threads = []
    for _ in range(10):
        t = threading.Thread(target=lambda: lazy.get())
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    assert counter == 1


async def async_func():
    return "async"


def sync_func():
    return "sync"


def test_mark_async_wrapper():
    wrapped = MarkAsyncWrapper(async_func)
    assert bt_iscoroutinefunction(wrapped)
    assert not bt_iscoroutinefunction(sync_func)


def test_add_azure_blob_headers():
    headers = {}
    url = "https://example.blob.core.windows.net/container/blob"
    add_azure_blob_headers(headers, url)
    assert headers.get("x-ms-blob-type") == "BlockBlob"

    # Test non-Azure URL
    headers = {}
    url = "https://example.com/path"
    add_azure_blob_headers(headers, url)
    assert "x-ms-blob-type" not in headers
