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
#include <cctype>

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
    fs::path __CURRENT__DIR__ = fs::current_path();
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

    string removeSpaces(string s) {
        s.erase(remove(s.begin(), s.end(), ' '), s.end());
        return s;
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







    // TODO: Mathpix.com подключить распознавание в LaTeX.



    bool LaTeXtoPNG(const std::string& latexCode, const std::string& outputFileName, int dpi = 800) {
        namespace fs = std::filesystem;

        // 1. Определяем пути
        fs::path output_dir = __CURRENT__DIR__ / "renderLaTeX" / outputFileName;
        fs::path temp_dir = __CURRENT__DIR__ / "temp_files";
        fs::path texFile = temp_dir / "temp.tex";
        fs::path dviFile = temp_dir / "temp.dvi";
        fs::path logFile = temp_dir / "temp.log";
        fs::path auxFile = temp_dir / "temp.aux";

        // 2. Пути к бинарникам
        #ifdef _WIN32
            fs::path latexPath = __CURRENT__DIR__ / "libraries" / "MikTeX" / "miktex" / "bin" / "x64" / "latex.exe";
            fs::path dvipngPath = __CURRENT__DIR__ / "libraries" / "MikTeX" / "miktex" / "bin" / "x64" / "dvipng.exe";
        #else
            fs::path latexPath = __CURRENT__DIR__ / "libraries" / "TeXLive" / "bin" / "x86_64-linux" / "latex";
            fs::path dvipngPath = __CURRENT__DIR__ / "libraries" / "TeXLive" / "bin" / "x86_64-linux" / "dvipng";
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
    

    /// Разбивает строку s по разделителю delim
    static vector<string> split(const string& s, char delim) {
        vector<string> parts;
        std::string cur;
        for (char c : s) {
            if (c == delim) {
                parts.push_back(cur);
                cur.clear();
            } else {
                cur.push_back(c);
            }
        }
        parts.push_back(cur);
        return parts;
    }

    /// Вычисляет значение одночлена, который может быть целым числом
    /// или дробью вида "(num/den)"
    static double parseTerm(const std::string& term) {
        // Если термин обёрнут в скобки и содержит '/', считаем дробь
        if (term.size() >= 5 && term.front() == '(' && term.back() == ')' && term.find('/') != std::string::npos) {
            // вырезаем "num/den"
            std::string frac = term.substr(1, term.size() - 2);
            auto parts = split(frac, '/');
            if (parts.size() == 2) {
                double num = std::stod(parts[0]);
                double den = std::stod(parts[1]);
                return num / den;
            }
        }
        // Иначе просто целое (или вещественное) число
        return stod(term);
    }


    /// Экранирует backslash и кавычки, чтобы можем вставить в C-строковый литерал
    static std::string escapeForCString(const std::string& s) {
        std::string out;
        out.reserve(s.size()*2);
        for (char c : s) {
            if (c == '\\')      out += "\\\\";
            else if (c == '\"') out += "\\\"";
            else                out += c;
        }
        return out;
    }



    string normalizeFraction(const string& latex_expr) {
        // Функция принимает строку с LaTeX выражением и заменяет все фракции вида \frac{num}{den} на (num.0/den.0).
        static const regex frac_re(R"(\\frac\{(-?\d+)\}\{(-?\d+)\})");
        string result = "";
        auto searchStart = latex_expr.cbegin();
        smatch match;
    
        while (regex_search(searchStart, latex_expr.cend(), match, frac_re)) {
            // копируем всё до найденной фракции
            result.append(searchStart, match.prefix().second);
    
            // форматируем числитель и знаменатель как mpf_class.
            string num = mpf_to_string(string_to_mpf(match[1].str()));
            string den = mpf_to_string(string_to_mpf(match[2].str()));
    
            // добавляем строку вида "(num.den/den.den)"
            result += "(" + num + "/" + den + ")";
    
            // двигаем указатель за текущую фракцию
            searchStart = match.suffix().first;
        }
    
        // добавляем хвост после последней фракции
        result.append(searchStart, latex_expr.cend());
        return result;
    }




    string eval(const string& expression) {
        string result = "";
        //Функция принимает строку с выражением, затем компилирует и запускает временный C++ файл, который вычисляет это выражение и возвращает результат.

        //1. Создаю временные файлы и директории.
        fs::path temp_dir = __CURRENT__DIR__ / "temp_files";
        fs::create_directories(temp_dir);
        fs::path src = temp_dir / "temp_eval.cpp";
        fs::path err = temp_dir / "compile_errors.txt";
        fs::path exe = temp_dir / "temp_eval.exe";

        
        //2. Подготовлю выражение-литерал
        string lit = escapeForCString(expression);

        //Берём lit, делаем замену: каждую последовательность цифр с точкой превращаем в mpf_class("…")
        static const std::regex num_re(R"((\d+\.\d+))");
        string expr_with_mpf = std::regex_replace(
            lit,
            num_re,
            std::string(R"(mpf_class("$1"))")
        );

        //3. Создам c++ код, что далее компилируется во временном файле (в папке temp_files) и возвращает результат выражения.
        string program =
            "#include <iostream>\n"
            "#include <string>\n"
            "#include <iomanip>\n"
            "#include <sstream>\n"
            "#include <C:\\Users\\dagahan\\Desktop\\MathLib\\libraries\\GMP\\include\\gmpxx.h>\n"
            "std::string mpf_to_string(const mpf_class num, int precision = 32) {\n"
            "    std::ostringstream oss;\n"
            "    oss << std::fixed\n"
            "       << std::setprecision(48)\n"
            "       << num;\n"
            "    return oss.str();\n"
            "}\n"
            "int main(){\n"
            "    mpf_set_default_prec(48);\n"
            "    mpf_class result = " + expr_with_mpf + ";\n"
            "    std::cout << mpf_to_string(result) << std::endl;\n"
            "    return 0;\n"
            "}\n";
            {
                std::ofstream ofs(src, std::ios::trunc);
                if (!ofs) return "Error: cannot open temp source file for writing";
                ofs << program;
                // при выходе из этого блока ofs будет закрыт
            }

        //4. Компилирую файл c++ в исполняемый файл с помощью g++.
        string compile_cmd = "g++ -std=c++17 -O2 \"" + src.string() +
            "\" -o \"" + exe.string() +
            "\" -lgmpxx -lgmp 2> \"" + err.string() + "\"";
        int ccode = system(compile_cmd.c_str());

        //4.5 Проверяю, что ошибка компиляции не возникла.
        if (ccode == 0) {
            array<char, 128> buffer;
            

            //5. Запускаю через popen() исполняемый файл и читаю результат в pipe.
            #ifdef _WIN32
                FILE* pipe = _popen(exe.string().c_str(), "r");
            #else
                FILE* pipe = popen(exe.string().c_str(), "r");
            #endif
                if (!pipe) throw runtime_error("popen() failed!");

                // Читаем всё из pipe
                while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
                    result += buffer.data();
                }

                // Закрываем pipe
            #ifdef _WIN32
                _pclose(pipe);
            #else
                pclose(pipe);
            #endif
        }

        else { //Если возникла ошибка компиляции, то читаю её из файла compile_errors.txt и возвращаю результат.
            ifstream iferr(err);
            stringstream ss;
            ss << iferr.rdbuf();
            result = "Compilation Error:\n" + ss.str();
        }

        //6. Удаляю все временные файлы и возвращаю результат.
        for (auto &p : {src, err, exe}) {
            if (fs::exists(p)) {
                try { fs::remove(p); }
                catch (...) {}
            }
        }
        return result;
    }

    string solveLaTeX(const string latexCode) {
        //1. Преобразую LaTeX выражение в string, содержащий формат выражения, который может выполнить компилятор c++ напрямую.
        string expression = normalizeFraction(latexCode);
        //2. Возвращаю результат вычисления, что произвёл компилятор c++ во временном файле.
        return eval(expression);
    }
}

void MATH_LIB_INIT_() {
    mpf_set_default_prec(MathLib::__DEFAULT__PREC__);
    cout << std::setprecision(MathLib::__PRECISION__);
    SetConsoleOutputCP(CP_UTF8);
}