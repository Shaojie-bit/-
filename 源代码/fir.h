#ifndef FIR_H
#define FIR_H

// 定义滤波器阶数 (tap数量)
const int N = 99;

// 为数据、系数和累加器定义统一的数据类型
// 使用 int 类型以匹配我们从 Python 生成的数据
typedef int data_t;
typedef int coef_t;
typedef int acc_t;

// 这是我们的顶层函数，HLS 将会把它转换成硬件IP
// 函数参数的接口类型将在后续步骤中指定
void fir_wrap(data_t *y, data_t *x, int len, coef_t *coef);

#endif // FIR_H