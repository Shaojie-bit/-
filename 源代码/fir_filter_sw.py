import time
import os
import numpy as np
import warnings
import plotly.graph_objs as go
from scipy.io import wavfile
from scipy.signal import firwin, lfilter, spectrogram, decimate

# 忽略 Scipy 的 FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- 1. 读入音频信号 ---
AUDIO_FILE_PATH = "./media/birds.wav"
if not os.path.exists(AUDIO_FILE_PATH):
    print(f"错误：找不到音频文件 {AUDIO_FILE_PATH}")
    exit()

fs, aud_in = wavfile.read(AUDIO_FILE_PATH)
print(f"成功读取音频文件，采样频率: {fs} Hz")

# --- 2. 设计 FIR 滤波器 ---
# FIR 滤波器的参数
nyq = fs / 2.0  # 奈奎斯特频率，是采样频率的一半
taps = 99  # 滤波器阶数（系数数量）
cutoff_hz = 2800.0  # 截止频率设为 2.8 kHz

# 使用 firwin 函数设计一个高通滤波器
# pass_zero=False 表示这是一个高通滤波器
hpf_coeffs = firwin(taps, cutoff_hz / nyq, pass_zero=False)
print(f"成功设计了一个 {taps} 阶的高通 FIR 滤波器。")

# --- 3. 应用滤波器并计时 ---
print("\n正在使用纯软件方式进行滤波...")
start_time = time.time()

# 使用 lfilter 函数将设计好的滤波器系数应用到原始音频数据上
aud_hpf = lfilter(hpf_coeffs, 1.0, aud_in)

end_time = time.time()

# 打印执行时间，这个时间很重要，后续将与硬件加速的结果进行对比
print(f"纯软件滤波耗时: {end_time - start_time:.6f} 秒")


# --- 4. 结果可视化 ---
# 定义绘图函数 (与上一个脚本相同)
def plot_spectrogram(samples, fs, title, decimation_factor=3):
    if decimation_factor > 1:
        samples_dec = decimate(samples, decimation_factor, zero_phase=True)
        fs_dec = int(fs / decimation_factor)
    else:
        samples_dec = samples
        fs_dec = fs

    f_label, t_label, spec_data = spectrogram(
        samples_dec, fs=fs_dec, mode="magnitude"
    )

    # 自动调整热力图的颜色范围，以获得更好的视觉效果
    max_heat = np.max(np.abs(samples_dec)) * 0.5  # 使用降采样后的数据计算max_heat并乘以一个系数

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=np.clip(spec_data, 0, max_heat),
        y=f_label,
        x=t_label
    ))
    fig.update_layout(
        title=title,
        xaxis_title='时间 (s)',
        yaxis_title='频率 (Hz)',
        height=500
    )
    fig.show()


# 调用函数，显示滤波后的音频频谱图
print("正在生成滤波后的频谱图，图表将在你的浏览器中打开...")
plot_spectrogram(aud_hpf, fs, title='滤波后音频的频谱图 (纯软件)')

# --- 5. 保存并播放滤波后的结果 ---
# 将浮点数结果转换回16位整型以便保存为 .wav 文件
# 我们需要对数据进行归一化处理，防止削波
scaled_output = np.int16(aud_hpf / np.max(np.abs(aud_hpf)) * 32767)

output_filename = "hpf_sw.wav"
wavfile.write(output_filename, fs, scaled_output)
print(f"\n滤波后的音频已保存为 {output_filename}。你可以播放它来听听效果。")
# ... (在脚本末尾添加) ...

# --- 6. 导出数据用于 HLS C++ Testbench ---
print("\n正在导出 HLS Testbench 所需的数据...")

# 将输入数据转换为 int32 (因为在 HLS 中我们通常使用整数)
# 注意：实验教程中输入数据类型为 int16，但为了处理中间值，我们使用 int32
input_data_int = np.int32(aud_in)

# 我们需要将浮点系数转换为整数，以便在硬件中使用
# 这个过程称为“量化”
hpf_coeffs_quant = hpf_coeffs / np.max(np.abs(hpf_coeffs)) * (2**15 - 1)
hpf_coeffs_int = np.int32(hpf_coeffs_quant)

# 使用量化后的整数系数，重新计算一次滤波结果，作为 C++ 仿真的“标准答案”
# 这样可以确保我们是在“苹果对苹果”的比较
golden_output_quant = lfilter(hpf_coeffs_int, 1.0, input_data_int)
golden_output_int = np.int32(golden_output_quant)

# 将数据保存到文本文件中
np.savetxt('input.dat', input_data_int, fmt='%d')
np.savetxt('coeffs.dat', hpf_coeffs_int, fmt='%d')
np.savetxt('golden_output.dat', golden_output_int, fmt='%d')

print("HLS Testbench 数据已成功保存到 input.dat, coeffs.dat, 和 golden_output.dat 文件中。")