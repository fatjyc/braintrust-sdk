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
        mock.return_value = repo
        yield repo

def test_get_past_n_ancestors_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_no_ancestor():
    with patch('braintrust.gitutil._current_repo') as mock_repo:
        with patch('braintrust.gitutil._get_base_branch_ancestor', return_value=None):
            mock_repo.return_value = Mock()
            assert list(get_past_n_ancestors()) == []

def test_get_past_n_ancestors_success(mock_repo):
    commits = [Mock(hexsha=f'commit{i}') for i in range(3)]
    for i in range(2):
        commits[i].parents = [commits[i+1]]
    commits[2].parents = []

    mock_repo.commit.return_value = commits[0]
    with patch('braintrust.gitutil._get_base_branch_ancestor', return_value='commit0'):
        result = list(get_past_n_ancestors(n=3))
        assert result == ['commit0', 'commit1', 'commit2']

def test_attempt_success():
    assert attempt(lambda: "success") == "success"

def test_attempt_failure():
    assert attempt(lambda: 1/0) is None

def test_truncate_to_byte_limit_under_limit():
    assert truncate_to_byte_limit("test", 100) == "test"

def test_truncate_to_byte_limit_at_limit():
    input_str = "a" * 65536
    assert truncate_to_byte_limit(input_str) == input_str

def test_truncate_to_byte_limit_over_limit():
    input_str = "a" * 70000
    result = truncate_to_byte_limit(input_str)
    assert len(result.encode('utf-8')) <= 65536

def test_get_repo_info_none_settings():
    with patch('braintrust.gitutil.repo_info', return_value=None):
        assert get_repo_info() is None

def test_get_repo_info_collect_none():
    settings = GitMetadataSettings(collect="none")
    assert get_repo_info(settings) is None

def test_get_repo_info_collect_all():
    mock_info = RepoInfo(commit="123", branch="main", tag=None, dirty=False,
                        author_name="test", author_email="test@test.com",
                        commit_message="test", commit_time="2025-03-14T00:00:00",
                        git_diff=None)
    with patch('braintrust.gitutil.repo_info', return_value=mock_info):
        result = get_repo_info(GitMetadataSettings(collect="all"))
        assert result == mock_info

def test_repo_info_no_repo():
    with patch('braintrust.gitutil._current_repo', return_value=None):
        assert repo_info() is None

def test_repo_info_success(mock_repo):
    head = Mock()
    commit = Mock()
    commit.hexsha = "123abc"
    commit.message = "test commit"
    commit.committed_datetime.isoformat.return_value = "2025-03-14T00:00:00"
    commit.author.name = "Test Author"
    commit.author.email = "test@example.com"

    head.commit = commit
    mock_repo.head = head
    mock_repo.active_branch.name = "main"
    mock_repo.git.describe.return_value = "v1.0"
    mock_repo.is_dirty.return_value = False

    result = repo_info()
    assert result.commit == "123abc"
    assert result.branch == "main"
    assert result.tag == "v1.0"
    assert result.dirty is False
    assert result.author_name == "Test Author"
    assert result.author_email == "test@example.com"
    assert result.commit_message == "test commit"
    assert result.commit_time == "2025-03-14T00:00:00"
    assert result.git_diff is None

def test_repo_info_dirty_repo(mock_repo):
    head = Mock()
    commit = Mock()
    commit.hexsha = "123abc"
    commit.message = "test commit"
    commit.committed_datetime.isoformat.return_value = "2025-03-14T00:00:00"
    commit.author.name = "Test Author"
    commit.author.email = "test@example.com"

    head.commit = commit
    mock_repo.head = head
    mock_repo.is_dirty.return_value = True
    mock_repo.git.diff.return_value = "diff content"

    result = repo_info()
    assert result.dirty is True
    assert result.git_diff == "diff content"
