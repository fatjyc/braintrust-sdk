import { describe, expect, it, beforeEach, afterEach } from "vitest";
import { getStackTrace, getCallerLocation } from "./stackutil";
import type { StackTraceEntry } from "./stackutil";
import iso from "./isomorph";

describe("stackutil", () => {
  describe("getStackTrace", () => {
    it("should parse stack trace correctly", () => {
      const trace = getStackTrace();
      expect(trace.length).toBeGreaterThan(0);
      expect(trace[0]).toMatchObject({
        functionName: expect.any(String),
        fileName: expect.any(String),
        lineNo: expect.any(Number)
      });
    });

    it("should handle empty stack trace", () => {
      const mockError = new Error();
      Object.defineProperty(mockError, "stack", {
        get: () => undefined
      });

      const origError = Error;
      // @ts-ignore
      global.Error = class extends Error {
        constructor() {
          super();
          return mockError;
        }
      };

      const trace = getStackTrace();
      expect(trace).toEqual([]);

      global.Error = origError;
    });

    it("should handle malformed stack trace lines", () => {
      const mockError = new Error();
      Object.defineProperty(mockError, "stack", {
        get: () => "Error\n  invalid line\nat foo (file.js:1:1)"
      });

      const origError = Error;
      // @ts-ignore
      global.Error = class extends Error {
        constructor() {
          super();
          return mockError;
        }
      };

      const trace = getStackTrace();
      expect(trace).toEqual([{
        functionName: "foo",
        fileName: "file.js",
        lineNo: 1
      }]);

      global.Error = origError;
    });
  });

  describe("getCallerLocation", () => {
    const origPathDirname = iso.pathDirname;

    beforeEach(() => {
      iso.pathDirname = (path: string) => {
        return path.substring(0, path.lastIndexOf("/"));
      };
    });

    afterEach(() => {
      iso.pathDirname = origPathDirname;
    });

    it("should return undefined when all frames are in same directory", () => {
      const mockError = new Error();
      Object.defineProperty(mockError, "stack", {
        get: () => "Error\n  at test (/path/to/dir/file1.js:1:1)\n  at test2 (/path/to/dir/file2.js:2:1)"
      });

      const origError = Error;
      // @ts-ignore
      global.Error = class extends Error {
        constructor() {
          super();
          return mockError;
        }
      };

      const location = getCallerLocation();
      expect(location).toBeUndefined();

      global.Error = origError;
    });

    it("should return first frame from different directory", () => {
      const mockError = new Error();
      Object.defineProperty(mockError, "stack", {
        get: () => "Error\n  at test (/path/to/dir1/file1.js:1:1)\n  at test2 (/path/to/dir2/file2.js:2:1)"
      });

      const origError = Error;
      // @ts-ignore
      global.Error = class extends Error {
        constructor() {
          super();
          return mockError;
        }
      };

      const location = getCallerLocation();
      expect(location).toEqual({
        caller_functionname: "test2",
        caller_filename: "/path/to/dir2/file2.js",
        caller_lineno: 2
      });

      global.Error = origError;
    });

    it("should handle empty stack trace", () => {
      const mockError = new Error();
      Object.defineProperty(mockError, "stack", {
        get: () => "Error"
      });

      const origError = Error;
      // @ts-ignore
      global.Error = class extends Error {
        constructor() {
          super();
          return mockError;
        }
      };

      const location = getCallerLocation();
      expect(location).toBeUndefined();

      global.Error = origError;
    });
  });
});
