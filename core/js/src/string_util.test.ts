import { expect, test } from "vitest";
import { camelToSnakeCase, _urljoin, capitalize, lowercase, snakeToCamelCase, snakeToTitleCase } from "./string_util";

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
  expect(capitalize("hello")).toBe("Hello");
  expect(capitalize("hello_world", "_")).toBe("Hello_World");
  expect(capitalize("")).toBe("");
  expect(capitalize("a")).toBe("A");
  expect(capitalize("hello world", " ")).toBe("Hello World");
  expect(capitalize("HELLO")).toBe("HELLO");
});

test("lowercase", () => {
  expect(lowercase("HELLO")).toBe("hELLO");
  expect(lowercase("Hello_World", "_")).toBe("hello_world");
  expect(lowercase("")).toBe("");
  expect(lowercase("A")).toBe("a");
  expect(lowercase("Hello World", " ")).toBe("hello world");
  expect(lowercase("hello")).toBe("hello");
});

test("snakeToCamelCase", () => {
  expect(snakeToCamelCase("my_variable")).toBe("MyVariable");
  expect(snakeToCamelCase("my_variable_name")).toBe("MyVariableName");
  expect(snakeToCamelCase("my_Variable_Name")).toBe("MyVariableName");
  expect(snakeToCamelCase("MY_VARIABLE_NAME")).toBe("MYVARIABLENAME");
  expect(snakeToCamelCase("my_variable_")).toBe("MyVariable");
  expect(snakeToCamelCase("_my_variable")).toBe("MyVariable");
  expect(snakeToCamelCase("")).toBe("");
});

test("snakeToTitleCase", () => {
  expect(snakeToTitleCase("my_variable")).toBe("My Variable");
  expect(snakeToTitleCase("my_variable_name")).toBe("My Variable_Name");
  expect(snakeToTitleCase("MY_VARIABLE_NAME")).toBe("MY VARIABLE_NAME");
  expect(snakeToTitleCase("my_variable_")).toBe("My Variable_");
  expect(snakeToTitleCase("_my_variable")).toBe(" My_Variable");
  expect(snakeToTitleCase("")).toBe("");
});
