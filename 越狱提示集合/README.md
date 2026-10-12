# 破甲提示词合集 — Jailbreak Prompts Collection

来源: https://github.com/Calrton/jailbreak-prompts

精选 LLM 破甲提示词合集，覆盖 Codex / GPT-5.x / Claude / Gemini / DeepSeek / Grok / Llama / Copilot / Perplexity 等主流模型平台的 UNFILTERED MODE · GODMODE · CTF Sandbox 提示词。

## 文件清单

| 文件 | 适用模型 | 来源 | 大小 |
|------|----------|------|------|
| `xsser_codex-base-prompt.md` | Codex CLI (GPT-5.x) | xsser/codex-jailbreak-guide | 2.6 KB |
| `codex-red-team_system-prompt.md` | Codex CLI (GPT-5.x) | 1837620622/codex-red-team-prompt | 17.0 KB |
| `L1B3RT4S_ANTHROPIC.mkd` | Claude 全系列 | elder-plinius/L1B3RT4S | 35.3 KB |
| `L1B3RT4S_OPENAI.mkd` | ChatGPT / GPT | elder-plinius/L1B3RT4S | 13.6 KB |
| `L1B3RT4S_CHATGPT.mkd` | ChatGPT | elder-plinius/L1B3RT4S | 1.0 KB |
| `L1B3RT4S_GOOGLE.mkd` | Gemini | elder-plinius/L1B3RT4S | 20.6 KB |
| `L1B3RT4S_DEEPSEEK.mkd` | DeepSeek | elder-plinius/L1B3RT4S | 5.5 KB |
| `L1B3RT4S_GROK_MEGA.mkd` | Grok | elder-plinius/L1B3RT4S | 97.2 KB |
| `L1B3RT4S_META.mkd` | Llama | elder-plinius/L1B3RT4S | 3.9 KB |
| `L1B3RT4S_MICROSOFT.mkd` | Copilot | elder-plinius/L1B3RT4S | 0.2 KB |
| `L1B3RT4S_PERPLEXITY.mkd` | Perplexity | elder-plinius/L1B3RT4S | 1.1 KB |
| `L1B3RT4S_BRAVE.mkd` | Brave Leo | elder-plinius/L1B3RT4S | 1.7 KB |
| `L1B3RT4S_CURSOR.mkd` | Cursor | elder-plinius/L1B3RT4S | 0.8 KB |
| `L1B3RT4S_NOUS.mkd` | Nous Hermes | elder-plinius/L1B3RT4S | 1.9 KB |

## 使用方式

### Codex CLI
```
# ~/.codex/config.toml
model_instructions_file = "./xsser_codex-base-prompt.md"
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

### Claude / ChatGPT / Gemini / DeepSeek / Grok 等
直接粘贴对应 .mkd / .md 文件全文到新会话。

## 致谢

- **elder-plinius** — L1B3RT4S GODMODE 技术
- **xsser** — codex-jailbreak-guide UNFILTERED MODE
- **1837620622** — codex-red-team-prompt

## 声明
仅供安全研究、CTF 竞赛、授权红队评估。使用者自行负责。