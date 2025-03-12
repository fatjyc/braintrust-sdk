import os
import sys
import threading
from unittest.mock import Mock

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


def test_merge_dicts():
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"d": 3}, "e": 4}
    result = merge_dicts(d1, d2)
    assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
    assert result is d1  # Tests in-place modification


def test_merge_dicts_with_paths():
    d1 = {"a": 1, "b": {"c": 2, "d": 3}}
    d2 = {"b": {"c": 4, "e": 5}, "f": 6}
    merge_paths = {("b",)}
    result = merge_dicts_with_paths(d1, d2, (), merge_paths)
    assert result == {"a": 1, "b": {"c": 4, "e": 5}, "f": 6}


def test_merge_dicts_with_paths_invalid_input():
    with pytest.raises(ValueError, match="merge_into must be a dictionary"):
        merge_dicts_with_paths("not a dict", {}, (), set())

    with pytest.raises(ValueError, match="merge_from must be a dictionary"):
        merge_dicts_with_paths({}, "not a dict", (), set())


def test_encode_uri_component():
    assert encode_uri_component("test") == "test"
    assert encode_uri_component("test/path") == "test%2Fpath"
    assert encode_uri_component("test space") == "test%20space"
    assert encode_uri_component("test+plus") == "test%2Bplus"
    assert encode_uri_component("test?query") == "test%3Fquery"


def test_response_raise_for_status():
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.side_effect = HTTPError("Bad Request")
    mock_response.text = "Error details"

    with pytest.raises(AugmentedHTTPError) as exc:
        response_raise_for_status(mock_response)
    assert str(exc.value) == "Error details"


def test_get_caller_location():
    def wrapper():
        return get_caller_location()

    location = wrapper()
    assert location is not None
    assert "test_util.py" in location["caller_filename"]
    assert location["caller_functionname"] == "test_get_caller_location"


def test_lazy_value():
    counter = 0

    def expensive_computation():
        nonlocal counter
        counter += 1
        return "result"

    lazy = LazyValue(expensive_computation, use_mutex=True)
    assert not lazy.has_succeeded
    assert lazy.value is None

    # First call computes
    assert lazy.get() == "result"
    assert counter == 1
    assert lazy.has_succeeded
    assert lazy.value == "result"

    # Subsequent calls use cached value
    assert lazy.get() == "result"
    assert counter == 1


def test_lazy_value_thread_safety():
    counter = 0
    event = threading.Event()

    def slow_computation():
        nonlocal counter
        event.wait()
        counter += 1
        return counter

    lazy = LazyValue(slow_computation, use_mutex=True)

    def thread_func():
        lazy.get()

    threads = [threading.Thread(target=thread_func) for _ in range(3)]
    for t in threads:
        t.start()

    event.set()
    for t in threads:
        t.join()

    assert counter == 1
    assert lazy.value == 1


def test_bt_iscoroutinefunction():
    async def async_func():
        pass

    def sync_func():
        pass

    marked_sync = MarkAsyncWrapper(sync_func)

    assert bt_iscoroutinefunction(async_func)
    assert not bt_iscoroutinefunction(sync_func)
    assert bt_iscoroutinefunction(marked_sync)


def test_add_azure_blob_headers():
    headers = {}
    url = "https://myaccount.blob.core.windows.net/container/blob"
    add_azure_blob_headers(headers, url)
    assert headers == {"x-ms-blob-type": "BlockBlob"}

    # Non-Azure URL should not add headers
    headers = {}
    url = "https://example.com/path"
    add_azure_blob_headers(headers, url)
    assert headers == {}
