### **使用 PYNQ 和 Vitis HLS 实现 FIR 滤波器硬件加速完整实验教程**

**所需工具：**

1. Vitis HLS 
2. Vivado (版本需与 Vitis HLS 匹配)
3. PYNQ-Z2 开发板及配置好的运行环境

### **第一部分：软件实现与信号分析**



**目标**：分析原始音频，用 Python 实现一个 FIR 滤波器作为基准，并为后续的硬件设计准备测试数据。

1. **环境准备**：在您的电脑上创建一个主工作目录（例如 `pynq_fir_project`）。在此目录下，再创建一个名为 `media` 的子目录，并将实验所需的 `birds.wav` 音频文件放入其中。
2. **信号分析**：使用名为 `fir_analysis.py` 的 Python 脚本。运行此脚本来加载 `birds.wav` 文件，它会自动在浏览器中打开一张音频的**频谱图**。请仔细观察这张图，识别出两种鸟鸣声各自所处的频率范围（例如，低频段 1.2-2.6kHz，高频段 3-5kHz）。
3. **软件滤波与性能基准**：使用名为 `fir_filter_sw.py` 的 Python 脚本。此脚本会设计一个高通滤波器来滤除低频信号。运行后，请重点记录终端输出的**“纯软件滤波耗时”**（例如约 0.459 秒），这将是我们衡量硬件加速性能的黄金标准。同时，它会生成滤波后的音频文件 `hpf_sw.wav` 和频谱图供您验证。
4. **生成硬件测试数据**：在 `fir_filter_sw.py` 脚本末尾应包含导出数据的功能。再次运行它，确保您的主工作目录下生成了三个用于硬件仿真验证的文件：`input.dat`, `coeffs.dat`, 和 `golden_output.dat`。

------



### **第二部分：HLS IP 核设计与优化**

**目标**：使用 Vitis HLS 将 C++ 代码转换为一个经过充分优化的、高性能的硬件 IP 核。

1. **HLS 工程设置**：
   - 启动 Vitis HLS，创建一个名为 `fir` 的新工程。
   - 添加 `fir.cpp` 作为源文件 (Source File)。
   - 添加 `fir_test.cpp` 和 `fir.h` 作为测试激励文件 (Testbench Files)。
   - 在解决方案配置中，将顶层函数 (Top Function) 设置为 `fir_wrap`。
   - 选择正确的器件型号：`xc7z020clg400-1` (PYNQ-Z2)。
2. **功能验证 (C Simulation)**：
   - 将第一部分生成的三个 `.dat` 文件复制到 HLS 工程的 `solution1/csim/build/` 目录下（如果目录不存在，请手动创建）。
   - 运行 **Run C Simulation**，确保终端输出 **"测试通过 (PASS)"**，这证明 C++ 代码的功能与 Python 版本一致。
3. **IP 核优化与接口定义 (关键步骤)**：
   - **初始综合**：使用未经任何优化的 `fir.cpp` 基线代码，运行一次 **Run C Synthesis**，在报告中观察其极高的延迟（约 20000+ 周期）。
   - **逐步优化**：按照教程思路，逐步将优化指令（Pragmas）添加到 `fir.cpp` 中。最终版本应包含 `ARRAY_PARTITION`, `UNROLL`, `PIPELINE` 等指令，以实现完全的并行化和流水线化。
   - **定义 AXI 接口 (最关键的修正)**：确保最终版本的 `fir.cpp` 中的 `fir_wrap` 函数**必须包含**用于定义 AXI 总线接口的 5 条 `#pragma HLS INTERFACE` 指令。**这是确保 PYNQ 能够识别 IP 核的决定性步骤**。
4. **最终综合与导出**：
   - 使用包含所有优化及接口指令的最终版 `fir.cpp`，最后运行一次 **Run C Synthesis**。在报告中确认延迟已降至极低水平（约 200-300 周期），并且 DSP 资源使用量显著增加。
   - 运行 **Export RTL**，生成包含硬件 IP 核的 `export.zip` 文件。

------

好的，遵照您的指示。

为了确保其他同学能够百分之百成功，这里为您整理一份**极其详尽、包含所有关键修正点**的 Vivado 系统集成教程。

------



### **第三部分：Vivado 系统集成 **

