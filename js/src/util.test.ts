import { describe, expect, it, vi } from "vitest";
import {
  LazyValue,
  runCatchFinally,
  getCurrentUnixTimestamp,
  isEmpty,
  addAzureBlobHeaders,
} from "./util";

describe("runCatchFinally", () => {
  it("should handle synchronous successful execution", () => {
    const finallyMock = vi.fn();
    const result = runCatchFinally(
      () => "success",
      (e) => `error: ${e}`,
      finallyMock,
    );
    expect(result).toBe("success");
    expect(finallyMock).toHaveBeenCalledTimes(1);
  });

  it("should handle synchronous error", () => {
    const finallyMock = vi.fn();
    const error = new Error("test error");
    const result = runCatchFinally(
      () => {
        throw error;
      },
      (e) => `caught: ${e}`,
      finallyMock,
    );
    expect(result).toBe(`caught: Error: test error`);
    expect(finallyMock).toHaveBeenCalledTimes(1);
  });

  it("should handle asynchronous successful execution", async () => {
    const finallyMock = vi.fn();
    const result = await runCatchFinally(
      () => Promise.resolve("async success"),
      (e) => `error: ${e}`,
      finallyMock,
    );
    expect(result).toBe("async success");
    expect(finallyMock).toHaveBeenCalledTimes(1);
  });

  it("should handle asynchronous error", async () => {
    const finallyMock = vi.fn();
    const error = new Error("async error");
    const result = await runCatchFinally(
      () => Promise.reject(error),
      (e) => `caught: ${e}`,
      finallyMock,
    );
    expect(result).toBe(`caught: Error: async error`);
    expect(finallyMock).toHaveBeenCalledTimes(1);
  });
});

describe("getCurrentUnixTimestamp", () => {
  it("should return current unix timestamp", () => {
    const timestamp = getCurrentUnixTimestamp();
    expect(typeof timestamp).toBe("number");
    expect(timestamp).toBeGreaterThan(0);
    expect(timestamp).toBeLessThanOrEqual(Date.now() / 1000);
  });
});

describe("isEmpty", () => {
  it("should return true for null and undefined", () => {
    expect(isEmpty(null)).toBe(true);
    expect(isEmpty(undefined)).toBe(true);
  });

  it("should return false for other values", () => {
    expect(isEmpty(0)).toBe(false);
    expect(isEmpty("")).toBe(false);
    expect(isEmpty(false)).toBe(false);
    expect(isEmpty({})).toBe(false);
    expect(isEmpty([])).toBe(false);
  });
});

describe("LazyValue", () => {
  it("evaluates exactly once", async () => {
    let callCount = 0;
    const lazy = new LazyValue(async () => {
      callCount++;
      return "test";
    });

    expect(callCount).toBe(0);
    expect(lazy.hasSucceeded).toBe(false);

    const promise1 = lazy.get();
    const promise2 = lazy.get();

    expect(callCount).toBe(1);
    expect(lazy.hasSucceeded).toBe(false);

    await promise1;
    await promise2;

    expect(callCount).toBe(1);
    expect(lazy.hasSucceeded).toBe(true);
  });

  it("hasSucceeded only set after successful completion", async () => {
    const lazy = new LazyValue(async () => {
      throw new Error("test error");
    });

    expect(lazy.hasSucceeded).toBe(false);

    try {
      await lazy.get();
    } catch (e) {
      expect(e).toBeInstanceOf(Error);
      expect((e as Error).message).toBe("test error");
    }

    expect(lazy.hasSucceeded).toBe(false);
  });

  it("caches successful result", async () => {
    const lazy = new LazyValue(async () => "test value");

    const result1 = await lazy.get();
    const result2 = await lazy.get();

    expect(result1).toBe("test value");
    expect(result2).toBe("test value");
    expect(lazy.hasSucceeded).toBe(true);
  });
});

describe("addAzureBlobHeaders", () => {
  it("should add blob header for azure blob urls", () => {
    const headers: Record<string, string> = {};
    addAzureBlobHeaders(
      headers,
      "https://myaccount.blob.core.windows.net/container/blob",
    );
    expect(headers["x-ms-blob-type"]).toBe("BlockBlob");
  });

  it("should not add blob header for non-azure urls", () => {
    const headers: Record<string, string> = {};
    addAzureBlobHeaders(headers, "https://example.com/file");
    expect(headers["x-ms-blob-type"]).toBeUndefined();
  });
});
