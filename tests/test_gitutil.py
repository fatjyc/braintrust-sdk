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
    with patch('git.Repo') as mock:
        repo = Mock()
        mock.return_value = repo
        yield repo

@pytest.fixture
def mock_commit():
    commit = Mock()
    commit.hexsha = "abc123"
    commit.message = "test commit"
    commit.committed_datetime.isoformat.return_value = "2025-03-01T12:00:00"
    commit.author.name = "Test Author"
    commit.author.email = "test@example.com"
    return commit

def test_get_past_n_ancestors(mock_repo, mock_commit):
    mock_repo.commit.return_value = mock_commit
    mock_commit.parents = [mock_commit]

    ancestors = list(get_past_n_ancestors(n=3))
    assert len(ancestors) == 3
    assert all(a == "abc123" for a in ancestors)

def test_get_past_n_ancestors_no_parents(mock_repo, mock_commit):
    mock_repo.commit.return_value = mock_commit
    mock_commit.parents = []

    ancestors = list(get_past_n_ancestors(n=3))
    assert len(ancestors) == 1
    assert ancestors[0] == "abc123"

def test_attempt():
    def success():
        return "success"
    assert attempt(success) == "success"

    def failure():
        raise ValueError()
    assert attempt(failure) is None

def test_truncate_to_byte_limit():
    # Test no truncation needed
    assert truncate_to_byte_limit("test", 10) == "test"

    # Test truncation
    long_str = "a" * 100000
    truncated = truncate_to_byte_limit(long_str, 10)
    assert len(truncated.encode('utf-8')) <= 10

def test_get_repo_info_none_settings():
    with patch('braintrust.gitutil.repo_info') as mock_repo_info:
        mock_repo_info.return_value = None
        assert get_repo_info(GitMetadataSettings(collect="none")) is None

def test_get_repo_info_all_settings():
    repo = RepoInfo(
        commit="abc123",
        branch="main",
        tag="v1.0",
        dirty=False,
        author_name="Test",
        author_email="test@example.com",
        commit_message="test",
        commit_time="2025-03-01T12:00:00",
        git_diff=None
    )

    with patch('braintrust.gitutil.repo_info') as mock_repo_info:
        mock_repo_info.return_value = repo
        result = get_repo_info(GitMetadataSettings(collect="all"))
        assert result == repo

def test_repo_info(mock_repo, mock_commit):
    mock_repo.head.commit = mock_commit
    mock_repo.is_dirty.return_value = False
    mock_repo.active_branch.name = "main"
    mock_repo.git.describe.return_value = "v1.0"

    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"
    assert result.branch == "main"
    assert result.tag == "v1.0"
    assert result.dirty is False
    assert result.author_name == "Test Author"
    assert result.author_email == "test@example.com"
    assert result.commit_message == "test commit"
    assert result.commit_time == "2025-03-01T12:00:00"
    assert result.git_diff is None

def test_repo_info_dirty(mock_repo, mock_commit):
    mock_repo.head.commit = mock_commit
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "diff content"

    result = repo_info()
    assert result.dirty is True
    assert result.git_diff == "diff content"

def test_repo_info_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert repo_info() is None
