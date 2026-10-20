# Design Decisions

Each decision is framed as **Decision → Rationale → Trade-off → Result**.

## 1. Exclude RAG from the initial scope

**Decision:** Use only project information directly supplied in the input.

**Rationale:** Retrieval would introduce a second failure layer. Keeping retrieval out makes it easier to distinguish generation/classification failures from retrieval failures.

**Trade-off:** The application cannot automatically search a multi-document project corpus.

**Result:** Generation and evaluation behavior could be measured independently; retrieval becomes a separate future extension.

## 2. Use structured output

**Decision:** Validate outputs with a Pydantic `ProgramReview` schema rather than relying on free-form prose.

**Rationale:** TPM findings need to be machine-readable and consistently comparable across experiments.

**Trade-off:** Hard category boundaries expose classification errors that free-form prose could hide.

**Result:** Structural checks, field assertions, and model-to-model comparisons became deterministic.

## 3. Start with one controlled local model

**Decision:** Stabilize prompt, schema, and evaluation with Ollama + `qwen3:8b` before adding a hosted model.

**Rationale:** Changing multiple model variables at once would make root-cause analysis harder.

**Trade-off:** Hosted-model quality was not measured during early iteration.

**Result:** The final prompt and holdout were frozen before Gemini was introduced, reducing provider-specific tuning bias.

## 4. Use low-randomness generation settings

**Decision:** Use temperature 0 for structured analysis. Local qwen used `think=False`; Gemini used the provider-supported `thinking_level=low`.

**Rationale:** The task values repeatable extraction and classification over creative diversity.

**Trade-off:** Provider runtime controls are not perfectly equivalent.

**Result:** Experimental comparisons focus on task behavior rather than intentional sampling variation.

## 5. Add few-shot examples only after measured failures

**Decision:** Move from rule accumulation to targeted semantic examples when category-boundary failures persisted.

**Rationale:** More than 30 rules in an earlier prompt did not improve semantic quality enough. Examples were better suited to showing boundaries such as Action vs Risk and Proposed vs Confirmed Requirement.

**Trade-off:** Few-shot examples increase prompt tokens and can overfit to example patterns.

**Result:** `fewshot-v0.5` was selected as the frozen prompt; a later v0.6 improved some classifications but missed the predeclared 80.0 semantic adoption gate.

## 6. Use an evidence-first schema

**Decision:** Material findings require evidence from the supplied input; subjective confidence/severity/likelihood fields were excluded from the first schema.

**Rationale:** Unsupported confidence can imply certainty that the input does not justify.

**Trade-off:** Strict lexical evidence checks may reject valid paraphrases.

**Result:** Evidence traceability can be measured independently from structural and semantic quality.

## 7. Keep final program decisions human-in-the-loop

**Decision:** The model identifies findings, evidence, and uncertainty; it does not autonomously accept risk, change schedules, set priorities, or make client commitments.

**Rationale:** These decisions often require business and technical context outside the supplied update.

**Trade-off:** Human review remains in the workflow.

**Result:** The system is positioned as TPM decision support rather than an autonomous decision maker.

## Decision boundaries in practice

An **Issue** is an already-occurring project problem; a **Risk** is a plausible future adverse condition grounded in source facts; a **Dependency** identifies a prerequisite between work items; an **Action** is a commitment or next step, not a speculative recommendation. Proposed requirement changes remain distinct from confirmed approvals. Missing ownership or dates remain unknown rather than being guessed.

These category boundaries are reinforced by the frozen [schema](../src/schemas.py) and [prompt examples](../src/prompts.py). Classification is still imperfect; the final holdout showed misses on inferred risks and some action/dependency categorization. The decision-support design therefore requires a TPM to review the findings before taking consequential actions.
