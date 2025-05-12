/******************************************************************************
 *                              _Math_Lib_.h                                 *
 *                                                                            *
 *  Project: EyeMath                                                         *
 *  File: _Math_Lib_.h                                                        *
 *  Author: Usov Nikita                                                      *
 *  Created: April 23, 2025                                                  *
 *  Last Modified: May 05, 2025                                              *
 *                                                                            *
 *  Description:                                                             *
 *  This is the Mathimatician Library with many of functions for EyeMath     *
 *  Project. Here's some funtions how multiply, power, Generate LaTeX and  *
 *  simpy recognize LaTeX code from PNG image.                               * 
 *                                                                            *
 ******************************************************************************/

#include <iostream>
#include <vector>
#include <C:\Users\dagahan\Desktop\MathLib\libraries\GMP\include\gmpxx.h> //FIXME: путь к библиотеке нужно сделать относительным, а не абсолютным.
#include <cstdlib>
#include <cstdio>
#include <filesystem>
#include <iomanip>
#include <cmath>
#include <string>
#include <sstream>
#include <fstream>
#include <typeinfo>
#include <algorithm>
#include <regex>

// new libs for DeepSeek http requests and JSON parsing
#include <C:\Users\dagahan\Desktop\MathLib\libraries\curl\include\curl\curl.h>
#include <C:\Users\dagahan\Desktop\MathLib\libraries\nlohmann\json.hpp>


// Define the namespace for convenience.
using namespace std;
using json = nlohmann::json;
namespace fs = std::filesystem;



namespace MathLib {
    constexpr int __PRECISION__ = 32;
    constexpr int __DEFAULT__PREC__ = 48;
    class Fraction; // Forward declaration of the Fraction class.

    string mpf_to_string(const mpf_class num, int precision = __PRECISION__) {
        std::ostringstream oss;
        oss << std::fixed
            << std::setprecision(precision)
            << num;
        return oss.str();
    }

    mpf_class string_to_mpf(const string str) {
        mpf_class result;
        std::istringstream iss(str);
        iss >> result;
        return result;
    }

    // getLaTeX() function using this to erase nulls.
    string removeTrailingZeros(const string& number) {
        //1. Проверяю, не пустая ли строка.
        if (number.empty()) return "0";
        string result = number;

        //2. Ищу, где находится точка.
        size_t dotPos = result.find('.');
        
        if (dotPos != string::npos) {
            // Удаление нулей после точки
            size_t lastNonZero = result.find_last_not_of('0');
            if (lastNonZero != string::npos && lastNonZero >= dotPos) {
                result.erase(lastNonZero + 1);
            }
            // Удаление точки, если она осталась последней
            if (result.back() == '.') result.pop_back();
        }
        // Обработка "-0" и пустой строки
        if (result == "-0" || result.empty()) result = "0";
        return result;
    }

    template <typename T>
    T module(const T A) {
        if constexpr (!std::is_same_v<T, Fraction>) {
            if constexpr (std::is_same_v<T, string>) {
                mpf_class B = string_to_mpf(A);
                return (B < 0) ? mpf_to_string(-B) : A;
            }
            else {
                //условие ? если_истина : если_ложь;
                return (A < 0) ? -A : A;
            }
        }
        else{
            return Fraction(mpf_to_string(module(string_to_mpf(A.getWhole()))),
            mpf_to_string(module(string_to_mpf(A.getNumerator()))),
            mpf_to_string(module(string_to_mpf(A.getDenominator()))));
        }
    }

    mpf_class gcd_for_two(mpf_class a, mpf_class b) {
        a = module(a);
        b = module(b);
        while (b != 0) {
            mpf_class temp = b;
            b = a - b * floor(a / b);
            a = temp;
        }
        return a;
    }

    template <typename T>
    T gcd_many(const std::vector<T> values) {
        if (values.empty()) return 0;

        T result = values[0];
        for (size_t i = 1; i < values.size(); ++i) {
            result = gcd_for_two(result, values[i]);
            if (result == 0) break;
        }
        return result;
    }


    class Fraction {
        private:
            //whole part
            string whole;
            //fractional part
            string numerator; //числитель
            string denominator; //знаменатель
        public:
            Fraction(string _whole, string _num, string _denom) {
                mpf_class denom_f(_denom);
                if (denom_f == 0) {
                    throw invalid_argument("Denominator cannot be zero.");
                }
                whole = _whole;
                numerator = _num;
                denominator = _denom;
                //reduce();
                //extractWholePart();
            }

            string getWhole() const { return whole; }
            string getNumerator() const { return numerator; }
            string getDenominator() const { return denominator; }

