import { describe, it, expect, vi, beforeEach } from "vitest";
import { simpleGit } from "simple-git";
import { currentRepo, getRepoInfo, getPastNAncestors } from "./gitutil";

vi.mock("simple-git", () => ({
  simpleGit: vi.fn(),
}));

describe("gitutil", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe("currentRepo", () => {
    it("should return git object when in a git repo", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBe(mockGit);
    });

    it("should return null when not in a git repo", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(false),
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBeNull();
    });

    it("should return null when git check throws error", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockRejectedValue(new Error("git error")),
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await currentRepo();
      expect(result).toBeNull();
    });
  });

  describe("getRepoInfo", () => {
    it("should return undefined when collect is none", async () => {
      const result = await getRepoInfo({ collect: "none" });
      expect(result).toBeUndefined();
    });

    it("should return full repo info when collect is all", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        revparse: vi.fn().mockResolvedValue("abc123"),
        raw: vi.fn()
          .mockResolvedValueOnce("commit message")
          .mockResolvedValueOnce("2025-03-14")
          .mockResolvedValueOnce("Test Author")
          .mockResolvedValueOnce("test@email.com")
          .mockResolvedValueOnce("v1.0.0")
          .mockResolvedValueOnce("main"),
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getRepoInfo({ collect: "all" });

      expect(result).toEqual({
        commit: "abc123",
        branch: "main",
        tag: "v1.0.0",
        dirty: false,
        author_name: "Test Author",
        author_email: "test@email.com",
        commit_message: "commit message",
        commit_time: "2025-03-14",
        git_diff: undefined,
      });
    });

    it("should return selected fields when fields are specified", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        revparse: vi.fn().mockResolvedValue("abc123"),
        raw: vi.fn().mockResolvedValue("main"),
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getRepoInfo({
        collect: "selected",
        fields: ["commit", "branch"],
      });

      expect(result).toEqual({
        commit: "abc123",
        branch: "main",
      });
    });
  });

  describe("getPastNAncestors", () => {
    it("should return empty array when not in git repo", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(false),
      };
      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getPastNAncestors();
      expect(result).toEqual([]);
    });

    it("should return commit hashes", async () => {
      const mockGit = {
        checkIsRepo: vi.fn().mockResolvedValue(true),
        diffSummary: vi.fn().mockResolvedValue({ files: [] }),
        remote: vi.fn().mockResolvedValue("origin"),
        getRemotes: vi.fn().mockResolvedValue([{ name: "origin" }]),
        branchLocal: vi.fn().mockResolvedValue({ all: ["main"] }),
        raw: vi.fn().mockResolvedValue("abc123"),
        log: vi.fn().mockResolvedValue({
          all: [
            { hash: "commit1" },
            { hash: "commit2" },
          ],
        }),
      };

      vi.mocked(simpleGit).mockReturnValue(mockGit as any);

      const result = await getPastNAncestors(2);
      expect(result).toEqual(["commit1", "commit2"]);
    });
  });
});
