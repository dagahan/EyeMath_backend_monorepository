import js from "@eslint/js";
import html from "eslint-plugin-html";
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import globals from "globals";

export default [
  { ignores: ["node_modules", "dist", "build", "coverage"] },
  js.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.browser, ...globals.node },
    },
    rules: {
      "no-multiple-empty-lines": ["error", { max: 2, maxBOF: 0, maxEOF: 1 }],
      "padding-line-between-statements": [
        "error",
        {
          blankLine: "never",
          prev: ["const", "let", "var"],
          next: ["const", "let", "var"],
        },
      ],
    },
  },
  { files: ["**/*.html"], plugins: { html } },
  eslintPluginPrettierRecommended,
];