            bool isPositive() const {
                if (string_to_mpf(numerator) >= 0 && string_to_mpf(denominator) >= 0 && string_to_mpf(whole) >= 0) {
                    return  true;
                } return false;
            }
        
            string getLaTeX() const {
                //1. Очищаю лишние нули у числителя, знаменателя, целой части.
                string clean_whole = removeTrailingZeros(whole);
                string clean_num = removeTrailingZeros(numerator);
                string clean_denom = removeTrailingZeros(denominator);

                // cout << "DEBUG: clean_whole=" << clean_whole 
                // << ", clean_num=" << clean_num 
                // << ", clean_denom=" << clean_denom << endl;
                
                //2. Если, дробь - целое число (знаменатель 1), то выводится сумма "дробной" целой части + целая часть.
                if (clean_denom == "1") {
                    mpf_class total = string_to_mpf(clean_whole) + string_to_mpf(clean_num);
                    string total_str = removeTrailingZeros(mpf_to_string(total));
                    return total_str;
                }

                //3. Собираю LaTeX строчку на return.
                string latex;
                if (clean_whole != "0" && clean_whole != "") {
                    latex = clean_whole + "\\frac{" + clean_num + "}{" + clean_denom + "}";
                } else {
                    latex = "\\frac{" + clean_num + "}{" + clean_denom + "}";
                }
                return latex;
            }

            void reduce() { 
                mpf_class num(numerator);
                mpf_class denom(denominator);

                mpf_class gcd = gcd_for_two(num, denom);
                if (gcd != 0) {
                    num /= gcd;
                    denom /= gcd;
                }

                numerator = mpf_to_string(num);
                denominator = mpf_to_string(denom);
            }

            void extractWholePart() {
                mpf_class num(numerator);
                mpf_class denom(denominator);
            
                mpf_class w = floor(num / denom);             // Берём целую часть (округлённую вниз)
                mpf_class rem = num - w * denom;              // Остаток — это новая дробная часть
            
                whole = mpf_to_string(w);                     // Целую часть в строку
                numerator = mpf_to_string(rem);               // Остаток (числитель)
            }
            
            void toImproper() {
                mpf_class w(whole);
                mpf_class num(numerator);
                mpf_class denom(denominator);
            
                mpf_class new_num = w * denom + num;
                numerator = mpf_to_string(new_num); 
                whole = "0";
            }
        };
        Fraction single_fraction(const std::string numerator) {
        return Fraction("0", numerator, "1");
    }


    mpf_class multiply_mpf(const mpf_class A, const mpf_class B) {
        //1. Решение тривиальных случаев.
        if (A == 0 || B == 0) return 0;
        if (A == 1 || B == 1) return (A == 1 ? B : A);
        if (A == -1 || B == -1) return (A == -1 ? -B : -A);

        //2. Вытаскиваю мантиссу и экспоненту у A и B.
        mp_exp_t expA, expB;
        string mantissaA = module(A).get_str(expA, 10);
        string mantissaB = module(B).get_str(expB, 10);

        //3. Считаю сумму символов A и B после запятой.
        mpz_class mA(mantissaA), mB(mantissaB), mantissaC = 0;
        int totalFrac = ((int)mantissaA.size() - expA) + ((int)mantissaB.size() - expB);

        //4. Складываю мантиссу A саму с собой мантисса B раз.
        for (mpz_class i = 0; i < mB; ++i){
            mantissaC += mA;
        }
        
        //5. Получаю строку результата-мантиссы и дозаполняю нулями в конце, если нужно, поскольку GMPxx хавает нули int на конце при конвертировании.
        string stringC = mantissaC.get_str();
        if ((int)stringC.size() <= totalFrac)
            stringC.insert(0, totalFrac + 1 - stringC.size(), '0');

        //6. Вставляю точку, отсчитав справа налево totalFrac символов.
        stringC.insert(stringC.size() - totalFrac, ".");

        //7. Собираю обратно mpf_class и устанавливаю знак.
        mpf_class C(stringC);
        if ((A < 0 && B > 0) || (A > 0 && B < 0)) {
            C = -C;
        }
        return C;
    }

