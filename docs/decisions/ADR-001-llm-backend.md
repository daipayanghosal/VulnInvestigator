# ADR-001: LLM Backend Selection

**Date**: 2026-01-01  
**Status**: Decided  
**Deciders**: Dissertation author  
**Context**: VulnInvestigator requires a large language model to generate evidence-grounded threat investigation reports.

---

## Context and Problem Statement

The system needs an LLM to:
1. Explain contextual risk rankings in natural language
2. Generate structured investigation reports grounded in CVE + ATT&CK + log evidence
3. Provide remediation guidance tailored to specific assets

The choice of LLM backend has significant implications for:
- **Reproducibility**: Academic research requires consistent, auditable outputs
- **Cost**: API calls accumulate rapidly during iterative development
- **Output quality**: Reasoning quality directly affects the research conclusions
- **Privacy**: CVE and asset data may be organisationally sensitive

---

## Options Considered

### Option A: OpenAI (GPT-4o)

| Criterion | Assessment |
|---|---|
| Output quality | Excellent — GPT-4o excels at structured reasoning and citation |
| Cost | High — ~\$5–15/M output tokens (may accumulate to \$50–200 during research) |
| Reproducibility | Moderate — temperature=0 helps but API changes affect outputs over time |
| Privacy | Poor — data is sent to OpenAI servers; not suitable for sensitive org data |
| Setup complexity | Low — single API key |

### Option B: Ollama (Local LLM — LLaMA 3, Mistral)

| Criterion | Assessment |
|---|---|
| Output quality | Good — Llama 3 70B matches GPT-4 for many tasks but weaker at structured output |
| Cost | Near-zero — only compute costs (runs locally on GPU/CPU) |
| Reproducibility | Excellent — same model weights, fully local, deterministic with fixed seed |
| Privacy | Excellent — no data leaves the machine |
| Setup complexity | Medium — requires Ollama installation, model download (4–40 GB) |

### Option C: Google Gemini (gemini-2.0-flash / gemini-1.5-pro)

| Criterion | Assessment |
|---|---|
| Output quality | Excellent — competitive with GPT-4o, strong structured output and long-context |
| Cost | Low–moderate — Gemini 2.0 Flash has a generous free tier (1M tokens/min free) |
| Reproducibility | Moderate — consistent within API version; versions are numbered |
| Privacy | Moderate — data sent to Google servers; Gemini API does not use data for training by default |
| Setup complexity | Low — single API key (GEMINI_API_KEY) |

---

## Decision

**Primary backend: Google Gemini (gemini-2.0-flash)**

Rationale:
1. **Cost**: The Gemini free tier provides sufficient throughput for dissertation-scale experiments (hundreds of LLM calls) without cost.
2. **Quality**: gemini-2.0-flash produces high-quality structured outputs suitable for the investigation report format.
3. **Reproducibility**: Version-locked API calls and low temperature (0.2) provide adequate reproducibility; outputs are logged for audit.
4. **Fallback**: The codebase supports all three backends via `get_llm_client(backend=…)`. Switching requires only a single environment variable change (`LLM_BACKEND=openai` or `LLM_BACKEND=ollama`).

---

## Consequences

### Positive
- Zero cost during development and experimentation
- Fast inference (Gemini Flash is optimised for speed)
- Long context window (1M tokens) supports large evidence bundles
- Simple setup: `pip install google-generativeai` + `GEMINI_API_KEY`

### Negative / Risks
- Google API availability: system is unavailable if Gemini API is down
- Privacy: CVE/asset data is transmitted to Google (acceptable for simulated data; use Ollama for real sensitive environments)
- API changes: `google-generativeai` library may require updates if the API evolves

### Mitigations
- All three backends are implemented; switching is a one-line config change
- LLM responses are logged to `data/processed/` for offline analysis
- Tests use mocked LLM responses, so the test suite runs without any API key

---

## Revisit Criteria

This decision should be revisited if:
- Gemini free tier limits are reached during large-scale evaluation (→ switch to Ollama)
- The dissertation requires strict data locality guarantees (→ switch to Ollama)
- GPT-4o quality is demonstrably superior for specific research questions (→ switch to OpenAI)
