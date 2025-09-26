#include <iostream>
#include <fstream>
#include <vector>
#include "fir.h"

int main() {
    // 从文件中读取数据
    std::ifstream input_file("input.dat");
    std::ifstream coeffs_file("coeffs.dat");
    std::ifstream golden_output_file("golden_output.dat");

    if (!input_file || !coeffs_file || !golden_output_file) {
        std::cerr << "错误: 无法打开数据文件！请确保 input.dat, coeffs.dat, 和 golden_output.dat 文件在 HLS 工程目录下。" << std::endl;
        return 1;
    }

    // 将数据读入 vector
    std::vector<data_t> input_data;
    std::vector<coef_t> coeffs_data;
    std::vector<data_t> golden_output_data;
    
    data_t val;
    while (input_file >> val) input_data.push_back(val);
    while (coeffs_file >> val) coeffs_data.push_back(val);
    while (golden_output_file >> val) golden_output_data.push_back(val);

    int data_len = input_data.size();
    std::vector<data_t> actual_output(data_len);

    // 调用待测试的 HLS 顶层函数
    fir_wrap(actual_output.data(), input_data.data(), data_len, coeffs_data.data());

    // 比较实际输出和黄金标准输出
    bool pass = true;
    for (int i = 0; i < data_len; ++i) {
        // 由于C++和Python在滤波计算的实现上可能有微小差异，
        // 我们检查差值是否在一个可接受的小范围内
        if (abs(actual_output[i] - golden_output_data[i]) > 2) {
            std::cout << "测试失败! Index: " << i 
                      << ", 实际输出: " << actual_output[i] 
                      << ", 期望输出: " << golden_output_data[i] << std::endl;
            pass = false;
            break;
        }
    }

    if (pass) {
        std::cout << "***************************" << std::endl;
        std::cout << "* 测试通过 (PASS)      *" << std::endl;
        std::cout << "***************************" << std::endl;
    } else {
        std::cout << "***************************" << std::endl;
        std::cout << "* 测试失败 (FAIL)      *" << std::endl;
        std::cout << "***************************" << std::endl;
    }

    input_file.close();
    coeffs_file.close();
    golden_output_file.close();

    return pass ? 0 : 1;
}