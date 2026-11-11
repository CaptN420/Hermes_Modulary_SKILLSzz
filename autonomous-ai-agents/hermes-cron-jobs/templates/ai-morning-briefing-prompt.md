# AI Morning Briefing — cron prompt template

Reusable self-contained prompt for the user's daily AI briefing cron job (deliver=discord, schedule `0 8 * * *`). Adapt sections when editing; never rewrite from memory — read the stored prompt from `cron/jobs.json` first.

## Skeleton (current 9-section layout)

```
Write the complete daily AI morning briefing, in ENGLISH (keep technical names, model names and product names in their original language). Serious AI watch: verified, sourced information only, from the last ~24h (an older but highly relevant item may be included if its date is stated). Do real web research (web_search + web_extract) across several queries; never invent a story, never present a rumour as a fact, merge redundant sources.

Themes: (1) new LLM/multimodal/reasoning/vision/audio-video models, open source and proprietary, local (NVIDIA, Anthropic, OpenAI, Google, Meta, xAI, Mistral, DeepSeek, Alibaba/Qwen, Microsoft...); (2) AI news: releases, products, tools, API changes, benchmarks, acquisitions, pricing; (3) LOCAL AI first: Ollama, llama.cpp, MLX, LM Studio, Hugging Face, vLLM, quantizations, inference techniques, large models running locally, CUDA/NVIDIA, Apple Silicon, memory/performance optimisations; (4) agents & automation: autonomous agent frameworks, coding agents, workflows, MCP, tools that let LLMs use apps/services; (5) research: publications with practical impact.

Deliver the briefing with EXACTLY this structure, in this order:

**🤖 AI MORNING BRIEFING — [today's date]**

### 🔥 1. TOP 5 — What I absolutely need to know today
### 🧠 2. NEW MODELS
### 🛠️ 3. NEW TOOLS / PROJECTS
### 📺 4. THE 3 VIDEOS TO WATCH
### 🌐 5. SITES / ARTICLES TO READ
### 💻 6. LOCAL AI — What changed
### 📈 7. BENCHMARKS & LEADERBOARDS — Who is leading
### 📊 8. TRENDS
### ⭐ 9. MY RECOMMENDATION OF THE DAY

[Each section keeps its field checklist — see the live job prompt for the full per-section requirements.]

Style rules: quality over quantity, emojis in moderation, Discord format readable on mobile (avoid very wide tables), briefing readable in 5-10 min, every important item sourced. Your final answer will be delivered to Discord automatically — do not write it to a file and do not take any other action.
```

## Notes

- Always end with the auto-delivery note so the cron agent doesn't try to send or write the output itself.
- The 9-section structure is the user's standing preference for this class of job. The language is now English; switch the "in ENGLISH" clause back to "in FRENCH" if a French briefing is wanted.
