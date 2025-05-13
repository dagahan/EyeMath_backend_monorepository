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


    //string latex = R"(sum_{i=1}^N i = \frac{n(n+1)}{2})";
    //LaTeXtoPNG(latex, "formula.png");

    string latex_expr = "(\\frac{12345}{67890} + \\frac{98765}{43210} * \\frac{5555}{6666} - \\frac{1000}{7} + 139.112234243253453495903405439583489) * 2";
    cout << solveLaTeX(latex_expr) << endl;
    

    //string latex_expr = "2 + \\frac{-1}{625}";
    //string expr2 = "\\5 * \\10";
    // string expr3 = "\\frac{12345}{67890} + \\frac{98765}{43210} * \\frac{5555}{6666} - \\frac{1000}{7}";
    // string expr4 = "0 - \\frac{-0}{5} + \\frac{3}{-7} * 0";
    // string expr5 = "\\frac{\\frac{2}{3} + \\frac{4}{5}}{\\frac{1}{2} - \\frac{1}{10}}";
    return 0;
}