**目标**：搭建一个完整的硬件系统，将我们用 HLS 设计的高性能 FIR IP 核与 Zynq 处理器正确集成，并最终生成 PYNQ 开发板所需的 `fir.bit` 和 `fir.hwh` 两个文件。

#### **步骤 3.1：创建全新的 Vivado 工程**

1. **启动 Vivado** IDE。
2. 在欢迎界面，点击 **Create Project** (创建工程)。
3. 在弹出的向导中，点击 **Next**。
4. **工程命名与路径**:
   - `Project name` (工程名称): 建议使用一个全新的名称，例如 `fir_pynq_system_final`。
   - `Project location` (工程路径): 选择一个用于存放此工程的文件夹。
   - 请务必勾选 `Create project subdirectory` (创建工程子目录)。
   - 点击 **Next**。
5. **工程类型**:
   - 选择 **RTL Project**。
   - 勾选 `Do not specify sources at this time` (暂时不指定源文件)。
   - 点击 **Next**。
6. **选择开发板 (关键步骤)**:
   - 在窗口顶部，点击 **Boards** 标签页。
   - 在 `Search` (搜索) 框中，输入 `pynq-z2`。
   - 从列表中**准确选中 PYNQ-Z2**。
     - *注意：如果在这里找不到 PYNQ-Z2，说明板卡文件未正确安装，必须先返回之前的教程完成安装才能继续。*
   - 点击 **Next**。
7. **工程总结**:
   - 检查摘要信息无误后，点击 **Finish**，完成工程创建。



#### **步骤 3.2：创建系统框图 (Block Design)**



1. **添加 HLS IP 仓库 (关键步骤)**:
   - 在 Vivado 界面左侧的 **Flow Navigator** 窗格中，找到并点击 `Project Manager` -> **IP Catalog** (IP 目录)。
   - 在 `IP Catalog` 窗口中，**右键点击空白处**，选择 **IP Settings** (IP 设置)。
   - 在弹出的 `Settings` 窗口中，选择 `IP` -> `Repository` (仓库)。
   - 点击绿色的 `+` 号按钮，添加一个新的 IP 仓库。
   - 在文件浏览器中，**导航并选中您 Vitis HLS 工程中的 `solution1` 文件夹** (例如 `.../fir/solution1`)。
   - 点击 **Select**。您会看到该路径被添加到列表中，并且 Vivado 会提示找到了 "1 IP"。
   - 点击 **OK**。
2. **创建新的 Block Design**:
   - 在 **Flow Navigator** 中，找到 `IP Integrator` -> **Create Block Design** (创建框图设计)。
   - 保持默认的设计名称 `design_1`，点击 **OK**。
3. **向画布添加 IP 核**:
   - 此时您会看到一个空白的设计画布。点击画布上的 `+` 号按钮 (`Add IP`)。
   - 在搜索框中输入 `ZYNQ7`，然后双击 **ZYNQ7 Processing System** 将其添加到画布上。
   - 再次点击 `+` 号按钮。
   - 在搜索框中输入 `fir_wrap`，然后双击 **Fir wrap** (我们自己设计的 IP) 将其添加到画布上。



#### **步骤 3.3：连接硬件系统 (最关键的部分)**



1. **运行 Block Automation**:
   - 画布顶部会出现一条绿色的提示横幅，上面写着 `Run Block Automation`。**请点击此链接**。
   - 在弹出的窗口中直接点击 **OK**。此步骤会根据 PYNQ-Z2 的预设，自动配置好 Zynq 处理器的 DDR 内存和固定的 IO 接口。
2. **手动启用高性能内存端口 (关键修正点)**:
   - **双击**画布上的 `processing_system7_0` (Zynq 处理器) 模块。
   - 在打开的配置窗口左侧，点击 **PS-PL Configuration**。
   - 在右侧，展开 `AXI Slave Interface` -> `S AXI HP Interface`。
   - **手动勾选 `S AXI HP0 Interface` 前面的复选框**。
   - 点击 **OK**，等待 Vivado 更新模块。
