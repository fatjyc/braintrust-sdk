import os
from unittest.mock import Mock, patch

import pytest
from braintrust.gitutil import (
    GitMetadataSettings,
    RepoInfo,
    attempt,
    get_past_n_ancestors,
    get_repo_info,
    repo_info,
    truncate_to_byte_limit,
)


@pytest.fixture
def mock_repo():
    with patch("braintrust.gitutil._current_repo") as mock:
        repo = Mock()
        repo.is_dirty.return_value = False
        repo.head.commit.hexsha = "abcd1234"
        repo.head.commit.message = "test commit"
        repo.head.commit.committed_datetime.isoformat.return_value = "2025-03-01T12:00:00"
        repo.head.commit.author.name = "Test Author"
        repo.head.commit.author.email = "test@example.com"
        repo.active_branch.name = "main"
        mock.return_value = repo
        yield repo


def test_get_past_n_ancestors_no_repo():
    with patch("braintrust.gitutil._current_repo", return_value=None):
        ancestors = list(get_past_n_ancestors(n=2))
        assert len(ancestors) == 0


def test_get_past_n_ancestors_with_repo(mock_repo):
    mock_repo.commit().hexsha = "abcd1234"
    mock_repo.commit().parents = [Mock(hexsha="efgh5678")]

    with patch("braintrust.gitutil._get_base_branch_ancestor", return_value="abcd1234"):
        ancestors = list(get_past_n_ancestors(n=2))
        assert len(ancestors) == 2
        assert ancestors[0] == "abcd1234"


def test_get_past_n_ancestors_no_parents(mock_repo):
    mock_repo.commit().hexsha = "abcd1234"
    mock_repo.commit().parents = []

    with patch("braintrust.gitutil._get_base_branch_ancestor", return_value="abcd1234"):
        ancestors = list(get_past_n_ancestors(n=2))
        assert len(ancestors) == 1
        assert ancestors[0] == "abcd1234"


def test_attempt():
    def success():
        return "ok"

    def failure():
        raise ValueError()

    assert attempt(success) == "ok"
    assert attempt(failure) is None


def test_attempt_handles_multiple_exceptions():
    def type_error():
        raise TypeError()

    def os_error():
        raise OSError()

    assert attempt(type_error) is None
    assert attempt(os_error) is None


def test_truncate_to_byte_limit():
    # Test string under limit
    assert truncate_to_byte_limit("test", 10) == "test"

    # Test string over limit
    long_str = "a" * 100000
    truncated = truncate_to_byte_limit(long_str, 100)
    assert len(truncated.encode("utf-8")) <= 100

    # Test unicode string
    unicode_str = "🔥" * 100
    truncated = truncate_to_byte_limit(unicode_str, 10)
    assert len(truncated.encode("utf-8")) <= 10


def test_get_repo_info_none_setting():
    settings = GitMetadataSettings(collect="none")
    assert get_repo_info(settings) is None


def test_get_repo_info_all_setting(mock_repo):
    settings = GitMetadataSettings(collect="all")
    info = get_repo_info(settings)
    assert isinstance(info, RepoInfo)
    assert info.commit == "abcd1234"


def test_get_repo_info_selected_fields(mock_repo):
    settings = GitMetadataSettings(collect="selected", fields=["commit", "branch"])
    info = get_repo_info(settings)
    assert info.commit == "abcd1234"
    assert info.branch == "main"
    assert info.author_name is None


def test_get_repo_info_no_settings(mock_repo):
    info = get_repo_info()
    assert isinstance(info, RepoInfo)
    assert info.commit == "abcd1234"


def test_repo_info_no_repo():
    with patch("braintrust.gitutil._current_repo", return_value=None):
        assert repo_info() is None


def test_repo_info_clean_repo(mock_repo):
    info = repo_info()
    assert isinstance(info, RepoInfo)
    assert info.commit == "abcd1234"
    assert info.branch == "main"
    assert info.author_name == "Test Author"
    assert info.author_email == "test@example.com"
    assert info.dirty is False
    assert info.git_diff is None


def test_repo_info_dirty_repo(mock_repo):
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "test diff"

    info = repo_info()
    assert info.dirty is True
    assert info.git_diff == "test diff"


def test_repo_info_error_handling(mock_repo):
    mock_repo.head.commit.hexsha = None
    mock_repo.active_branch.name = None

    info = repo_info()
    assert isinstance(info, RepoInfo)
    assert info.commit is None
    assert info.branch is None


def test_repo_info_with_tag(mock_repo):
    mock_repo.git.describe.return_value = "v1.0.0"
    info = repo_info()
    assert info.tag == "v1.0.0"


def test_repo_info_with_empty_tag(mock_repo):
    mock_repo.git.describe.side_effect = Exception("No tag")
    info = repo_info()
    assert info.tag is None
