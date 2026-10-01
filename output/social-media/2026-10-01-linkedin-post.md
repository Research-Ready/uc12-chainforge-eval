# LinkedIn Post Draft: 2026-10-01

_Human-corrected from AI draft: verified against output/runs/2026-10-01-summary.json_

---

We ran 4 local AI models across 5 task categories on our own hardware. Here's what surprised us.

The winner was phi4 (9.1 GB). It beat qwen3:14b: a model 200 MB larger: by 3 points overall.

More interesting: our smallest model, llama3.1:8b (4.9 GB), tied the winner on code generation and security analysis. Runs twice as fast. Costs nothing to host.

Full results (median score /5):

| Category | hermes3 | qwen3:14b | phi4 | llama3.1:8b |
|----------|---------|-----------|------|-------------|
| Reasoning | 4 | 5 | 5 | 4 |
| Code gen | 5 | 4 | 5 | 5 |
| Security | 5 | 4 | 5 | 5 |
| Creative | 4 | 4 | 4 | 4 |
| Instruction | 4 | 4 | 5 | 4 |
| **Total** | **22** | **21** | **24** | **22** |

One category where nothing differentiated: creative writing. Every model scored 4/5. That tells you something about where local models still plateau.

Hardware: AMD Ryzen 7 8845HS, RTX 4060 (8 GB), 46 GB RAM. All prompts, scores, and raw data are in the public repo. Clone it, re-run it, challenge the results.

What benchmark category would you add next?

---

**Repo:** https://github.com/Research-Ready/uc12-chainforge-eval
_#AI #LLM #OpenSource #LocalAI #ResearchReady_
