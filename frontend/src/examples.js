export const exampleCategories = {
  'Basic Algebra': [
    { name: "Quadratic equation", expr: "x^2 - 5x + 6 = 0" },
    { name: "Cubic equation", expr: "x^3 - 6x^2 + 11x - 6 = 0" },
    { name: "Biquadratic equation", expr: "x^4 - 10x^2 + 9 = 0" },
    { name: "Difference of squares", expr: "x^2 - 4" },
    { name: "Sum of cubes", expr: "x^3 + 8" },
    { name: "Difference of cubes", expr: "x^3 - 27" },
    { name: "Perfect square", expr: "x^2 + 2x + 1" },
    { name: "4th degree polynomial", expr: "x^4 - 1" },
    { name: "Rational expression", expr: "\\frac{x^2 - 1}{x - 1}" },
    { name: "Complex expression", expr: "(x + 1)^2 - (x - 1)^2" },
    { name: "Polynomial division", expr: "\\frac{x^3 + 2x^2 - 5x + 1}{x - 2}" },
    { name: "Partial fractions", expr: "\\frac{1}{x^2 - 1}" },
    { name: "Rational equation", expr: "\\frac{x + 1}{x - 1} = \\frac{x - 1}{x + 1}" },
    { name: "Radical equation", expr: "\\sqrt{x + 3} = x - 1" },
    { name: "Absolute value equation", expr: "|2x - 3| = 5" }
  ],
  
  'Differentiation': [
    { name: "Derivative of x²", expr: "\\frac{d}{dx}(x^2)" },
    { name: "Derivative of sin(x)", expr: "\\frac{d}{dx}(\\sin(x))" },
    { name: "Derivative of cos(x)", expr: "\\frac{d}{dx}(\\cos(x))" },
    { name: "Derivative of e^x", expr: "\\frac{d}{dx}(e^x)" },
    { name: "Derivative of ln(x)", expr: "\\frac{d}{dx}(\\ln(x))" },
    { name: "Derivative of polynomial", expr: "\\frac{d}{dx}(x^3 + 2x^2 - 5x + 1)" },
    { name: "Derivative of composite function", expr: "\\frac{d}{dx}(\\sin(x^2))" },
    { name: "Derivative of product", expr: "\\frac{d}{dx}(x \\cdot e^x)" },
    { name: "Derivative of quotient", expr: "\\frac{d}{dx}\\left(\\frac{x^2 + 1}{x - 1}\\right)" },
    { name: "Derivative of power", expr: "\\frac{d}{dx}((x^2 + 1)^3)" }
  ],
  
  'Integration': [
    { name: "Integral of x²", expr: "\\int x^2 dx" },
    { name: "Integral of sin(x)", expr: "\\int \\sin(x) dx" },
    { name: "Integral of cos(x)", expr: "\\int \\cos(x) dx" },
    { name: "Integral of e^x", expr: "\\int e^x dx" },
    { name: "Integral of 1/x", expr: "\\int \\frac{1}{x} dx" },
    { name: "Integral of polynomial", expr: "\\int (x^3 + 2x^2 - 5x + 1) dx" },
    { name: "Integral of product", expr: "\\int x \\cdot e^x dx" },
    { name: "Integral of rational function", expr: "\\int \\frac{1}{x^2 + 1} dx" },
    { name: "Integral of composite function", expr: "\\int \\sin(x^2) \\cdot x dx" },
    { name: "Integral of power", expr: "\\int (x^2 + 1)^2 dx" }
  ],
  
  'Definite Integrals': [
    { name: "Integral from 0 to 1", expr: "\\int_0^1 x^2 dx" },
    { name: "Integral of sine", expr: "\\int_0^{\\pi} \\sin(x) dx" },
    { name: "Integral of cosine", expr: "\\int_0^{\\pi/2} \\cos(x) dx" },
    { name: "Integral of exponential", expr: "\\int_0^1 e^x dx" },
    { name: "Integral of logarithm", expr: "\\int_1^e \\frac{1}{x} dx" },
    { name: "Integral from -1 to 1", expr: "\\int_{-1}^1 x^2 dx" },
    { name: "Integral of product", expr: "\\int_0^1 x \\cdot e^x dx" },
    { name: "Integral of rational function", expr: "\\int_0^1 \\frac{1}{x^2 + 1} dx" },
    { name: "Integral with infinite limits", expr: "\\int_0^{\\infty} e^{-x} dx" },
    { name: "Integral from 0 to π", expr: "\\int_0^{\\pi} x \\sin(x) dx" }
  ],
  
  'Limits': [
    { name: "Limit of sin(x)/x", expr: "\\lim_{x \\to 0} \\frac{\\sin(x)}{x}" },
    { name: "Limit of (1+x)^(1/x)", expr: "\\lim_{x \\to 0} (1 + x)^{1/x}" },
    { name: "Limit of (e^x-1)/x", expr: "\\lim_{x \\to 0} \\frac{e^x - 1}{x}" },
    { name: "Limit at infinity", expr: "\\lim_{x \\to \\infty} \\frac{x^2 + 1}{x^3 + 1}" },
    { name: "Limit of (x²-1)/(x-1)", expr: "\\lim_{x \\to 1} \\frac{x^2 - 1}{x - 1}" },
    { name: "Limit of ln(x)/x", expr: "\\lim_{x \\to \\infty} \\frac{\\ln(x)}{x}" },
    { name: "Limit of x^x", expr: "\\lim_{x \\to 0^+} x^x" },
    { name: "Limit of (1-cos(x))/x²", expr: "\\lim_{x \\to 0} \\frac{1 - \\cos(x)}{x^2}" },
    { name: "Limit of (x+1)^(1/x)", expr: "\\lim_{x \\to \\infty} (x + 1)^{1/x}" },
    { name: "Limit of tan(x)/x", expr: "\\lim_{x \\to 0} \\frac{\\tan(x)}{x}" }
  ],
  
  'Systems of Equations': [
    { name: "2x2 system", expr: "\\begin{cases} x + y = 5 \\\\ 2x - y = 1 \\end{cases}" },
    { name: "System with squares", expr: "\\begin{cases} x^2 + y^2 = 25 \\\\ x + y = 7 \\end{cases}" },
    { name: "3x3 system", expr: "\\begin{cases} x + 2y + z = 6 \\\\ 2x - y + z = 3 \\\\ x + y - z = 0 \\end{cases}" },
    { name: "System with parameter", expr: "\\begin{cases} x + y = a \\\\ x - y = 1 \\end{cases}" },
    { name: "System with fractions", expr: "\\begin{cases} \\frac{1}{x} + \\frac{1}{y} = 1 \\\\ x + y = 3 \\end{cases}" },
    { name: "System with logarithms", expr: "\\begin{cases} \\log(x) + \\log(y) = 2 \\\\ x + y = 10 \\end{cases}" },
    { name: "System with exponentials", expr: "\\begin{cases} e^x + e^y = 5 \\\\ e^x - e^y = 1 \\end{cases}" },
    { name: "System with trigonometry", expr: "\\begin{cases} \\sin(x) + \\cos(y) = 1 \\\\ \\cos(x) - \\sin(y) = 0 \\end{cases}" }
  ],
  
  'Matrices': [
    { name: "2x2 matrix", expr: "\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}" },
    { name: "Diagonal matrix", expr: "\\begin{pmatrix} 2 & 0 \\\\ 0 & 3 \\end{pmatrix}" },
    { name: "Identity matrix", expr: "\\begin{pmatrix} 1 & 0 & 0 \\\\ 0 & 1 & 0 \\\\ 0 & 0 & 1 \\end{pmatrix}" },
    { name: "3x3 matrix", expr: "\\begin{pmatrix} 1 & 2 & 3 \\\\ 4 & 5 & 6 \\\\ 7 & 8 & 9 \\end{pmatrix}" },
    { name: "Inverse matrix", expr: "\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}^{-1}" },
    { name: "Determinant", expr: "\\det\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}" },
    { name: "Matrix trace", expr: "\\text{tr}\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}" },
    { name: "Matrix multiplication", expr: "\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix} \\begin{pmatrix} 5 & 6 \\\\ 7 & 8 \\end{pmatrix}" }
  ],
  
  'Trigonometry': [
    { name: "Pythagorean identity", expr: "\\sin^2(x) + \\cos^2(x) = 1" },
    { name: "Double angle sine", expr: "\\sin(2x)" },
    { name: "Double angle cosine", expr: "\\cos(2x)" },
    { name: "Sum of sines", expr: "\\sin(x) + \\sin(y)" },
    { name: "Product of sines", expr: "\\sin(x) \\cdot \\sin(y)" },
    { name: "Reduction formula", expr: "\\sin(x + \\frac{\\pi}{2})" },
    { name: "Tangent of sum", expr: "\\tan(x + y)" },
    { name: "Inverse functions", expr: "\\arcsin(x) + \\arccos(x)" },
    { name: "Hyperbolic functions", expr: "\\sinh(x) + \\cosh(x)" },
    { name: "Complex numbers", expr: "e^{ix} = \\cos(x) + i\\sin(x)" }
  ],
  
  'Logarithms and Exponentials': [
    { name: "Logarithm of product", expr: "\\ln(x \\cdot y)" },
    { name: "Logarithm of quotient", expr: "\\ln\\left(\\frac{x}{y}\\right)" },
    { name: "Logarithm of power", expr: "\\ln(x^2)" },
    { name: "Exponential of sum", expr: "e^{x + y}" },
    { name: "Exponential of product", expr: "e^{2x}" },
    { name: "Logarithm of exponential", expr: "\\ln(e^x)" },
    { name: "Exponential of logarithm", expr: "e^{\\ln(x)}" },
    { name: "Base-10 logarithm", expr: "\\log_{10}(x)" },
    { name: "Base-2 logarithm", expr: "\\log_2(x)" },
    { name: "Complex exponential", expr: "e^{x^2 + 1}" }
  ],
  
  'Combinatorics': [
    { name: "Factorial", expr: "5!" },
    { name: "Combinations", expr: "C(10, 3)" },
    { name: "Permutations", expr: "P(8, 4)" },
    { name: "Binomial coefficient", expr: "\\binom{12}{5}" },
    { name: "Sum of combinations", expr: "\\sum_{k=0}^{n} \\binom{n}{k}" },
    { name: "Pascal's triangle", expr: "\\binom{n}{k} = \\binom{n-1}{k-1} + \\binom{n-1}{k}" },
    { name: "Stirling's formula", expr: "n! \\approx \\sqrt{2\\pi n} \\left(\\frac{n}{e}\\right)^n" },
    { name: "Fibonacci numbers", expr: "F_n = F_{n-1} + F_{n-2}" }
  ],
  
  'Series': [
    { name: "Geometric series", expr: "\\sum_{n=0}^{\\infty} x^n" },
    { name: "Harmonic series", expr: "\\sum_{n=1}^{\\infty} \\frac{1}{n}" },
    { name: "Taylor series for e^x", expr: "\\sum_{n=0}^{\\infty} \\frac{x^n}{n!}" },
    { name: "Taylor series for sin(x)", expr: "\\sum_{n=0}^{\\infty} \\frac{(-1)^n x^{2n+1}}{(2n+1)!}" },
    { name: "Taylor series for cos(x)", expr: "\\sum_{n=0}^{\\infty} \\frac{(-1)^n x^{2n}}{(2n)!}" },
    { name: "Taylor series for ln(1+x)", expr: "\\sum_{n=1}^{\\infty} \\frac{(-1)^{n+1} x^n}{n}" },
    { name: "General Taylor series", expr: "f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n" },
    { name: "Alternating series", expr: "\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{n}" }
  ],
  
  'Complex Numbers': [
    { name: "Square of complex number", expr: "(1 + i)^2" },
    { name: "Product of complex numbers", expr: "(2 + 3i)(1 - i)" },
    { name: "Quotient of complex numbers", expr: "\\frac{1 + i}{1 - i}" },
    { name: "Euler's formula", expr: "e^{i\\pi} = -1" },
    { name: "Modulus of complex number", expr: "|1 + i|" },
    { name: "Argument of complex number", expr: "\\arg(1 + i)" },
    { name: "Roots of unity", expr: "\\sqrt[n]{1}" },
    { name: "Complex exponential", expr: "e^{i\\theta} = \\cos(\\theta) + i\\sin(\\theta)" }
  ],
  
  'Special Functions': [
    { name: "Gamma function", expr: "\\Gamma(n)" },
    { name: "Beta function", expr: "B(m, n)" },
    { name: "Bessel function", expr: "J_0(x)" },
    { name: "Error function", expr: "\\text{erf}(x)" },
    { name: "Riemann zeta function", expr: "\\zeta(s)" },
    { name: "Elliptic integrals", expr: "K(k)" },
    { name: "Dirac delta function", expr: "\\delta(x)" },
    { name: "Heaviside step function", expr: "H(x)" }
  ],
  
  'Differential Equations': [
    { name: "Simple ODE", expr: "\\frac{dy}{dx} = x" },
    { name: "Separable ODE", expr: "\\frac{dy}{dx} = y" },
    { name: "Linear ODE", expr: "\\frac{dy}{dx} = x \\cdot y" },
    { name: "Second order ODE", expr: "\\frac{d^2y}{dx^2} = -y" },
    { name: "ODE with constant coefficients", expr: "\\frac{d^2y}{dx^2} + y = 0" },
    { name: "Nonhomogeneous ODE", expr: "\\frac{d^2y}{dx^2} + y = \\sin(x)" },
    { name: "Bernoulli equation", expr: "\\frac{dy}{dx} + y = xy^2" },
    { name: "Riccati equation", expr: "\\frac{dy}{dx} = y^2 + x^2" },
    { name: "Exact differential equation", expr: "(2xy + 1)dx + (x^2 + 2y)dy = 0" },
    { name: "Homogeneous ODE", expr: "\\frac{dy}{dx} = \\frac{x + y}{x - y}" },
    { name: "Linear first order", expr: "\\frac{dy}{dx} + 2y = e^{-x}" },
    { name: "Cauchy-Euler equation", expr: "x^2\\frac{d^2y}{dx^2} + x\\frac{dy}{dx} + y = 0" }
  ],

  'Multivariable Calculus': [
    { name: "Partial derivative", expr: "\\frac{\\partial}{\\partial x}(x^2y + xy^2)" },
    { name: "Gradient", expr: "\\nabla f(x,y) = \\frac{\\partial f}{\\partial x}\\hat{i} + \\frac{\\partial f}{\\partial y}\\hat{j}" },
    { name: "Divergence", expr: "\\nabla \\cdot \\vec{F} = \\frac{\\partial F_x}{\\partial x} + \\frac{\\partial F_y}{\\partial y}" },
    { name: "Curl", expr: "\\nabla \\times \\vec{F} = \\left(\\frac{\\partial F_z}{\\partial y} - \\frac{\\partial F_y}{\\partial z}\\right)\\hat{i} + \\left(\\frac{\\partial F_x}{\\partial z} - \\frac{\\partial F_z}{\\partial x}\\right)\\hat{j}" },
    { name: "Double integral", expr: "\\iint_D (x^2 + y^2) dA" },
    { name: "Triple integral", expr: "\\iiint_V (x^2 + y^2 + z^2) dV" },
    { name: "Line integral", expr: "\\int_C \\vec{F} \\cdot d\\vec{r}" },
    { name: "Surface integral", expr: "\\iint_S \\vec{F} \\cdot d\\vec{S}" },
    { name: "Green's theorem", expr: "\\oint_C (P dx + Q dy) = \\iint_D \\left(\\frac{\\partial Q}{\\partial x} - \\frac{\\partial P}{\\partial y}\\right) dA" },
    { name: "Stokes' theorem", expr: "\\oint_C \\vec{F} \\cdot d\\vec{r} = \\iint_S (\\nabla \\times \\vec{F}) \\cdot d\\vec{S}" },
    { name: "Divergence theorem", expr: "\\iiint_V (\\nabla \\cdot \\vec{F}) dV = \\iint_S \\vec{F} \\cdot d\\vec{S}" },
    { name: "Chain rule", expr: "\\frac{\\partial z}{\\partial t} = \\frac{\\partial z}{\\partial x}\\frac{\\partial x}{\\partial t} + \\frac{\\partial z}{\\partial y}\\frac{\\partial y}{\\partial t}" }
  ],

  'Linear Algebra': [
    { name: "Matrix multiplication", expr: "\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix} \\begin{pmatrix} 5 & 6 \\\\ 7 & 8 \\end{pmatrix}" },
    { name: "Determinant 3x3", expr: "\\det\\begin{pmatrix} 1 & 2 & 3 \\\\ 4 & 5 & 6 \\\\ 7 & 8 & 9 \\end{pmatrix}" },
    { name: "Eigenvalues", expr: "\\det(A - \\lambda I) = 0" },
    { name: "Eigenvectors", expr: "A\\vec{v} = \\lambda\\vec{v}" },
    { name: "Matrix inverse", expr: "A^{-1} = \\frac{1}{\\det(A)}\\text{adj}(A)" },
    { name: "Rank of matrix", expr: "\\text{rank}\\begin{pmatrix} 1 & 2 & 3 \\\\ 2 & 4 & 6 \\\\ 1 & 1 & 1 \\end{pmatrix}" },
    { name: "Null space", expr: "\\text{null}(A) = \\{\\vec{x} : A\\vec{x} = \\vec{0}\\}" },
    { name: "Column space", expr: "\\text{col}(A) = \\text{span}\\{\\vec{a}_1, \\vec{a}_2, \\ldots, \\vec{a}_n\\}" },
    { name: "Gram-Schmidt process", expr: "\\vec{u}_k = \\vec{v}_k - \\sum_{i=1}^{k-1} \\text{proj}_{\\vec{u}_i}\\vec{v}_k" },
    { name: "QR decomposition", expr: "A = QR" },
    { name: "LU decomposition", expr: "A = LU" },
    { name: "Singular value decomposition", expr: "A = U\\Sigma V^T" }
  ],

  'Statistics & Probability': [
    { name: "Mean", expr: "\\mu = \\frac{1}{n}\\sum_{i=1}^{n} x_i" },
    { name: "Variance", expr: "\\sigma^2 = \\frac{1}{n}\\sum_{i=1}^{n} (x_i - \\mu)^2" },
    { name: "Standard deviation", expr: "\\sigma = \\sqrt{\\frac{1}{n}\\sum_{i=1}^{n} (x_i - \\mu)^2}" },
    { name: "Normal distribution", expr: "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{1}{2}\\left(\\frac{x-\\mu}{\\sigma}\\right)^2}" },
    { name: "Binomial probability", expr: "P(X = k) = \\binom{n}{k} p^k (1-p)^{n-k}" },
    { name: "Poisson distribution", expr: "P(X = k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}" },
    { name: "Exponential distribution", expr: "f(x) = \\lambda e^{-\\lambda x}" },
    { name: "Chi-square distribution", expr: "f(x) = \\frac{1}{2^{k/2}\\Gamma(k/2)} x^{k/2-1} e^{-x/2}" },
    { name: "Central limit theorem", expr: "\\lim_{n \\to \\infty} P\\left(\\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}} \\leq z\\right) = \\Phi(z)" },
    { name: "Confidence interval", expr: "\\bar{x} \\pm z_{\\alpha/2} \\frac{\\sigma}{\\sqrt{n}}" },
    { name: "Correlation coefficient", expr: "r = \\frac{\\sum_{i=1}^{n} (x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum_{i=1}^{n} (x_i - \\bar{x})^2 \\sum_{i=1}^{n} (y_i - \\bar{y})^2}}" },
    { name: "Linear regression", expr: "y = \\beta_0 + \\beta_1 x + \\epsilon" }
  ],

  'Number Theory': [
    { name: "Greatest common divisor", expr: "\\gcd(a, b)" },
    { name: "Least common multiple", expr: "\\text{lcm}(a, b)" },
    { name: "Euclidean algorithm", expr: "\\gcd(a, b) = \\gcd(b, a \\bmod b)" },
    { name: "Prime factorization", expr: "n = p_1^{a_1} p_2^{a_2} \\cdots p_k^{a_k}" },
    { name: "Euler's totient function", expr: "\\phi(n) = n \\prod_{p|n} \\left(1 - \\frac{1}{p}\\right)" },
    { name: "Fermat's little theorem", expr: "a^{p-1} \\equiv 1 \\pmod{p}" },
    { name: "Chinese remainder theorem", expr: "x \\equiv a_i \\pmod{m_i}" },
    { name: "Quadratic reciprocity", expr: "\\left(\\frac{p}{q}\\right)\\left(\\frac{q}{p}\\right) = (-1)^{\\frac{p-1}{2}\\frac{q-1}{2}}" },
    { name: "Diophantine equation", expr: "ax + by = c" },
    { name: "Pell's equation", expr: "x^2 - dy^2 = 1" },
    { name: "Möbius function", expr: "\\mu(n) = \\begin{cases} 1 & \\text{if } n = 1 \\\\ (-1)^k & \\text{if } n \\text{ is product of } k \\text{ distinct primes} \\\\ 0 & \\text{otherwise} \\end{cases}" },
    { name: "Riemann zeta function", expr: "\\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}" }
  ],

  'Discrete Mathematics': [
    { name: "Permutation", expr: "P(n, r) = \\frac{n!}{(n-r)!}" },
    { name: "Combination", expr: "C(n, r) = \\binom{n}{r} = \\frac{n!}{r!(n-r)!}" },
    { name: "Binomial theorem", expr: "(x + y)^n = \\sum_{k=0}^{n} \\binom{n}{k} x^{n-k} y^k" },
    { name: "Pascal's triangle", expr: "\\binom{n}{k} = \\binom{n-1}{k-1} + \\binom{n-1}{k}" },
    { name: "Inclusion-exclusion principle", expr: "|A \\cup B \\cup C| = |A| + |B| + |C| - |A \\cap B| - |A \\cap C| - |B \\cap C| + |A \\cap B \\cap C|" },
    { name: "Pigeonhole principle", expr: "\\text{If } n > m \\text{, then at least one pigeonhole contains more than one pigeon}" },
    { name: "Graph theory - degree", expr: "\\sum_{v \\in V} \\deg(v) = 2|E|" },
    { name: "Euler's formula", expr: "V - E + F = 2" },
    { name: "Hamiltonian path", expr: "\\text{Path visiting each vertex exactly once}" },
    { name: "Eulerian path", expr: "\\text{Path using each edge exactly once}" },
    { name: "Recurrence relation", expr: "a_n = c_1 a_{n-1} + c_2 a_{n-2} + \\cdots + c_k a_{n-k}" },
    { name: "Generating function", expr: "G(x) = \\sum_{n=0}^{\\infty} a_n x^n" }
  ],

  'Advanced Calculus': [
    { name: "Taylor series", expr: "f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n" },
    { name: "Maclaurin series", expr: "f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(0)}{n!}x^n" },
    { name: "Fourier series", expr: "f(x) = \\frac{a_0}{2} + \\sum_{n=1}^{\\infty} (a_n \\cos(nx) + b_n \\sin(nx))" },
    { name: "Laplace transform", expr: "\\mathcal{L}\\{f(t)\\} = \\int_0^{\\infty} e^{-st} f(t) dt" },
    { name: "Inverse Laplace transform", expr: "\\mathcal{L}^{-1}\\{F(s)\\} = f(t)" },
    { name: "Fourier transform", expr: "\\mathcal{F}\\{f(x)\\} = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i \\xi x} dx" },
    { name: "Convolution", expr: "(f * g)(t) = \\int_{-\\infty}^{\\infty} f(\\tau) g(t-\\tau) d\\tau" },
    { name: "Parseval's theorem", expr: "\\int_{-\\infty}^{\\infty} |f(x)|^2 dx = \\int_{-\\infty}^{\\infty} |\\hat{f}(\\xi)|^2 d\\xi" },
    { name: "Cauchy integral formula", expr: "f(a) = \\frac{1}{2\\pi i} \\oint_C \\frac{f(z)}{z-a} dz" },
    { name: "Residue theorem", expr: "\\oint_C f(z) dz = 2\\pi i \\sum \\text{Res}(f, z_k)" },
    { name: "Maximum modulus principle", expr: "|f(z)| \\leq \\max_{z \\in \\partial D} |f(z)|" },
    { name: "Schwarz lemma", expr: "|f(z)| \\leq |z| \\text{ for } |z| < 1" }
  ],

  'Optimization': [
    { name: "Lagrange multipliers", expr: "\\nabla f = \\lambda \\nabla g" },
    { name: "Kuhn-Tucker conditions", expr: "\\nabla f + \\sum_{i=1}^{m} \\lambda_i \\nabla g_i + \\sum_{j=1}^{p} \\mu_j \\nabla h_j = 0" },
    { name: "Linear programming", expr: "\\min c^T x \\text{ subject to } Ax \\leq b, x \\geq 0" },
    { name: "Quadratic programming", expr: "\\min \\frac{1}{2} x^T Q x + c^T x \\text{ subject to } Ax \\leq b" },
    { name: "Simplex method", expr: "\\text{Maximize } z = c^T x \\text{ subject to } Ax = b, x \\geq 0" },
    { name: "Dual problem", expr: "\\max b^T y \\text{ subject to } A^T y \\leq c" },
    { name: "Gradient descent", expr: "x_{k+1} = x_k - \\alpha \\nabla f(x_k)" },
    { name: "Newton's method", expr: "x_{k+1} = x_k - \\frac{f(x_k)}{f'(x_k)}" },
    { name: "Conjugate gradient", expr: "x_{k+1} = x_k + \\alpha_k p_k" },
    { name: "BFGS method", expr: "B_{k+1} = B_k + \\frac{y_k y_k^T}{y_k^T s_k} - \\frac{B_k s_k s_k^T B_k}{s_k^T B_k s_k}" },
    { name: "Interior point method", expr: "\\min f(x) - \\mu \\sum_{i=1}^{m} \\log(-g_i(x))" },
    { name: "Branch and bound", expr: "\\text{Solve } \\min_{x \\in X} f(x) \\text{ where } X \\text{ is discrete}" }
  ],

  'Geometry & Topology': [
    { name: "Distance formula", expr: "d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}" },
    { name: "Circle equation", expr: "(x-h)^2 + (y-k)^2 = r^2" },
    { name: "Ellipse equation", expr: "\\frac{(x-h)^2}{a^2} + \\frac{(y-k)^2}{b^2} = 1" },
    { name: "Hyperbola equation", expr: "\\frac{(x-h)^2}{a^2} - \\frac{(y-k)^2}{b^2} = 1" },
    { name: "Parabola equation", expr: "y = ax^2 + bx + c" },
    { name: "Sphere equation", expr: "(x-h)^2 + (y-k)^2 + (z-l)^2 = r^2" },
    { name: "Plane equation", expr: "ax + by + cz + d = 0" },
    { name: "Cross product", expr: "\\vec{a} \\times \\vec{b} = \\begin{vmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ a_1 & a_2 & a_3 \\\\ b_1 & b_2 & b_3 \\end{vmatrix}" },
    { name: "Dot product", expr: "\\vec{a} \\cdot \\vec{b} = |\\vec{a}||\\vec{b}|\\cos\\theta" },
    { name: "Vector projection", expr: "\\text{proj}_{\\vec{b}}\\vec{a} = \\frac{\\vec{a} \\cdot \\vec{b}}{|\\vec{b}|^2}\\vec{b}" },
    { name: "Gauss-Bonnet theorem", expr: "\\int_M K dA + \\int_{\\partial M} k_g ds = 2\\pi \\chi(M)" },
    { name: "Euler characteristic", expr: "\\chi = V - E + F" }
  ],

  'Physics Applications': [
    { name: "Newton's second law", expr: "F = ma" },
    { name: "Kinetic energy", expr: "K = \\frac{1}{2}mv^2" },
    { name: "Potential energy", expr: "U = mgh" },
    { name: "Work-energy theorem", expr: "W = \\Delta K" },
    { name: "Momentum", expr: "p = mv" },
    { name: "Angular momentum", expr: "L = r \\times p" },
    { name: "Torque", expr: "\\tau = r \\times F" },
    { name: "Simple harmonic motion", expr: "x(t) = A\\cos(\\omega t + \\phi)" },
    { name: "Wave equation", expr: "\\frac{\\partial^2 u}{\\partial t^2} = c^2 \\frac{\\partial^2 u}{\\partial x^2}" },
    { name: "Schrödinger equation", expr: "i\\hbar\\frac{\\partial\\psi}{\\partial t} = \\hat{H}\\psi" },
    { name: "Maxwell's equations", expr: "\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\epsilon_0}, \\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}" },
    { name: "Einstein's mass-energy", expr: "E = mc^2" }
  ]
};


export function getRandomExample(category) {
  const examples = exampleCategories[category];
  if (!examples || examples.length === 0) return null;
  return examples[Math.floor(Math.random() * examples.length)];
}


export function getRandomExampleFromAny() {
  const allCategories = Object.keys(exampleCategories);
  const randomCategory = allCategories[Math.floor(Math.random() * allCategories.length)];
  return getRandomExample(randomCategory);
}


export function getCategories() {
  return Object.keys(exampleCategories);
}


export function getExamplesForCategory(category) {
  return exampleCategories[category] || [];
}



