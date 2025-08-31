// Application constants
export const THEMES = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system"
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: "em_access",
  REFRESH_TOKEN: "em_refresh",
  THEME: "em_theme"
};

export const ROUTES = {
  HOME: "/",
  RECOGNIZE: "/recognize",
  SOLVE: "/solve",
  RENDER: "/render",
  LOGIN: "/login",
  REGISTER: "/register"
};

export const MATH_SYMBOLS = {
  SQUARE: "x^2",
  SQUARE_ROOT: "\\sqrt{x}",
  FRACTION: "\\frac{a}{b}",
  INTEGRAL: "\\int_{a}^{b}",
  SUM: "\\sum_{i=1}^{n}",
  LIMIT: "\\lim_{x \\to \\infty}",
  SIN: "\\sin(x)",
  COS: "\\cos(x)",
  LOG: "\\log(x)",
  PI: "\\pi",
  INFINITY: "\\infty",
  ALPHA: "\\alpha",
  BETA: "\\beta",
  GAMMA: "\\gamma"
};

export const EXAMPLES = {
  RECOGNIZE: [
    "x^2 - 5x + 6 = 0",
    "\\int_0^1 x^2 dx",
    "\\frac{d}{dx}(x^3 + 2x^2 - 5x + 1)"
  ],
  SOLVE: [
    { name: "Quadratic Equation", expr: "x^2 - 5x + 6 = 0" },
    { name: "Integral", expr: "\\int_0^1 x^2 dx" },
    { name: "Derivative", expr: "\\frac{d}{dx}(x^3 + 2x^2 - 5x + 1)" },
    { name: "Limit", expr: "\\lim_{x \\to 0} \\frac{\\sin(x)}{x}" },
    { name: "System of Equations", expr: "\\begin{cases} x + y = 5 \\\\ 2x - y = 1 \\end{cases}" }
  ],
  RENDER: [
    { name: "Integral", expr: "\\int_0^1 x^2 dx = \\frac{1}{3}" },
    { name: "Quadratic Formula", expr: "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" },
    { name: "Matrix", expr: "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix} = \\begin{pmatrix} ax + by \\\\ cx + dy \\end{pmatrix}" },
    { name: "Sum", expr: "\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}" },
    { name: "Limit", expr: "\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1" },
    { name: "Derivative", expr: "\\frac{d}{dx}[x^n] = nx^{n-1}" }
  ]
};