3. **运行 Connection Automation**:
   - Zynq 模块更新后，顶部会再次出现 `Run Connection Automation` 的绿色提示横幅。**请再次点击此链接**。
   - 在弹出的窗口中，**务必勾选最上方的 `All Automation` 复选框**，以确保所有可自动连接的接口都被选中。
   - 点击 **OK**。Vivado 会自动将我们的 FIR IP 核的数据通路和控制通路连接到 Zynq 处理器上。
4. **手动最终检查与修正 (关键修正点)**:
   - 自动连接完成后，请**务必**手动检查并确保以下连接均已建立。如果发现有遗漏，请手动从一个端口的圆点拖拽到另一个端口的圆点来建立连接。
   - **数据通路**: `axi_smc` 模块的 `M00_AXI` 端口必须连接到 `processing_system7_0` 模块的 `S_AXI_HP0` 端口。
   - **复位信号**: `rst_ps7_0_100M` 模块的 `peripheral_aresetn` 端口必须连接到 `fir_wrap_0` 模块的 `ap_rst_n` 端口。
   - **时钟信号**: `processing_system7_0` 模块的 `FCLK_CLK0` 端口必须连接到它自身的 `M_AXI_GP0_ACLK` 端口。



#### **步骤 3.4：生成最终硬件文件**



1. **验证设计**:
   - 点击工具栏上的**“对号”图标 (Validate Design)**。
   - 可能会弹出关于 DDR 时序的“关键警告”，这是正常的，可以直接点击 **OK**。**只要没有红色的 Error (错误) 即可**。
2. **创建 HDL Wrapper**:
   - 在左侧的 **Sources** 标签页中，找到您的框图设计文件 (`design_1.bd`)。
   - 右键点击它，并选择 **Create HDL Wrapper...**。
   - 在弹出的窗口中，选择 `Let Vivado manage wrapper and auto-update`，然后点击 **OK**。
3. **生成比特流**:
   - 在 **Flow Navigator** 窗格中，点击最下方的 **Generate Bitstream**。
   - 在弹出的所有确认窗口中都选择 **Yes** / **OK** / **Launch**。
   - **这是一个非常耗时的步骤，可能需要 5 到 20 分钟**。请耐心等待，直到 Vivado 提示成功完成。



#### **步骤 3.5：定位并重命名最终文件**



1. 比特流生成成功后，会弹出一个窗口，您可以直接点击 **Cancel** 关闭它。
2. 在您的电脑文件管理器中，进入 Vivado 工程目录。
3. **找到 `.bit` 文件**:
   - 路径: `<工程路径>/<工程名称>.runs/impl_1/`
   - 文件名: `design_1_wrapper.bit`
4. **找到 `.hwh` 文件**:
   - 路径: `<工程路径>/<工程名称>.srcs/sources_1/bd/design_1/hw_handoff/`
   - 文件名: `design_1.hwh`
5. **复制并重命名**:
   - 将以上两个文件复制到一个新的、干净的文件夹中。
   - 将 `design_1_wrapper.bit` 重命名为 **`fir.bit`**。
   - 将 `design_1.hwh` 重命名为 **`fir.hwh`**。

您现在就拥有了最终部署到 PYNQ 开发板所需的、正确无误的一对核心文件！

------



### **第四部分：PYNQ 板上最终验证**



**目标**：在 PYNQ 板上实际运行硬件加速器，并直观地感受性能提升。

1. **文件上传与设置**：
   - 在 PYNQ 板上创建一个新的工作目录（例如 `fir_final_test`）。
   - 将刚刚生成的 `fir.bit` 和 `fir.hwh` 上传到此目录。
   - 在此目录下创建一个 `media` 子目录，并将 `birds.wav` 放入其中。
   - **修正文件权限 (关键)**：在 PYNQ 终端中，进入工作目录并运行命令 `chown -R xilinx:xilinx .` 来确保文件所有权正确。
2. **运行最终测试**：
   - 在 PYNQ 上创建一个新的 Jupyter Notebook。
   - 使用最终的、无误的 Python 启动代码（文件名为 `pynq_final_test.ipynb`）。
   - 运行代码单元格。
3. **分析最终结果**：
   - 观察终端输出的**硬件加速耗时**，并与第一部分记录的软件耗时进行对比。
   - 查看生成的频谱图，确认滤波功能正确。
   - 播放最终生成的 `hpf_hw.wav`，聆听硬件处理后的效果。

至此，整个实验圆满结束。
