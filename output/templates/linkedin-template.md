# LinkedIn Post Templates — UC12 Benchmark Results

Use one of these three variants below based on your benchmark findings. Fill all `[FILL: ...]` placeholders with data from `output/report.md` before posting.

---

## Variant 1: "The Surprising Winner"

**When to use:** When a local/open-source model outperforms a commercial or more expensive model on at least one task category.

**Template:**

We ran [FILL: number of models] local AI models against [FILL: number of categories] task categories. The winner wasn't what we expected.

[FILL: Local model name] outperformed [FILL: commercial/expensive model name] on [FILL: category name] by [FILL: score difference] points. It wasn't just that one category either — across all [FILL: number] categories, the results surprised us:

[FILL: Key finding #1 with numbers]
[FILL: Key finding #2 with numbers]
[FILL: Key finding #3 with numbers]

If you're [FILL: target audience — e.g., "building AI-powered applications" or "running inference at scale"], you might not need the expensive API.

What's your go-to model for [FILL: category name]? Drop it in comments.

---

## Variant 2: "The Right Tool"

**When to use:** When results show clear specialization — different models excel at different categories rather than one dominant winner.

**Template:**

Not all AI models are equal. And honestly, that's actually a good thing.

We benchmarked [FILL: number of models] models across [FILL: number of categories] task types. Every single model had at least one category where it dominated:

[FILL: Model A name] won at [FILL: category]. Average score: [FILL: X.X]/5.
[FILL: Model B name] dominated [FILL: category]. Average score: [FILL: X.X]/5.
[FILL: Model C name] surprised us on [FILL: category]. Average score: [FILL: X.X]/5.

The lesson here: model selection matters more than model size. Pick the right tool for your specific task, and you'll get better results.

Are you using the right model for your specific task? Or are you defaulting to whichever one you tried first?

---

## Variant 3: "Open Science"

**When to use:** When emphasizing reproducibility, transparency, and open methodology (works for any benchmark results).

**Template:**

We benchmarked [FILL: number of models] AI models across [FILL: number of task categories]. And we're publishing the raw data so you can challenge our results.

Here's what we did:
- Used ChainForge to run identical prompts across all models
- Scored each output on a 5-point rubric
- Ran [FILL: number of trials per category] trials per category
- Recorded every score, every prompt, every model version

One key finding: [FILL: biggest finding — e.g., "Open-source models closed the gap with commercial APIs faster than expected."]

Everything is in the repo — methodology, raw CSVs, scoring rubrics, hardware specs. Clone it. Re-run it. Challenge our results.

What benchmark categories would you add to make this more useful for your work?

---

## Template Completion Notes

- **[FILL: number of models]** — count from your models table in report.md (usually 5-8)
- **[FILL: number of categories]** — count of task categories (usually 10)
- **[FILL: Local model name]** and **[FILL: commercial/expensive model name]** — pull from Overall Rankings table
- **[FILL: score difference]** — subtract lower score from higher score (e.g., 4.8 - 3.2 = 1.6)
- **[FILL: Key finding #N with numbers]** — pull from "Key Findings" section in report.md
- **[FILL: target audience]** — e.g., "researchers", "startups", "enterprises running inference", "teams on a budget"
- **[FILL: category name]** — any category where results were interesting or surprising
- **[FILL: biggest finding]** — the most important takeaway from the entire benchmark

## Posting Rules

All posts must:
- Be 150-250 words
- Start with a specific number or surprising fact (not generic preamble)
- End with a question to drive comments
- Avoid corporate jargon: no "excited to share", "thrilled to announce", "AI revolution"

## After Posting

Log engagement metrics in `output/social-media/posting-log.md`:
- Date posted
- Post variant used
- View count (if available)
- Engagement rate
- Top comment or sentiment
