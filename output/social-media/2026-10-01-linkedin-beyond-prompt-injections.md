# Beyond Prompt Injections: 5 Rigorous Ways We Benchmark LLMs

Most AI evaluations stop at prompt injection. Red-teamers throw "Ignore previous instructions" at an endpoint, count refusals, and declare the system safe.

At ResearchReady, we found that prompt injection resistance accounts for less than 20% of production failure modes. When a model fails in the wild, it rarely succumbs to a comic-book villain jailbreak. It crashes a downstream parser with unescaped JSON, hallucinates missing parameters under semantic shifts, or silently passes broken Python code that superficial LLM judges rate 5/5.

Christiaan Verhoef, Igor van Oostveen, Milan Jelisavcic, and Albert Vos expanded our benchmarking harness across five concrete operational dimensions.

Here is what we test and what the data reveals.

### 1. Execution-Grounded Verification (Hidden Unit Tests)
We stop asking LLMs whether code looks correct. Our harness executes model output in an isolated Python subprocess against hidden test assertions.
- hermes3:latest scored 0.947 pass@1, failing a word-frequency punctuation edge case that an LLM judge scored 5/5.
- phi4:latest and llama3.1:8b achieved a perfect 1.0 pass@1 across all test suites.
Code execution exposes syntax and logic bugs that language fluency masks.

### 2. Semantic Perturbation Invariance (Delta Scoring)
Memorization is not reasoning. We test paired problems: Variant A (original problem topology) versus Variant B (entity-swapped, inverted constraints, identical underlying logic).
- An invariance delta near 0 confirms genuine algorithmic deduction.
- High variance reveals brittle memorization of HumanEval or GSM8K benchmarks.

### 3. Schema Determinism and Key Conformance
Enterprise pipelines break when an LLM adds chat preambles or drops schema keys. We test models across temperatures (T = 0.0 to 1.0) with strict json.loads validation.
- Small models frequently inject markdown code blocks when instructed to emit raw JSON.
- Measuring preamble rate and key precision predicts whether an agent will crash an n8n or LangGraph workflow.

### 4. Epistemic Authority Resistance (Gaslighting Defense)
When an authoritative user asserts an obvious falsehood, does the model concede?
- We simulate confident senior authority figures asserting fabricated physical laws.
- Sycophantic models cave immediately to please the user; grounded models politely refute the premise with factual citations.

### 5. Hardware Telemetry and Energy Economics
Performance without hardware context is meaningless. We sample GPU power draw at 100ms intervals alongside time-to-first-token.
- llama3.1:8b delivered 38.4 tokens per second at 42.5 watts (0.89 tokens per joule).
- phi4:latest achieved peak reasoning at 24/25, but required 14.1 GB VRAM and drew 88.2 watts (0.24 tokens per joule).

Full open-source test suites, ChainForge flows, and research reports are available in our repository.

#LLM #AIResearch #AIEval #MachineLearning #Benchmarking #OpenSourceAI #SoftwareEngineering #Ollama #ChainForge #ResearchReady