    Fraction multiply(Fraction A, Fraction B) {
        //1. Перевожу A и B в неправильные дроби соответственно (если есть целая часть - она прибавляется к дробному значению полностью).
        A.toImproper(), B.toImproper();

        //2. Решение тривиальных случаев.
        if (A.getNumerator() == "1" && A.getDenominator() == "1") return B;
        if (B.getNumerator() == "1" && B.getDenominator() == "1") return A;
        if (A.getNumerator() == "-1" && A.getDenominator() == "1")
            return Fraction("0", "-" + B.getNumerator(), B.getDenominator());
        if (B.getNumerator() == "-1" && B.getDenominator() == "1")
            return Fraction("0", "-" + A.getNumerator(), A.getDenominator());

        //3. Умножаю числитель A на B, знаменатель A на B, используя функцию для умножения mpf_class.
        mpf_class numC = multiply_mpf(string_to_mpf(A.getNumerator()), string_to_mpf(B.getNumerator()));
        mpf_class denomC = multiply_mpf(string_to_mpf(A.getDenominator()), string_to_mpf(B.getDenominator()));

        //4. Собираю Fraction.
        Fraction C = Fraction("0", mpf_to_string(numC), mpf_to_string(denomC));
        //5. Сокращаю дробь, выделяю целую часть.
        C.reduce();
        C.extractWholePart();
        return C;
    }

    Fraction power(Fraction base, Fraction exponent) {
        //FIXME: Функция power работает только с целыми числами:/
        //1. Перевожу base и exponent в неправильные дроби соответственно (если есть целая часть - она прибавляется к дробному значению полностью).
        base.toImproper(), exponent.toImproper();

        //2. Достаю числитель из экспоненты и перевожу его в mpf_class для дальнейших вычислений.
        mpf_class exponent_f(exponent.getNumerator());

        //3. Проверяю на тривиальные случаи:
        if (exponent_f == 0) return Fraction("0", "1", "1");
        if (exponent_f == 1) return base;
        if (exponent_f == -1) return Fraction("0", "1", base.getNumerator());

        //4. Обьявляю "технические" переменные для хранения промежуточных результатов.
        Fraction C = base;
        mpf_class count = module(exponent_f);

        //5. A^B = (A * A) B раз.
        Fraction current = base;
        for (mpf_class i = 1; i < count; i++) {
            C = multiply(C, base);
        }

        //6. Проверяю на отрицательную степень, если да, то возвращаю дробь 1/C.
        if (exponent_f > 0) {
            return Fraction("0", module(C.getNumerator()), "1");
        } return Fraction("0", "1", module(C.getNumerator()));
    }






    // TODO: max(), min(), round(), ceil(), floor(), trunc(), isgreater(), isgreaterequal(),  isless(), islessequal(), islessgreater(), iszero(), ispositive(), isnegative(), INFINITY 

    // TODO: Mathpix.com подключить распознавание в LaTeX.

    // TODO: Перевести все функции на Fraction class.
    // TODO: Побитовое сложение и вычитание.
    // TODO: Корень из числа, иррациональная степень.







    Fraction Discriminant(Fraction A, Fraction B, Fraction C) {
        Fraction four = single_fraction("4");
        Fraction B_squared = power(B, single_fraction("2")); // B^2
        Fraction fourAC = multiply(multiply(four, A), C);      // 4AC
        return single_fraction(mpf_to_string(string_to_mpf(B_squared.getNumerator()) - string_to_mpf(fourAC.getNumerator())));
    }

    Fraction quadratic_equation(Fraction A, Fraction B, Fraction C) {
        Fraction D = Discriminant(A, B, C);
        return D;
    }

