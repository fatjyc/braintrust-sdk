import { describe, it, expect, vi, beforeEach } from "vitest";
import { simpleGit, SimpleGit } from "simple-git";
import { currentRepo, getRepoInfo, getPastNAncestors } from "./gitutil";

vi.mock("simple-git");

describe("gitutil", () => {
  let mockGit: SimpleGit;

  beforeEach(() => {
    vi.resetAllMocks();
    mockGit = {
      checkIsRepo: vi.fn(),
      getRemotes: vi.fn(),
      branchLocal: vi.fn(),
      remote: vi.fn(),
      diffSummary: vi.fn(),
      raw: vi.fn(),
      log: vi.fn(),
      revparse: vi.fn(),
    } as unknown as SimpleGit;

    vi.mocked(simpleGit).mockReturnValue(mockGit);
  });

  describe("currentRepo", () => {
    it("returns git object if in repo", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(true);
      const result = await currentRepo();
      expect(result).toBe(mockGit);
    });

    it("returns null if not in repo", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(false);
      const result = await currentRepo();
      expect(result).toBeNull();
    });

    it("returns null on error", async () => {
      vi.mocked(mockGit.checkIsRepo).mockRejectedValue(new Error());
      const result = await currentRepo();
      expect(result).toBeNull();
    });
  });

  describe("getRepoInfo", () => {
    it("returns undefined if collect is none", async () => {
      const result = await getRepoInfo({ collect: "none" });
      expect(result).toBeUndefined();
    });

    it("returns full repo info if collect is all", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(true);
      vi.mocked(mockGit.diffSummary).mockResolvedValue({ files: [] });
      vi.mocked(mockGit.revparse).mockResolvedValue("abc123");
      vi.mocked(mockGit.raw).mockImplementation(async (args) => {
        if (args[0] === "log" && args[2] === "--pretty=%B")
          return "commit message";
        if (args[0] === "log" && args[2] === "--pretty=%cI")
          return "2024-01-01T00:00:00Z";
        if (args[0] === "log" && args[2] === "--pretty=%aN")
          return "Test Author";
        if (args[0] === "log" && args[2] === "--pretty=%aE")
          return "test@example.com";
        if (args[0] === "describe") return "v1.0.0";
        if (args[0] === "rev-parse") return "main";
        return "";
      });

      const result = await getRepoInfo({ collect: "all" });

      expect(result).toEqual({
        commit: "abc123",
        branch: "main",
        tag: "v1.0.0",
        dirty: false,
        author_name: "Test Author",
        author_email: "test@example.com",
        commit_message: "commit message",
        commit_time: "2024-01-01T00:00:00Z",
        git_diff: undefined,
      });
    });

    it("returns only specified fields", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(true);
      vi.mocked(mockGit.diffSummary).mockResolvedValue({ files: [] });
      vi.mocked(mockGit.revparse).mockResolvedValue("abc123");

      const result = await getRepoInfo({
        collect: "selected",
        fields: ["commit"],
      });

      expect(result).toEqual({
        commit: "abc123",
      });
    });
  });

  describe("getPastNAncestors", () => {
    it("returns empty array if not in repo", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(false);
      const result = await getPastNAncestors();
      expect(result).toEqual([]);
    });

    it("returns commit hashes", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(true);
      vi.mocked(mockGit.getRemotes).mockResolvedValue([{ name: "origin" }]);
      vi.mocked(mockGit.branchLocal).mockResolvedValue({ all: ["main"] });
      vi.mocked(mockGit.diffSummary).mockResolvedValue({ files: [] });
      vi.mocked(mockGit.raw).mockImplementation(async (args) => {
        if (args[0] === "merge-base") return "abc123";
        return "";
      });
      vi.mocked(mockGit.log).mockResolvedValue({
        all: [{ hash: "abc123" }, { hash: "def456" }],
      } as any);

      const result = await getPastNAncestors(2);
      expect(result).toEqual(["abc123", "def456"]);
    });

    it("returns empty array when no common ancestor found", async () => {
      vi.mocked(mockGit.checkIsRepo).mockResolvedValue(true);
      vi.mocked(mockGit.getRemotes).mockResolvedValue([{ name: "origin" }]);
      vi.mocked(mockGit.branchLocal).mockResolvedValue({ all: ["main"] });
      vi.mocked(mockGit.diffSummary).mockResolvedValue({ files: [] });
      vi.mocked(mockGit.raw).mockRejectedValue(new Error("No common ancestor"));

      const result = await getPastNAncestors(2);
      expect(result).toEqual([]);
    });
  });
});
