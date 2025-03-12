import os
import sys
import threading
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
    assert captured.out == ""


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
    assert encode_uri_component("test") == "test"
    assert encode_uri_component("test/path") == "test%2Fpath"
    assert encode_uri_component("test space") == "test%20space"
    assert encode_uri_component("test+special&chars") == "test%2Bspecial%26chars"


def test_response_raise_for_status():
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error")
    mock_response.text = "Error details"

    with pytest.raises(AugmentedHTTPError) as exc:
        response_raise_for_status(mock_response)
    assert "Error details" in str(exc.value)

    # Test success case
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.return_value = None
    response_raise_for_status(mock_response)


def test_get_caller_location():
    def inner_func():
        return get_caller_location()

    result = inner_func()
    assert result is not None
    assert "test_util.py" in result["caller_filename"]
    assert result["caller_functionname"] == "test_get_caller_location"


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

    def thread_func():
        assert lazy.get() == "result"

    threads = [threading.Thread(target=thread_func) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert counter == 1


async def async_func():
    return "async"


def test_bt_iscoroutinefunction():
    def normal_func():
        pass

    assert bt_iscoroutinefunction(async_func)
    assert not bt_iscoroutinefunction(normal_func)

    wrapped = MarkAsyncWrapper(normal_func)
    assert bt_iscoroutinefunction(wrapped)


def test_add_azure_blob_headers():
    headers = {}
    url = "https://account.blob.core.windows.net/container/blob"
    add_azure_blob_headers(headers, url)
    assert headers["x-ms-blob-type"] == "BlockBlob"

    # Test non-Azure URL
    headers = {}
    url = "https://example.com/path"
    add_azure_blob_headers(headers, url)
    assert not headers