    bool LaTeXtoPNG(const std::string& latexCode, const std::string& outputFileName, int dpi = 800) {
        namespace fs = std::filesystem;

        // 1. Определяем пути
        fs::path currentDir = fs::current_path();
        fs::path output_dir = currentDir / "renderLaTeX" / outputFileName;
        fs::path temp_dir = currentDir / "temp_files";
        fs::path texFile = temp_dir / "temp.tex";
        fs::path dviFile = temp_dir / "temp.dvi";
        fs::path logFile = temp_dir / "temp.log";
        fs::path auxFile = temp_dir / "temp.aux";

        // 2. Пути к бинарникам
        #ifdef _WIN32
            fs::path latexPath = currentDir / "libraries" / "MikTeX" / "miktex" / "bin" / "x64" / "latex.exe";
            fs::path dvipngPath = currentDir / "libraries" / "MikTeX" / "miktex" / "bin" / "x64" / "dvipng.exe";
        #else
            fs::path latexPath = currentDir / "libraries" / "TeXLive" / "bin" / "x86_64-linux" / "latex";
            fs::path dvipngPath = currentDir / "libraries" / "TeXLive" / "bin" / "x86_64-linux" / "dvipng";
        #endif

        // 3. Проверка существования бинарников
        if (!fs::exists(latexPath)) {
            std::cerr << "Error: latex not found at " << latexPath << std::endl;
            return false;
        }
        if (!fs::exists(dvipngPath)) {
            std::cerr << "Error: dvipng not found at " << dvipngPath << std::endl;
            return false;
        }

        // 4. Создаем папки
        fs::create_directories(temp_dir);
        fs::create_directories(output_dir.parent_path());

        // 5. Генерация TeX-файла
        {
            std::ofstream f(texFile);
            if (!f) {
                std::cerr << "Error: Failed to create " << texFile << std::endl;
                return false;
            }
            f << "\\documentclass[border=20pt]{standalone}\n"
                 "\\usepackage{amsmath}\n" // Добавлен обязательный пакет
                 "\\begin{document}\n"
                 "\\thispagestyle{empty}\n"
                 "$\\displaystyle " << latexCode << "$\n"
                 "\\end{document}\n";
        }

        // 6. Компиляция LaTeX
        std::string cmd_dvi = "\"" + latexPath.string() + "\" -interaction=nonstopmode -halt-on-error -output-directory=\"" + temp_dir.string() + "\" \"" + texFile.string() + "\"";
        #ifdef _WIN32
            cmd_dvi += " >nul 2>&1";
        #else
            cmd_dvi += " >/dev/null 2>&1";
        #endif

        int compileResult = std::system(cmd_dvi.c_str());
        if (compileResult != 0) {
            std::cerr << "LaTeX compilation failed. Exit code: " << compileResult << std::endl;
            if (fs::exists(logFile)) {
                std::cerr << "--- Log File Content ---\n";
                std::cerr << std::ifstream(logFile).rdbuf() << "\n--- End Log ---\n";
            }
            return false;
        }

        // 7. Конвертация в PNG
        std::string cmd_png = "\"" + dvipngPath.string() + "\" -T tight -D " + std::to_string(dpi) + " -o \"" + output_dir.string() + "\" \"" + dviFile.string() + "\"";
        #ifdef _WIN32
            cmd_png += " >nul 2>&1";
        #else
            cmd_png += " >/dev/null 2>&1";
        #endif

        if (std::system(cmd_png.c_str()) != 0) {
            std::cerr << "dvipng conversion failed." << std::endl;
            return false;
        }

        // 8. Удаление временных файлов
        for (const auto& file : {texFile, dviFile, logFile, auxFile}) {
            try {
                if (fs::exists(file)) fs::remove(file);
            } catch (...) {
                // Игнорируем ошибки удаления
            }
        }
        return true;
    }

    bool LaTeXtoPNG_LAGACY(const string& latexCode, const string& outputFileName, int dpi = 800) {
        //FIXME: Функция работает через консоль, а значит, нужно, чтобы в системе был установлен LaTeX (MikTeX).
        //Во-вторых, нужно, чтобы в системе был установлен dvipng (обычно он идёт в комплекте с LaTeX дистрибутивами).
        //В-третьих, картинка, что рендерит функция на выходе получается с ОЧЕНЬ МАЛЕНЬКИМИ рамками, буквально
        //в притык, значит, в самом интерфейсе EyeMath нужно будет делать искуственные увеличенные рамки для каждого вывода подобной картинки.

        const string output_dir = "renderLaTeX\\" + outputFileName;
        const string temp_dir = "temp_files\\";
        const string texFile = temp_dir + "temp.tex";
        const string dviFile = temp_dir + "temp.dvi";
        const string logFile = temp_dir + "temp.log";
        const string auxFile = temp_dir + "temp.aux";

        //1. Создаю temp.tex (временный файл с LaTeX кодом).
        {
            ofstream f(texFile);
            if (!f) return false;
            f << "\\documentclass{standalone}\n"
                "\\usepackage{amsmath}\n"
                "\\begin{document}\n"
                "$\\displaystyle " << latexCode << "$\n"
                "\\end{document}\n";
        }

        //2. Компиляция LaTeX в dvi.
        string cmd_dvi = "latex -interaction=nonstopmode -halt-on-error -output-directory=" + temp_dir + " \"" + texFile + "\" >nul 2>&1";
        if (system(cmd_dvi.c_str()) != 0) return false;

        //3. Конвертация dvi в png.
        string cmd_png = "dvipng -T tight -D " + to_string(dpi) + " -o \"" + output_dir + "\" \"" + dviFile + "\" >nul 2>&1";
        if (system(cmd_png.c_str()) != 0) return false;

        //4. Удаление временных файлов.
        remove(texFile.c_str());
        remove(dviFile.c_str());
        remove(logFile.c_str());
        remove(auxFile.c_str());
        return true;
    }


    bool PNGtoLaTeX(const string& pngFileName, const string& outputFileName) {
        return true;\
    }


