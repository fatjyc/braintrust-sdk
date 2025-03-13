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
    with patch('braintrust.gitutil._current_repo') as mock:
        repo = Mock()
        repo.is_dirty.return_value = False
        mock.return_value = repo
        yield repo

@pytest.fixture
def mock_commit():
    commit = Mock()
    commit.hexsha = "abc123"
    commit.message = "Test commit message"
    commit.committed_datetime.isoformat.return_value = "2025-03-01T12:00:00"
    commit.author.name = "Test Author"
    commit.author.email = "test@example.com"
    return commit

def test_get_past_n_ancestors_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_no_ancestor():
    with patch('braintrust.gitutil._current_repo') as mock_repo, \
         patch('braintrust.gitutil._get_base_branch_ancestor', return_value=None):
        mock_repo.return_value = Mock()
        assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_success(mock_repo, mock_commit):
    parent_commit = Mock()
    parent_commit.hexsha = "def456"
    parent_commit.parents = []

    mock_commit.parents = [parent_commit]
    mock_repo.commit.return_value = mock_commit

    with patch('braintrust.gitutil._get_base_branch_ancestor', return_value="abc123"):
        ancestors = list(get_past_n_ancestors(2))
        assert ancestors == ["abc123", "def456"]

def test_attempt_success():
    assert attempt(lambda: "success") == "success"

def test_attempt_failure():
    assert attempt(lambda: int("not_a_number")) is None

def test_truncate_to_byte_limit_under_limit():
    assert truncate_to_byte_limit("test", 10) == "test"

def test_truncate_to_byte_limit_over_limit():
    long_string = "a" * 100
    result = truncate_to_byte_limit(long_string, 10)
    assert len(result.encode('utf-8')) <= 10

def test_get_repo_info_none_settings():
    with patch('braintrust.gitutil.repo_info', return_value=None):
        assert get_repo_info() is None

def test_get_repo_info_collect_none():
    settings = GitMetadataSettings(collect="none")
    assert get_repo_info(settings) is None

def test_get_repo_info_collect_all(mock_repo, mock_commit):
    mock_repo.head.commit = mock_commit
    mock_repo.active_branch.name = "main"
    mock_repo.git.describe.return_value = "v1.0"
    mock_repo.is_dirty.return_value = False

    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"
    assert result.branch == "main"
    assert result.author_name == "Test Author"

def test_repo_info_dirty_repo(mock_repo, mock_commit):
    mock_repo.head.commit = mock_commit
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "diff content"

    result = repo_info()
    assert result.dirty is True
    assert result.git_diff == "diff content"

def test_repo_info_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert repo_info() is None

def test_repo_info_error_handling(mock_repo):
    mock_repo.head.commit.hexsha.side_effect = git.GitCommandError('cmd', 1)

    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit is None
