module.exports = {
  extends: ["stylelint-config-standard"],
  plugins: ["stylelint-order"],
  overrides: [{ files: ["**/*.html"], customSyntax: "postcss-html" }],
  rules: {
    "rule-empty-line-before": [
      "always-multi-line",
      { except: ["first-nested"], ignore: ["after-comment"] },
    ],
    "at-rule-empty-line-before": [
      "always",
      { except: ["first-nested"], ignore: ["after-comment"] },
    ],
    "comment-empty-line-before": ["always", { except: ["first-nested"] }],

    "order/properties-alphabetical-order": true,
  },
};