    vector<string> tokenize_latex(const string& latex) {
        vector<string> tokens;
        regex re(R"(\\frac\{(-?\d+\.?\d*)\}\{(-?\d+\.?\d*)\}|(-?\d+\.?\d*)|([+\-*/]))");
        smatch match;
        string s = latex;
    
        while (regex_search(s, match, re)) {
            if (match[1].matched) { // Дробь
                string num = match[1].str();
                string den = match[2].str();
                tokens.push_back("frac{" + num + "}{" + den + "}");
            } else if (match[3].matched) { // Число
                tokens.push_back(match[3].str());
            } else if (match[4].matched) { // Оператор
                tokens.push_back(match[4].str());
            }
            s = match.suffix().str();
        }
    
        return tokens;
    }
    
    Fraction parse_fraction(const string& token) {
        if (token.find("frac{") == 0) {
            size_t num_start = 5;
            size_t num_end = token.find('}', num_start);
            string numerator = token.substr(num_start, num_end - num_start);
            size_t den_start = num_end + 2;
            size_t den_end = token.find('}', den_start);
            string denominator = token.substr(den_start, den_end - den_start);
            return Fraction("0", numerator, denominator);
        } else {
            return single_fraction(token);
        }
    }
    
    Fraction add(const Fraction A, const Fraction B) {
        Fraction a = A, b = B;
        a.toImproper(), b.toImproper();
    
        mpf_class denomA = string_to_mpf(a.getDenominator());
        mpf_class denomB = string_to_mpf(b.getDenominator());
        mpf_class commonDenom = multiply_mpf(denomA, denomB);
    
        mpf_class numA = string_to_mpf(a.getNumerator()) * denomB;
        mpf_class numB = string_to_mpf(b.getNumerator()) * denomA;
    
        mpf_class totalNum = numA + numB;
    
        Fraction result("0", mpf_to_string(totalNum), mpf_to_string(commonDenom));
        result.reduce();
        result.extractWholePart();
        return result;
    }
    
    Fraction subtract(const Fraction A, const Fraction B) {
        Fraction a = A, b = B;
        a.toImproper(), b.toImproper();
    
        mpf_class denomA = string_to_mpf(a.getDenominator());
        mpf_class denomB = string_to_mpf(b.getDenominator());
        mpf_class commonDenom = multiply_mpf(denomA, denomB);
    
        mpf_class numA = string_to_mpf(a.getNumerator()) * denomB;
        mpf_class numB = string_to_mpf(b.getNumerator()) * denomA;
    
        mpf_class totalNum = numA - numB;
    
        Fraction result("0", mpf_to_string(totalNum), mpf_to_string(commonDenom));
        result.reduce();
        result.extractWholePart();
        return result;
    }
    
    Fraction divide(const Fraction A, const Fraction B) {
        Fraction reciprocal_B("0", B.getDenominator(), B.getNumerator());
        return multiply(A, reciprocal_B);
    }
    
    Fraction calculate_latex(const string& latex) {
        vector<string> tokens = tokenize_latex(latex);
        vector<Fraction> values;
        vector<char> ops;
    
        for (const auto& token : tokens) {
            if (token.size() == 1 && string("+-*/").find(token) != string::npos) {
                ops.push_back(token[0]);
            } else {
                values.push_back(parse_fraction(token));
            }
        }
    
        // Обработка умножения и деления
        for (size_t i = 0; i < ops.size();) {
            if (ops[i] == '*' || ops[i] == '/') {
                Fraction a = values[i];
                Fraction b = values[i + 1];
                Fraction res = (ops[i] == '*') ? multiply(a, b) : divide(a, b);
                
                values.erase(values.begin() + i, values.begin() + i + 2);
                values.insert(values.begin() + i, res);
                ops.erase(ops.begin() + i);
            } else {
                ++i;
            }
        }
    
        // Обработка сложения и вычитания
        for (size_t i = 0; i < ops.size();) {
            Fraction a = values[i];
            Fraction b = values[i + 1];
            Fraction res = (ops[i] == '+') ? add(a, b) : subtract(a, b);
            
            values.erase(values.begin() + i, values.begin() + i + 2);
            values.insert(values.begin() + i, res);
            ops.erase(ops.begin() + i);
        }
    
        return values.empty() ? Fraction("0", "0", "1") : values[0];
    }
}

void MATH_LIB_INIT_() {
    mpf_set_default_prec(MathLib::__DEFAULT__PREC__);
    cout << std::setprecision(MathLib::__PRECISION__);
    SetConsoleOutputCP(CP_UTF8);
}