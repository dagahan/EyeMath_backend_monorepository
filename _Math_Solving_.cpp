#include <iostream>
#include <C:\Users\dagahan\Desktop\MathLib\_Math_Lib_.h>

using namespace MathLib;
using namespace std;


int main() {
    using namespace MathLib;
    MATH_LIB_INIT_();

    const mpf_class π("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068");
    const mpf_class e("2.718281828459045235360287471352662497757247093699959574966967627724076630353547594571382178525166427");
    const mpf_class φ("1.618033988749894848204586834365638117720309179805762862135448622705260462818902449707207204189391137");

    //cout << "π is: " << π << endl;

    //Fraction A("0", "210.205", "1");
    //Fraction B("0", "-1542.512", "1");

    Fraction A("0", "2", "1");
    Fraction B("0", "-1", "625");

    //B.reduce();

    //cout << module(B).getLaTeX() << endl;
    //cout << "2/1 multiply by -1/625 is: " << multiply(A, B).getLaTeX() << endl;
    //cout << "5 powered by -4 is: " << power(single_fraction("5"), single_fraction("-4")).getLaTeX() << endl;

    //vector<mpf_class> massive = { mpf_class("18.0"), mpf_class("6.0") , mpf_class("12.0")};
    //cout << "GCD of massive: " << gcd_many(massive) << endl;

    //cout << "Quadratic equation: " << quadratic_equation(single_fraction("2"), single_fraction("-1"), single_fraction("-5")).getLaTeX() << endl;


    //string latex = R"(sum_{i=1}^N i = \frac{n(n+1)}{2})";
    //LaTeXtoPNG(latex, "formula.png");


    string latex_expr = "2 + \\frac{-1}{625}";
    Fraction result = calculate_latex(latex_expr);
    cout << "Result: " << result.getLaTeX() << endl;

    string expr1 = "\\frac{3}{4} * \\frac{5}{9}";
    Fraction res1 = calculate_latex(expr1);
    cout << "Result: " << res1.getLaTeX() << endl;

    string expr2 = "\\5 * \\10";
    Fraction res2 = calculate_latex(expr2);
    cout << "Result: " << res2.getLaTeX() << endl;

    // string expr3 = "\\frac{12345}{67890} + \\frac{98765}{43210} * \\frac{5555}{6666} - \\frac{1000}{7}";
    // Fraction res3 = calculate_latex(expr3);
    // cout << "Result 3: " << res3.getLaTeX() << endl;
    // // Ожидаемый результат: -\frac{18621252587}{180319548} ≈ -103.2

    // string expr4 = "0 - \\frac{-0}{5} + \\frac{3}{-7} * 0";
    // Fraction res4 = calculate_latex(expr4);
    // cout << "Result 4: " << res4.getLaTeX() << endl;
    // // Вывод: 0

    // string expr5 = "\\frac{\\frac{2}{3} + \\frac{4}{5}}{\\frac{1}{2} - \\frac{1}{10}}";
    // Fraction res5 = calculate_latex(expr5);
    // cout << "Result 5: " << res5.getLaTeX() << endl;
    // Ожидаемый результат: \frac{22}{15} / \frac{2}{5} = \frac{11}{3}

    return 0;
}