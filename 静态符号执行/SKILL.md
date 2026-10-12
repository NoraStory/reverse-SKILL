---
name: 静态符号执行
description: 静态符号执行方法论（供安全研究/自有应用）。当需要求解混淆过的指令序列、自动推导某输入约束、还原被 OLLVM/VMP 打乱的逻辑时，用 Angr / Miasm / Triton 做符号执行。涵盖三种引擎选型、符号执行基本流程、约束求解、处理路径爆炸。
---

# 静态符号执行（Angr / Miasm / Triton）

当逻辑被混淆到人眼难读，或想"给定输出反推输入"时，符号执行让工具替你算。把具体值换成符号变量，跟踪约束，最后用求解器解出满足条件的输入。

## 一、三种引擎怎么选
| 引擎 | 语言 | 强项 | 适合 |
|---|---|---|---|
| **Angr** | Python | 生态全、上手快、CFG/符号执行/求解一体 | 通用首选、CTF、找特定路径输入 |
| **Miasm** | Python | 中间表示强、擅长反混淆/重写 | OLLVM/VMP 去混淆、指令语义分析 |
| **Triton** | C++/Python | 动态符号执行、污点分析、快 | 跟真实执行结合、单函数精确分析 |

## 二、Angr 典型流程（最常用）
```python
import angr, claripy
proj = angr.Project("libtarget.so", auto_load_libs=False)
# 目标函数地址
func = 0x1234
# 符号化输入
arg = claripy.BVS("arg", 8*16)
state = proj.factory.call_state(func, arg)
simgr = proj.factory.simulation_manager(state)
# 找到"验证通过"的地址，避开"失败"地址
simgr.explore(find=0xAABB, avoid=0xCCDD)
if simgr.found:
    print(simgr.found[0].solver.eval(arg, cast_to=bytes))
```

## 三、关键难点：路径爆炸
- 分支太多 → 状态指数增长跑不完。对策：
  - 用 `avoid` 剪掉无关分支
  - 缩小符号化范围（只符号化关键输入，其余给具体值）
  - 从目标函数中间开始（`blank_state(addr=...)`）而非从 main
  - hook 掉耗时的库函数（`proj.hook`）用 SimProcedure 替代

## 四、配合其他技能
- 反 OLLVM：符号执行帮确定平坦化的 state 转移（配合 deobfuscation-ollvm）
- VMP：Miasm 符号执行分析 VM handler 语义（配合 devirtualization-vmp）
- native 定位：先用 ida-decompile/rev-symbol 找到目标函数地址再符号执行

## 五、手机端现实
符号执行工具（angr/miasm/triton）跑在 **PC**（手机装不了）。玄星里 AI 的角色：
- 帮你写/改 angr 脚本、定位 find/avoid 地址、诊断路径爆炸
- 解读符号执行结果、把求解出的输入翻译成人话
- 实际运行在你电脑上，AI 指导

## 边界
用于自有 App / 授权样本的算法分析、漏洞研究、CTF、学习。不协助破解他人付费验证。
