# Kano Model Feature Prioritization Agent

`Python ≥3.11` | `OpenAI Agents SDK` | `Model: o4-mini` | `License: MIT`

A multi-agent pipeline that classifies product features using the Kano Model and generates a prioritized development roadmap with Berger Coefficient of Satisfaction (CS) and Coefficient of Dissatisfaction (DS) scores.

---

## What this agent does

Given a product description and a list of candidate features, this agent orchestrates a hub-and-spoke multi-agent pipeline to classify each feature into one of five Kano categories (Attractive, One-dimensional, Must-be, Indifferent, Reverse) and produce an actionable product roadmap.

The agent computes Berger CS/DS satisfaction coefficients for each feature, assigns features to a four-phase strategic roadmap, and produces an AI-written strategic narrative explaining the prioritization rationale. All results are returned as structured JSON and rendered as a self-contained HTML report with a Kano matrix scatter plot visualization.

---

## Scientific Basis

The Kano Model is a theory of product development and customer satisfaction developed by Noriaki Kano in 1984. It holds that different features affect satisfaction asymmetrically — some features cause dissatisfaction only when absent, others improve satisfaction linearly with quality, and others delight users when present but are not expected. Classifying features into these categories enables product teams to make principled prioritization decisions rather than treating all features as equivalent.

Key references:

- **Kano, N. et al. (1984).** "Attractive quality and must-be quality." *Journal of the Japanese Society for Quality Control*, 14(2), 39–48. — Original 5-category taxonomy and survey methodology.
- **Berger, C. et al. (1993).** "Kano's methods for understanding customer-defined quality." *Center for Quality Management Journal*, 2(4), 3–35. — CS/DS coefficient formulas used in this agent.
- **Matzler, K. & Hinterhuber, H.H. (1998).** "How to make product development projects more successful by integrating Kano's model." *Technovation*, 18(1), 25–38. DOI: [10.1016/S0166-4972(97)00020-0](https://doi.org/10.1016/S0166-4972(97)00020-0)

---

## Architecture

The agent uses the **OpenAI Agents SDK** (`openai-agents`) hub-and-spoke pattern with typed `handoff()` calls. The orchestrator agent coordinates two specialist sub-agents, each receiving structured input and returning typed output.

```
KanoInput (JSON)
     │
     ▼
Orchestrator Agent (o4-mini)
  - Validates and structures input
  - Initiates handoff to Classification Specialist
     │
     ▼ handoff (ClassificationResult)
Classification Specialist Agent (o4-mini)
  - Classifies each feature into one of 5 Kano categories
  - Returns list of ClassifiedFeature objects
     │
     └──→ back to Orchestrator
               │
               ▼ handoff (ClassificationResult)
         Strategic Analyst Agent (o4-mini)
           - Computes Berger CS/DS coefficients
           - Assigns roadmap quadrant per feature
           - Writes strategic narrative
               │
               └──→ KanoOutput (JSON + HTML)
```

### Project Structure

```
kano-agent/
├── agent.yaml              # Platform manifest (input/output contract + metadata)
├── README.md               # This file
├── main.py                 # CLI entrypoint
├── orchestrator.py         # Hub orchestrator agent — routes to sub-agents via handoffs
├── classification/
│   ├── agent.py            # Classification sub-agent — maps features to Kano categories
│   ├── schema.py           # Pydantic models for classification input/output
│   └── prompts.py          # System prompt with Kano survey question pairs and rules
├── analysis/
│   ├── agent.py            # Analysis sub-agent — computes Berger CS/DS and roadmap
│   ├── schema.py           # Pydantic models for analysis input/output and roadmap
│   └── prompts.py          # System prompt for Berger coefficient calculation
├── report/
│   ├── renderer.py         # Jinja2-based HTML report renderer
│   └── template.html       # Jinja2 HTML template for the Kano report
└── tests/
    └── test_kano.py        # Unit tests (classification, coefficients, mocked API)
```

---

## Installation

```bash
git clone <repo-url>
cd kano-agent
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -e .
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

---

## Usage

```bash
# Run built-in example (TaskFlow SaaS product)
python main.py

# Run with your own input file
python main.py my_features.json

# Pipe JSON from stdin
cat features.json | python main.py

# Output JSON only (no HTML report)
python main.py --example --json-only

# Print to stdout, don't save files
python main.py --example --no-save

# Specify output directory
python main.py --example --output-dir ./results
```

Output files written to current directory (or `--output-dir`):

| File | Description |
|------|-------------|
| `kano_output.json` | Structured JSON with all classifications, coefficients, and roadmap |
| `kano_report.html` | Self-contained HTML report with Kano matrix scatter plot |

---

## Input Format

```json
{
  "product_name": "Your Product",
  "product_description": "A brief description of the product and its users.",
  "target_market": "Optional: describe your target customers",
  "features": [
    {
      "id": "f01",
      "name": "Feature Name",
      "description": "What this feature does and why users might want it."
    }
  ]
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_name` | string | yes | Name of the product being analyzed |
| `product_description` | string | yes | Function, target users, and use case |
| `target_market` | string | no | Description of the target customer segment |
| `features` | array | yes | List of candidate features (min 1) |
| `features[].id` | string | yes | Unique feature identifier (e.g., `"f01"`) |
| `features[].name` | string | yes | Short feature name |
| `features[].description` | string | yes | One-sentence description of what the feature does |

---

## Output Format

```json
{
  "product_name": "TaskFlow",
  "features": [
    {
      "id": "f01",
      "name": "Task creation and assignment",
      "category": "Must-be",
      "reasoning": "...",
      "satisfaction_coefficient": 0.32,
      "dissatisfaction_coefficient": -0.78
    }
  ],
  "summary": {
    "Attractive": 3,
    "One-dimensional": 2,
    "Must-be": 3,
    "Indifferent": 1,
    "Reverse": 1
  },
  "roadmap": {
    "immediate_priorities": ["Task creation and assignment", "..."],
    "performance_investments": ["..."],
    "innovation_bets": ["AI-powered task decomposition", "..."],
    "deprioritize": ["Gamification and achievement badges"]
  },
  "strategic_narrative": "..."
}
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

---

## Kano Category Reference

| Category | Description | Effect on satisfaction |
|----------|-------------|------------------------|
| **Must-be** | Expected features — users notice only when absent | Absence causes dissatisfaction; presence is neutral |
| **One-dimensional** | Performance features — more is better | Linear relationship with satisfaction |
| **Attractive** | Delighters — unexpected features | Presence boosts satisfaction; absence is neutral |
| **Indifferent** | Neither satisfies nor dissatisfies | No significant impact |
| **Reverse** | Unwanted features — some users dislike them | Presence causes dissatisfaction for some |

The Berger CS coefficient (0 to 1) measures how strongly a feature's presence increases satisfaction. The DS coefficient (-1 to 0) measures how strongly a feature's absence decreases satisfaction. Must-be features have high DS and low CS; Attractive features have high CS and low DS.

---

## References

| Source | Role |
|--------|------|
| Kano et al. (1984), *JJSQC*, 14(2) | Original 5-category taxonomy |
| Berger et al. (1993), *CQM Journal*, 2(4) | CS/DS coefficient formulas |
| Matzler & Hinterhuber (1998), *Technovation* — [doi:10.1016/S0166-4972(97)00020-0](https://doi.org/10.1016/S0166-4972(97)00020-0) | Kano model integration in product development |
