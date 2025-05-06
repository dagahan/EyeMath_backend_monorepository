#include <iostream>
#include <C:\Users\dagahan\Desktop\MathLib\_Math_Lib_.h>

using namespace MathLib;
using namespace std;


Fraction Solve(string N) {
    return single_fraction(N);
}



int main() {
    using namespace MathLib;
    MATH_LIB_INIT_();

    const mpf_class π("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068");
    const mpf_class e("2.718281828459045235360287471352662497757247093699959574966967627724076630353547594571382178525166427");
    const mpf_class φ("1.618033988749894848204586834365638117720309179805762862135448622705260462818902449707207204189391137");

    //cout << "π is: " << π << endl;

    Fraction A("0", "210.205", "1");
    Fraction B("0", "-1542.512", "1");

    //B.reduce();

    //cout << module(B).getLaTeX() << endl;
    //cout << "210.205 multiply by -1542.512 is: " << multiply(A, B).getLaTeX() << endl;
    //cout << "5 powered by -4 is: " << power(single_fraction("5"), single_fraction("-4")).getLaTeX() << endl;

    vector<mpf_class> massive = { mpf_class("18.0"), mpf_class("6.0") , mpf_class("12.0")};
    //cout << "GCD of massive: " << gcd_many(massive) << endl;

    //cout << "Quadratic equation: " << quadratic_equation(single_fraction("2"), single_fraction("-1"), single_fraction("-5")).getLaTeX() << endl;


    string latex = R"(sum_{i=1}^N i = \frac{n(n+1)}{2})";
    LaTeXtoPNG(latex, "formula.png");


    string N = "2 * 4";
    cout << Solve(N).getLaTeX() << endl;

    return 0;
}