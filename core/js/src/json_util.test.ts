import { expect, test } from "vitest";
import { deterministicReplacer, constructJsonArray } from "./json_util";

test("deterministicReplacer basic", () => {
  const obj = {
    c: "hello",
    a: { q: 99, d: null },
    b: [9, { c: "yes", d: "no" }, { d: "yes", c: "no" }],
  };
  const obj2 = {
    b: [9, { d: "no", c: "yes" }, { c: "no", d: "yes" }],
    a: { d: null, q: 99 },
    c: "hello",
  };
  expect(obj).toEqual(obj2);

  expect(JSON.stringify(obj)).not.toEqual(JSON.stringify(obj2));
  expect(JSON.stringify(obj, deterministicReplacer)).toEqual(
    JSON.stringify(obj2, deterministicReplacer),
  );
});

test("deterministicReplacer handles non-object values", () => {
  expect(deterministicReplacer("key", "string")).toBe("string");
  expect(deterministicReplacer("key", 123)).toBe(123);
  expect(deterministicReplacer("key", null)).toBe(null);
  expect(deterministicReplacer("key", undefined)).toBe(undefined);
  expect(deterministicReplacer("key", [1, 2, 3])).toEqual([1, 2, 3]);
});

test("deterministicReplacer handles empty object", () => {
  expect(deterministicReplacer("key", {})).toEqual({});
});

test("deterministicReplacer handles nested objects", () => {
  const obj = {
    z: {
      y: {
        x: 1,
        a: 2,
      },
      b: 3,
    },
    a: 4,
  };

  const result = JSON.stringify(obj, deterministicReplacer);
  const parsed = JSON.parse(result);

  expect(parsed).toEqual({
    a: 4,
    z: {
      b: 3,
      y: {
        a: 2,
        x: 1,
      },
    },
  });
});
