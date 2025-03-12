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
    mock.head.commit.committed_datetime.isoformat.return_value = "2025-03-14T12:00:00"
    mock.head.commit.author.name = "Test Author"
    mock.head.commit.author.email = "test@example.com"
    mock.active_branch.name = "main"
    return mock

@pytest.fixture
def mock_git():
    with patch('braintrust.gitutil.git', autospec=True) as mock_git:
        yield mock_git

def test_get_past_n_ancestors(mock_repo, mock_git):
    mock_git.Repo.return_value = mock_repo

    # Mock ancestor commit chain
    ancestor1 = Mock()
    ancestor1.hexsha = "abc123"
    ancestor1.parents = [Mock()]
    ancestor1.parents[0].hexsha = "def456"
    ancestor1.parents[0].parents = []

    mock_repo.commit.return_value = ancestor1

    ancestors = list(get_past_n_ancestors(n=2))
    assert len(ancestors) == 2
    assert ancestors == ["abc123", "def456"]

def test_attempt():
    def success():
        return "success"

    def failure():
        raise ValueError()

    assert attempt(success) == "success"
    assert attempt(failure) is None

def test_truncate_to_byte_limit():
    # Test string under limit
    assert truncate_to_byte_limit("test", 10) == "test"

    # Test string at limit
    assert truncate_to_byte_limit("test", 4) == "test"

    # Test string over limit
    long_str = "a" * 100
    truncated = truncate_to_byte_limit(long_str, 10)
    assert len(truncated.encode('utf-8')) <= 10

def test_get_repo_info_none_setting():
    settings = GitMetadataSettings(collect="none")
    assert get_repo_info(settings) is None

def test_get_repo_info_all_setting(mock_repo, mock_git):
    mock_git.Repo.return_value = mock_repo
    settings = GitMetadataSettings(collect="all")

    result = get_repo_info(settings)
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"
    assert result.author_name == "Test Author"

def test_get_repo_info_partial_setting(mock_repo, mock_git):
    mock_git.Repo.return_value = mock_repo
    settings = GitMetadataSettings(collect="partial", fields=["commit", "branch"])

    result = get_repo_info(settings)
    assert result.commit == "abc123"
    assert result.branch == "main"
    assert result.author_name is None

def test_repo_info_clean_repo(mock_repo, mock_git):
    mock_git.Repo.return_value = mock_repo
    mock_repo.git.describe.return_value = "v1.0.0"

    result = repo_info()
    assert isinstance(result, RepoInfo)
    assert result.commit == "abc123"
    assert result.branch == "main"
    assert result.tag == "v1.0.0"
    assert not result.dirty
    assert result.git_diff is None

def test_repo_info_dirty_repo(mock_repo, mock_git):
    mock_git.Repo.return_value = mock_repo
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "diff content"

    result = repo_info()
    assert result.dirty
    assert result.git_diff == "diff content"

def test_repo_info_no_repo(mock_git):
    mock_git.Repo.side_effect = git.exc.InvalidGitRepositoryError()

    result = repo_info()
    assert result is None
