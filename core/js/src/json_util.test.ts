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
  // Test primitive values
  expect(deterministicReplacer("key", 42)).toBe(42);
  expect(deterministicReplacer("key", "string")).toBe("string");
  expect(deterministicReplacer("key", null)).toBe(null);
  expect(deterministicReplacer("key", undefined)).toBe(undefined);

  // Test arrays
  const arr = [1, 2, 3];
  expect(deterministicReplacer("key", arr)).toBe(arr);
});

test("deterministicReplacer handles nested objects", () => {
  const obj = {
    z: { c: 3, a: 1, b: 2 },
    x: { f: 6, d: 4, e: 5 },
    y: { i: 9, g: 7, h: 8 },
  };

  const result = deterministicReplacer("", obj) as any;
  const keys = Object.keys(result);
  expect(keys).toEqual(["x", "y", "z"]);

  // Check that nested objects maintain their original values
  expect(result.x.d).toBe(4);
  expect(result.x.e).toBe(5);
  expect(result.x.f).toBe(6);

  expect(result.y.g).toBe(7);
  expect(result.y.h).toBe(8);
  expect(result.y.i).toBe(9);

  expect(result.z.a).toBe(1);
  expect(result.z.b).toBe(2);
  expect(result.z.c).toBe(3);
});

test("constructJsonArray basic", () => {
  expect(constructJsonArray([])).toBe("[]");
  expect(constructJsonArray(["1", "2", "3"])).toBe("[1,2,3]");
  expect(constructJsonArray(['"a"', '"b"', '"c"'])).toBe('["a","b","c"]');
  expect(constructJsonArray(["true", "false"])).toBe("[true,false]");
});
