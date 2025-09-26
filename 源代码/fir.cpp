#include "./fir.h"

// 全局系数数组
coef_t c[N];

// FIR 核心计算函数 (这部分保持我们最终的优化版本不变)
void fir(data_t *y, data_t x)
{
    // 静态移位寄存器数组
    static data_t shift_reg[N];

    // 阵列分区指令，用于实现并行访问
    #pragma HLS ARRAY_PARTITION variable=c complete dim=0
    #pragma HLS ARRAY_PARTITION variable=shift_reg complete dim=0

    acc_t acc;
    int i;

    acc = 0;

    // TDL 循环：应用“循环展开”，实现所有移位操作并行执行
    TDL:
    for (i = N - 1; i > 0; i--) {
        #pragma HLS unroll
        shift_reg[i] = shift_reg[i - 1];
    }
    shift_reg[0] = x;

    // MAC 循环：应用“流水线”，实现乘法累加操作重叠执行
    MAC:
    for (i = N - 1; i >= 0; i--) {
        #pragma HLS PIPELINE II=1
        acc += shift_reg[i] * c[i];
    }

    *y = acc;
}


// HLS 顶层函数 (Top Function)
void fir_wrap(data_t *y, data_t *x, int len, coef_t *coef)
{
    // ====================== 【关键修改处】 ======================
    // 下面这 5 行是解决问题的核心。
    // 它们将 C++ 函数的参数映射为标准的 AXI 总线接口，
    // 这样 PYNQ 和 Vivado 才能正确识别和连接我们的 IP 核。

    // 为数据指针 y, x, coef 创建高性能的 AXI-Master 接口
    #pragma HLS INTERFACE m_axi depth=100 port=y
    #pragma HLS INTERFACE m_axi depth=100 port=x
    #pragma HLS INTERFACE m_axi depth=99 port=coef

    // 为 len 和函数控制信号创建 AXI-Lite 控制接口
    #pragma HLS INTERFACE s_axilite port=len bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL
    // ==========================================================

    data_t res;

    // 将系数从主内存读入 IP 核内部
    for (int i = 0; i < N; i++)
    {
        #pragma HLS PIPELINE II=1
        c[i] = *coef++;
    }

    // 对每一个输入数据点调用 fir 函数进行处理
    for (int i = 0; i < len; i++)
    {
        #pragma HLS PIPELINE II=1
        fir(&res, *x++);
        *y = res;
        y++;
    }
}
