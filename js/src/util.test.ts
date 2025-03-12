import { describe, expect, test } from "vitest";
import {
  LazyValue,
  runCatchFinally,
  getCurrentUnixTimestamp,
  isEmpty,
  addAzureBlobHeaders,
} from "./util";

test("LazyValue evaluates exactly once", async () => {
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

test("LazyValue hasSucceeded only set after successful completion", async () => {
  const lazy = new LazyValue(async () => {
    throw new Error("test error");
  });

  expect(lazy.hasSucceeded).toBe(false);

  try {
    await lazy.get();
  } catch (e) {
    expect(e).toBeInstanceOf(Error);
    // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
    expect((e as Error).message).toBe("test error");
  }

  expect(lazy.hasSucceeded).toBe(false);
});

test("LazyValue caches successful result", async () => {
  const lazy = new LazyValue(async () => "test value");

  const result1 = await lazy.get();
  const result2 = await lazy.get();

  expect(result1).toBe("test value");
  expect(result2).toBe("test value");
  expect(lazy.hasSucceeded).toBe(true);
});

describe("runCatchFinally", () => {
  test("handles synchronous success case", () => {
    let finallyCalled = false;
    const result = runCatchFinally(
      () => "success",
      (e) => `error: ${e}`,
      () => {
        finallyCalled = true;
      },
    );

    expect(result).toBe("success");
    expect(finallyCalled).toBe(true);
  });

  test("handles synchronous error case", () => {
    let finallyCalled = false;
    const result = runCatchFinally(
      () => {
        throw new Error("test error");
      },
      (e) => `caught: ${e}`,
      () => {
        finallyCalled = true;
      },
    );

    expect(result).toBe("caught: Error: test error");
    expect(finallyCalled).toBe(true);
  });

  test("handles asynchronous success case", async () => {
    let finallyCalled = false;
    const result = await runCatchFinally(
      () => Promise.resolve("async success"),
      (e) => `error: ${e}`,
      () => {
        finallyCalled = true;
      },
    );

    expect(result).toBe("async success");
    expect(finallyCalled).toBe(true);
  });

  test("handles asynchronous error case", async () => {
    let finallyCalled = false;
    const result = await runCatchFinally(
      () => Promise.reject(new Error("async error")),
      (e) => `caught: ${e}`,
      () => {
        finallyCalled = true;
      },
    );

    expect(result).toBe("caught: Error: async error");
    expect(finallyCalled).toBe(true);
  });
});

test("getCurrentUnixTimestamp returns number", () => {
  const timestamp = getCurrentUnixTimestamp();
  expect(typeof timestamp).toBe("number");
  expect(timestamp).toBeGreaterThan(0);
});

describe("isEmpty", () => {
  test("returns true for null and undefined", () => {
    expect(isEmpty(null)).toBe(true);
    expect(isEmpty(undefined)).toBe(true);
  });

  test("returns false for other values", () => {
    expect(isEmpty(0)).toBe(false);
    expect(isEmpty("")).toBe(false);
    expect(isEmpty(false)).toBe(false);
    expect(isEmpty({})).toBe(false);
    expect(isEmpty([])).toBe(false);
  });
});

describe("addAzureBlobHeaders", () => {
  test("adds header for Azure blob URLs", () => {
    const headers: Record<string, string> = {};
    addAzureBlobHeaders(
      headers,
      "https://myaccount.blob.core.windows.net/container/blob",
    );
    expect(headers["x-ms-blob-type"]).toBe("BlockBlob");
  });

  test("does not add header for non-Azure URLs", () => {
    const headers: Record<string, string> = {};
    addAzureBlobHeaders(headers, "https://example.com/file");
    expect(headers["x-ms-blob-type"]).toBeUndefined();
  });
});
