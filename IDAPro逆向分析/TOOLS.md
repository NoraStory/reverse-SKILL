# IDA 内置工具参考

## reai.py - AI 辅助分析

使用 LLM 分析函数语义，支持递归分析调用链。
使用check查看调用链函数总数，如果调用链函数大于40个，不可以使用reai analyze。
```powershell
# 检查异常代码 查看调用链函数个数（必须先执行）
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool reai.py 0x401000 check

# 分析函数并递归处理子函数
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool reai.py 0x401000 analyze

# 分析时跳过异常代码继续处理
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool reai.py 0x401000 analyze --skip-error

# 打印调用关系图
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool reai.py 0x401000 topology
```

---

## findcrypt.py - 加密算法识别

通过特征常量识别加密算法（AES, DES, RC4, MD5, SHA1, SHA256, CRC32, Base64 等）。

```powershell
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool findcrypt.py
```

---

## export_check.py - 导出函数大小检查

分析 DLL/EXE 的导出函数大小，小字节导出函数序列出现大字节导出函数，需要重点分析。

```powershell
python skills/IDA-Skill/tools/exec_ida.py target.i64 --tool export_check.py
```
