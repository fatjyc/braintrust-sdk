import os
import pytest
from unittest.mock import Mock, patch
import git
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
    mock = Mock()
    mock.is_dirty.return_value = False
    mock.head.commit.hexsha = "abc123"
    mock.head.commit.message = "test commit"
    mock.head.commit.committed_datetime.isoformat.return_value = "2025-03-01T12:00:00"
    mock.head.commit.author.name = "Test User"
    mock.head.commit.author.email = "test@example.com"
    mock.active_branch.name = "main"
    mock.git.describe.return_value = "v1.0"
    mock.git.diff.return_value = "test diff"
    return mock

@pytest.fixture
def mock_git_repo(mocker, mock_repo):
    mocker.patch("braintrust.gitutil._current_repo", return_value=mock_repo)
    return mock_repo

def test_get_past_n_ancestors_no_repo(mocker):
    mocker.patch("braintrust.gitutil._current_repo", return_value=None)
    assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_no_ancestor(mocker, mock_git_repo):
    mocker.patch("braintrust.gitutil._get_base_branch_ancestor", return_value=None)
    assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_success(mocker, mock_git_repo):
    ancestor_commit = Mock()
    ancestor_commit.hexsha = "def456"
    ancestor_commit.parents = [Mock(hexsha="ghi789")]

    mock_git_repo.commit.return_value = ancestor_commit
    mocker.patch("braintrust.gitutil._get_base_branch_ancestor", return_value="def456")

    ancestors = list(get_past_n_ancestors(n=2))
    assert len(ancestors) == 2
    assert ancestors == ["def456", "ghi789"]

def test_attempt_success():
    assert attempt(lambda: "success") == "success"

def test_attempt_failure():
    assert attempt(lambda: int("not_a_number")) is None

def test_truncate_to_byte_limit_under_limit():
    input_str = "test string"
    assert truncate_to_byte_limit(input_str, 100) == input_str

def test_truncate_to_byte_limit_over_limit():
    input_str = "test" * 20000
    result = truncate_to_byte_limit(input_str, 10)
    assert len(result.encode('utf-8')) <= 10

def test_get_repo_info_none_settings():
    with patch("braintrust.gitutil.repo_info") as mock_repo_info:
        mock_repo_info.return_value = None
        assert get_repo_info() is None

def test_get_repo_info_all_settings():
    repo = RepoInfo(
        commit="abc123",
        branch="main",
        tag="v1.0",
        dirty=False,
        author_name="Test",
        author_email="test@test.com",
        commit_message="test",
        commit_time="2025-03-01T12:00:00",
        git_diff=None
    )

    with patch("braintrust.gitutil.repo_info") as mock_repo_info:
        mock_repo_info.return_value = repo
        settings = GitMetadataSettings(collect="all")
        result = get_repo_info(settings)
        assert result == repo

def test_get_repo_info_filtered_settings():
    repo = RepoInfo(
        commit="abc123",
        branch="main",
        tag="v1.0",
        dirty=False,
        author_name="Test",
        author_email="test@test.com",
        commit_message="test",
        commit_time="2025-03-01T12:00:00",
        git_diff=None
    )

    with patch("braintrust.gitutil.repo_info") as mock_repo_info:
        mock_repo_info.return_value = repo
        settings = GitMetadataSettings(collect="some", fields=["commit", "branch"])
        result = get_repo_info(settings)
        assert result.commit == "abc123"
        assert result.branch == "main"
        assert result.tag is None

def test_repo_info_no_repo(mocker):
    mocker.patch("braintrust.gitutil._current_repo", return_value=None)
    assert repo_info() is None

def test_repo_info_success(mock_git_repo):
    result = repo_info()
    assert result.commit == "abc123"
    assert result.branch == "main"
    assert result.tag == "v1.0"
    assert result.author_name == "Test User"
    assert result.author_email == "test@example.com"
    assert result.commit_message == "test commit"
    assert result.commit_time == "2025-03-01T12:00:00"
    assert not result.dirty

def test_repo_info_dirty(mock_git_repo):
    mock_git_repo.is_dirty.return_value = True
    result = repo_info()
    assert result.dirty
    assert result.git_diff == "test diff"
