# 导入所需的库
from scipy.io import wavfile
import numpy as np
import warnings
import plotly.graph_objs as go
# 注意：我们不再使用 plotly.offline
from scipy.signal import spectrogram, decimate
import os

# Scipy库可能会产生一些关于未来版本变更的警告，我们在这里将其忽略
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- 1. 定义音频文件路径 ---
# 确保 'media' 文件夹和这个脚本在同一个目录下
AUDIO_FILE_PATH = "./media/birds.wav"

if not os.path.exists(AUDIO_FILE_PATH):
    print(f"错误：找不到音频文件 {AUDIO_FILE_PATH}")
    print("请确保 'birds.wav' 文件在一个名为 'media' 的子文件夹中。")
    exit()

print("分析 'birds.wav' 文件...")
# 在脚本中，我们无法直接播放音频，但你可以用系统播放器手动打开它。


# --- 2. 读入信号 ---
# 使用 SciPy 的 wavfile 模块读入信号
# fs 是采样频率，aud_in 是原始音频数据
fs, aud_in = wavfile.read(AUDIO_FILE_PATH)

# 打印一些信号信息
print(f"采样频率 (fs): {fs} Hz")
print(f"数据类型: {type(aud_in)}")
print(f"数据点长度: {len(aud_in)}")
print(f"数据格式: {aud_in.dtype}")


# --- 3. 绘制频谱图 ---
# 定义一个函数来绘制频谱图
def plot_spectrogram(samples, fs, decimation_factor=3, max_heat=50):
    if decimation_factor > 1:
        samples_dec = decimate(samples, decimation_factor, zero_phase=True)
        fs_dec = int(fs / decimation_factor)
    else:
        samples_dec = samples
        fs_dec = fs

    f_label, t_label, spec_data = spectrogram(
        samples_dec, fs=fs_dec, mode="magnitude"
    )

    # 在 .py 脚本中，我们创建一个 Figure 对象，然后调用 .show()
    fig = go.Figure()
    
    fig.add_trace(go.Heatmap(
        z=np.clip(spec_data, 0, max_heat),
        y=f_label,
        x=t_label
    ))
    
    fig.update_layout(
        title='原始音频频谱图',
        xaxis_title='时间 (s)',
        yaxis_title='频率 (Hz)',
        height=500
    )

    # .show() 会自动在你的默认浏览器中打开一个包含图表的标签页
    fig.show()


# 调用函数，绘制并显示原始音频的频谱图
print("\n正在生成频谱图，图表将在你的浏览器中打开...")
plot_spectrogram(aud_in, fs)

print("\n频谱图已生成。请在浏览器中查看。")
print("观察图表，为下一步设计滤波器做准备。")