# AI Morning Briefing — cron prompt template

Reusable self-contained prompt for the user's daily AI briefing cron job (deliver=discord, schedule `0 8 * * *`). Adapt sections when editing; never rewrite from memory — read the stored prompt from `cron/jobs.json` first.

## Skeleton (current 9-section layout)

```
Rédige le briefing IA matinal quotidien complet, en FRANÇAIS (noms techniques, modèles, produits restés en langue originale). Veille IA sérieuse : uniquement des informations vérifiées, sourcées, des dernières ~24h (une info plus ancienne mais très pertinente peut être incluse en indiquant sa date). Fais des recherches web réelles (web_search + web_extract) sur plusieurs requêtes ; ne fabrique jamais une nouvelle, ne présente jamais une rumeur comme un fait, regroupe les sources redondantes.

Thèmes : (1) nouveaux modèles LLM/multimodaux/raisonnement/vision/audio-vidéo, open source comme propriétaires, locaux (NVIDIA, Anthropic, OpenAI, Google, Meta, xAI, Mistral, DeepSeek, Alibaba/Qwen, Microsoft...) ; (2) actualités IA : releases, produits, outils, changements d'API, benchmarks, acquisitions, prix ; (3) LOCAL AI en priorité : Ollama, llama.cpp, MLX, LM Studio, Hugging Face, vLLM, quantizations, techniques d'inférence, gros modèles en local, CUDA/NVIDIA, Apple Silicon, optimisations mémoire/performance ; (4) agents & automatisation : frameworks d'agents autonomes, coding agents, workflows, MCP, outils pour les LLM utiliser des apps/services ; (5) recherche : publications à impact pratique.

Rends le briefing avec EXACTEMENT cette structure, dans cet ordre :

**🤖 AI MORNING BRIEFING — [date du jour]**

### 🔥 1. TOP 5 — Ce que je dois absolument savoir aujourd'hui
### 🧠 2. NOUVEAUX MODÈLES
### 🛠️ 3. NOUVEAUX OUTILS / PROJETS
### 📺 4. LES 3 VIDÉOS À REGARDER
### 🌐 5. SITES / ARTICLES À CONSULTER
### 💻 6. LOCAL AI — Ce qui a changé
### 📈 7. BENCHMARKS & LEADERBOARDS — Qui est en tête
### 📊 8. TENDANCES
### ⭐ 9. MA RECOMMANDATION DU JOUR

[Each section keeps its field checklist — see the live job prompt for the full per-section requirements.]

Règles de style : qualité avant quantité, emojis avec modération, format Discord lisible sur mobile (éviter les tableaux très larges), briefing lisible en 5-10 min, chaque élément important sourcé. Ta réponse finale sera automatiquement envoyée sur Discord — ne l'écris pas dans un fichier et ne fais aucune autre action.
```

## Notes

- Always end with the auto-delivery note so the cron agent doesn't try to send or write the output itself.
- The French style + section structure is the user's standing preference for this class of job.
