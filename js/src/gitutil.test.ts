import { describe, it, expect, vi, beforeEach } from 'vitest';
import { simpleGit } from 'simple-git';
import { currentRepo, getRepoInfo, getPastNAncestors } from './gitutil';

vi.mock('simple-git', () => ({
  simpleGit: vi.fn()
}));

describe('gitutil', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('currentRepo', () => {
    it('returns git object when in a repo', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true)
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBe(mockGit);
    });

    it('returns null when not in a repo', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(false)
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBeNull();
    });

    it('returns null on error', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockRejectedValue(new Error())
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBeNull();
    });
  });

  describe('getRepoInfo', () => {
    it('returns undefined when collect is none', async () => {
      const result = await getRepoInfo({ collect: 'none' });
      expect(result).toBeUndefined();
    });

    it('returns full repo info when collect is all', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        revparse: vi.fn().mockResolvedValue('abc123'),
        raw: vi.fn().mockImplementation((args) => {
          if (args.includes('log')) {
            return Promise.resolve('test message');
          }
          return Promise.resolve('');
        })
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getRepoInfo({ collect: 'all' });

      expect(result).toEqual(expect.objectContaining({
        commit: 'abc123',
        commit_message: 'test message',
        dirty: false
      }));
    });

    it('returns filtered repo info when fields specified', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        revparse: vi.fn().mockResolvedValue('abc123'),
        raw: vi.fn().mockResolvedValue('test')
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getRepoInfo({
        collect: 'selected',
        fields: ['commit']
      });

      expect(result).toEqual({
        commit: 'abc123'
      });
    });
  });

  describe('getPastNAncestors', () => {
    it('returns empty array when not in git repo', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(false)
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getPastNAncestors();
      expect(result).toEqual([]);
    });

    it('returns commit hashes', async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        getRemotes: vi.fn().mockResolvedValue([{ name: 'origin' }]),
        branchLocal: vi.fn().mockResolvedValue({ all: ['main'] }),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        raw: vi.fn().mockResolvedValue('abc123'),
        log: vi.fn().mockResolvedValue({
          all: [
            { hash: 'abc123' },
            { hash: 'def456' }
          ]
        })
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getPastNAncestors(2);
      expect(result).toEqual(['abc123', 'def456']);
    });
  });
});
