import os
import pytest
from unittest.mock import Mock, patch
from braintrust.gitutil import (
    get_past_n_ancestors,
    attempt,
    truncate_to_byte_limit,
    get_repo_info,
    repo_info,
    GitMetadataSettings,
    RepoInfo
)

@pytest.fixture
def mock_repo():
    with patch('braintrust.gitutil._current_repo') as mock:
        repo = Mock()
        repo.is_dirty.return_value = False
        repo.head.commit.hexsha = "abc123"
        repo.head.commit.message = "test commit"
        repo.head.commit.committed_datetime.isoformat.return_value = "2025-03-01T12:00:00"
        repo.head.commit.author.name = "Test Author"
        repo.head.commit.author.email = "test@example.com"
        repo.active_branch.name = "main"
        mock.return_value = repo
        yield repo

def test_get_past_n_ancestors_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_no_ancestor():
    with patch('braintrust.gitutil._current_repo') as mock_repo, \
         patch('braintrust.gitutil._get_base_branch_ancestor', return_value=None):
        mock_repo.return_value = Mock()
        assert list(get_past_n_ancestors()) == []

def test_attempt_success():
    assert attempt(lambda: "success") == "success"

def test_attempt_failure():
    assert attempt(lambda: 1/0) is None

def test_truncate_to_byte_limit_under_limit():
    assert truncate_to_byte_limit("test", 100) == "test"

def test_truncate_to_byte_limit_over_limit():
    long_str = "a" * 100000
    result = truncate_to_byte_limit(long_str, 10)
    assert len(result.encode('utf-8')) <= 10

def test_get_repo_info_none_setting():
    settings = GitMetadataSettings(collect="none")
    assert get_repo_info(settings) is None

def test_get_repo_info_all_setting(mock_repo):
    settings = GitMetadataSettings(collect="all")
    result = get_repo_info(settings)
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"

def test_get_repo_info_filtered_setting(mock_repo):
    settings = GitMetadataSettings(collect="filtered", fields=["commit"])
    result = get_repo_info(settings)
    assert result.commit == "abc123"
    assert result.branch is None

def test_repo_info_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert repo_info() is None

def test_repo_info_success(mock_repo):
    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"
    assert result.author_name == "Test Author"
    assert result.author_email == "test@example.com"
    assert result.branch == "main"
    assert not result.dirty

def test_repo_info_dirty_repo(mock_repo):
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "test diff"
    result = repo_info()
    assert result.dirty
    assert result.git_diff == "test diff"

def test_repo_info_error_handling(mock_repo):
    mock_repo.head.commit.hexsha = None
    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit is None
