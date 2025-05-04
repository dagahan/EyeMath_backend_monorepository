#include <iostream>
#include <vector>
#include <gmpxx.h>
#include <iomanip>
#include <limits>
#include <cmath>
#include <windows.h>
#include <string>

using namespace std;



template <typename T>
T module(const T& A) {
    //условие ? если_истина : если_ложь;
    return (A < 0) ? -A : A;
}


mpf_class multiply(const mpf_class& A, const mpf_class& B) {
    if (A == 0 || B == 0) return 0;
    if (A == 1 || B == 1) return (A == 1 ? B : A);
    if (A == -1 || B == -1) return (A == -1 ? -B : -A);

    //Вытаскиваю мантиссу и экспоненту у A и B.
    mp_exp_t expA, expB;
    string mantissaA = module(A).get_str(expA, 10);
    string mantissaB = module(B).get_str(expB, 10);

    //Считаю сумму символов A и B после запятой.
    mpz_class mA(mantissaA), mB(mantissaB), mantissaC = 0;
    int totalFrac = ((int)mantissaA.size() - expA) + ((int)mantissaB.size() - expB);

    //Складываю мантиссу A саму с собой мантисса B раз.
    for (mpz_class i = 0; i < mB; ++i){
        mantissaC += mA;
    }
     
    //Получаю строку результата-мантиссы и дозаполняю нулями в конце, если нужно, поскольку GMPxx хавает нули int на конце при конвертировании.
    string stringC = mantissaC.get_str();
    if ((int)stringC.size() <= totalFrac)
        stringC.insert(0, totalFrac + 1 - stringC.size(), '0');

    //Вставляю точку, отсчитав справа налево totalFrac символов.
    stringC.insert(stringC.size() - totalFrac, ".");

    //Собираю обратно mpf_class и устанавливаю знак.
    mpf_class C(stringC);
    if ((A < 0 && B > 0) || (A > 0 && B < 0)) {
        C = -C;
    }
    return C;
}




class Fraction {
private:
    string numerator;
    string denominator;

public:
    Fraction(string num, string denom) {
        mpf_class denom_f(denom);
        if (denom_f == 0) {
            //throw invalid_argument("Denominator cannot be zero.");
        }
        numerator = num;
        denominator = denom;
    }

    string getNumerator() const {
        return numerator;
    }

    string getDenominator() const {
        return denominator;
    }
};




mpf_class powerby(const mpf_class& base, const mpf_class& exponent) {
    if (exponent == 0) return 1;
    if (exponent == 1) return base;

    mpf_class C = 1;
    mpf_class count = module(exponent);

    for (mpf_class i = 0; i < count; i++) {
        C = multiply(C, base);
    }

    if (exponent < 0) {
        return Fraction(1, C.get_d()); // Возвращаем дробь 1/C, если степень отрицательная
    }
    return module(C);
}





mpf_class NOD_for_two(const mpf_class& a, const mpf_class& b) {
    mpf_class x = a, y = b;

    while (y != 0) {
        mpf_class temp = y;
        mpf_class mod = fmod(x.get_d(), y.get_d()); // через double
        y = mod;
        x = temp;
    }

    return x;
}

mpf_class NOD_many(const vector<mpf_class>& massive) {
    if (massive.empty()) return 0;

    mpf_class result = massive[0];
    for (size_t i = 1; i < massive.size(); ++i) {
        result = NOD_for_two(result, massive[i]);
        if (result == 0) break;
    }
    return result;
}



mpf_class Discriminant(const mpf_class& A, const mpf_class& B, const mpf_class& C){
    mpf_class Discriminant = powerby(B, 2) - multiply(multiply(4, A), C);
    return Discriminant;
}

mpf_class quadratic_equation(const mpf_class& A, const mpf_class& B, const mpf_class& C) {
    mpf_class D = Discriminant(A, B, C);
    return D;
}


int main() {
    mpf_set_default_prec(4096);
    cout << std::setprecision(1000);
    SetConsoleOutputCP(CP_UTF8);
    //cout << std::fixed; //чтобы показывать всю-всю дробную часть всегда (со всеми нулями)

    const mpf_class π("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068");
    const mpf_class e("2.718281828459045235360287471352662497757247093699959574966967627724076630353547594571382178525166427");
    const mpf_class φ("1.618033988749894848204586834365638117720309179805762862135448622705260462818902449707207204189391137");

    //cout << "π is: " << π << endl;

    cout << "210.205 multiply by -1542.512 is: " << multiply(mpf_class("210.205"), mpf_class("-1542.512")) << endl;
    cout << "5 powered by -4 is: " << powerby(mpf_class("-5"), mpf_class("-4")) << endl;

    vector<mpf_class> massive = { mpf_class("18.0"), mpf_class("6.0") , mpf_class("12.0")};
    cout << "GCD of massive: " << NOD_many(massive) << endl;

    cout << "Quadratic equation: " << quadratic_equation(mpf_class("2"), mpf_class("-1"), mpf_class("-5")) << endl;

    return 0;
}