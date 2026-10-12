---
name: OLLVM反混淆
description: 反混淆/控制流平坦化还原（De-OLLVM）方法论（供安全研究/自有应用）。当 native 函数被 OLLVM 混淆（控制流平坦化 Flattening、虚假控制流 BCF、指令替换 SUB）导致 IDA 反编译一团乱、看不懂逻辑时，用于识别分发器、还原真实控制流、恢复可读逻辑。涵盖 OLLVM 三种混淆识别与去除思路、Deflat 脚本、符号执行辅助。
---

# 反混淆 · 控制流平坦化还原（De-OLLVM）

OLLVM 是最常见的 native 混淆，反编译出来全是 `while(1){ switch(state){...} }` 看不懂逻辑。这个技能教你还原。

## 一、识别 OLLVM 三大混淆
| 混淆 | 特征 | IDA 表现 |
|---|---|---|
| **控制流平坦化 (Flattening)** | 把顺序代码拆成 switch-case + 状态分发器 | 一个大 while + switch，块之间靠 state 变量跳 |
| **虚假控制流 (BCF)** | 插入永假/永真的分支 | 大量 `if(opaque)` 不会走的死代码 |
| **指令替换 (Sub)** | 简单运算换成等价复杂式子 | `a+b` 变成一堆位运算 |

## 二、平坦化还原核心思路（重点）
平坦化的本质：真实的"块 A→块 B"被
...[520 chars omitted]...
署 patch）
3. 复杂/大量函数 → 用 D-810（IDA 插件，自动去 OLLVM）或 Triton/Miasm 符号执行做（见 static-symbolic-execution 技能）
4. 只需理解逻辑不需还原文件 → 直接跟着 state 变量人工梳理主干

## 四、工具
- **D-810**：IDA 插件，自动反 OLLVM，首选
- **deflat.py**（angr 系）：脚本化去平坦化
- **Triton/Miasm**：符号执行还原（硬核，见 static-symbolic-execution）
- **unicorn**：模拟执行辅助确定 state 转移（见 rev-unicorn-debug）

## 五、验证
还原后对比：关键输入下，原函数和还原函数输出是否一致（可用 unicorn 各跑一遍对比）。

## 边界
用于自有 App / 授权样本的混淆分析、算法理解、安全研究、学习编译器混淆原理。不协助破解他人商业保护牟利。
