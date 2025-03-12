import { expect, test } from "vitest";
import {
  camelToSnakeCase,
  _urljoin,
  capitalize,
  lowercase,
  snakeToCamelCase,
  snakeToTitleCase,
} from "./string_util";

test("_urljoin", () => {
  expect(_urljoin("/a", "/b", "/c")).toBe("a/b/c");
  expect(_urljoin("a", "b", "c")).toBe("a/b/c");
  expect(_urljoin("/a/", "/b/", "/c/")).toBe("a/b/c/");
  expect(_urljoin("a/", "b/", "c/")).toBe("a/b/c/");
  expect(_urljoin("", "a", "b", "c")).toBe("a/b/c");
  expect(_urljoin("a", "", "c")).toBe("a/c");
  expect(_urljoin("/", "a", "b", "c")).toBe("a/b/c");
  expect(_urljoin("http://example.com", "api", "v1")).toBe(
    "http://example.com/api/v1",
  );
  expect(_urljoin("http://example.com/", "/api/", "/v1/")).toBe(
    "http://example.com/api/v1/",
  );
  expect(_urljoin()).toBe("");
  expect(_urljoin("a")).toBe("a");
});

test("camelToSnakeCase", () => {
  expect(camelToSnakeCase("myVariable")).toBe("my_variable");
  expect(camelToSnakeCase("MyVariable")).toBe("my_variable");
  expect(camelToSnakeCase("MyVariableName")).toBe("my_variable_name");
  expect(camelToSnakeCase("myVariableName")).toBe("my_variable_name");
  expect(camelToSnakeCase("my_variable_name")).toBe("my_variable_name");
  expect(camelToSnakeCase("my_variable")).toBe("my_variable");
  expect(camelToSnakeCase("my_variable_name")).toBe("my_variable_name");
  expect(camelToSnakeCase("MYVARIABLENAME")).toBe(
    "m_y_v_a_r_i_a_b_l_e_n_a_m_e",
  );
});

test("capitalize", () => {
  expect(capitalize("test")).toBe("Test");
  expect(capitalize("TEST")).toBe("TEST");
  expect(capitalize("")).toBe("");
  expect(capitalize("a")).toBe("A");
  expect(capitalize("test_string", "_")).toBe("Test_String");
  expect(capitalize("test string", " ")).toBe("Test String");
  expect(capitalize("test__string", "_")).toBe("Test__String");
});

test("lowercase", () => {
  expect(lowercase("Test")).toBe("test");
  expect(lowercase("TEST")).toBe("tEST");
  expect(lowercase("")).toBe("");
  expect(lowercase("A")).toBe("a");
  expect(lowercase("Test_String", "_")).toBe("test_string");
  expect(lowercase("Test String", " ")).toBe("test string");
  expect(lowercase("Test__String", "_")).toBe("test__string");
});

test("snakeToCamelCase", () => {
  expect(snakeToCamelCase("my_variable")).toBe("MyVariable");
  expect(snakeToCamelCase("my_variable_name")).toBe("MyVariableName");
  expect(snakeToCamelCase("my__variable")).toBe("MyVariable");
  expect(snakeToCamelCase("")).toBe("");
  expect(snakeToCamelCase("my")).toBe("My");
  expect(snakeToCamelCase("MY_VARIABLE")).toBe("MYVARIABLE");
});

test("snakeToTitleCase", () => {
  expect(snakeToTitleCase("my_variable")).toBe("My Variable");
  expect(snakeToTitleCase("my_variable_name")).toBe("My Variable_Name");
  expect(snakeToTitleCase("my__variable")).toBe("My _Variable");
  expect(snakeToTitleCase("")).toBe("");
  expect(snakeToTitleCase("my")).toBe("My");
  expect(snakeToTitleCase("MY_VARIABLE")).toBe("MY VARIABLE");
});
