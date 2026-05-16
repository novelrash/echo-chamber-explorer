# Echo Chamber Explorer

A web tool that detects political bias in news articles using two independent analysis methods: a Claude-powered linguistic analysis (primary) and a keyword heuristic system based on academic methodologies (secondary). Results from both run in parallel so you can compare them.

## How it works

Paste or POST article text. You get back two independent scores:

**1. AI Analysis (primary)** — Claude Haiku reads the article the same way a human analyst would: looking at word choice, framing, which sources are quoted and how, and whether the headline language matches neutral reporting. Returns a score from −1.0 (strongly left-leaning) to +1.0 (strongly right-leaning) in 0.1 increments, plus a written rationale and specific flagged phrases.

**2. Keyword Analysis (secondary)** — A heuristic system that counts partisan terminology, weights sentences by position (headlines count more than late paragraphs), and checks source diversity. Returns a score to three significant figures. Built from three published methodologies:
- Harvard/PNAS (40%) — position and attribution weighting (Kim, Lelkes, McCrain 2022)
- Columbia University (35%) — partisan phrase detection (Gentzkow & Shapiro)
- AllSides (20%) — story framing and source diversity indicators
- TextBlob sentiment (5%)

The two methods often agree directionally but diverge in magnitude. The AI can detect structural framing bias that phrase-matching can't see; the keyword analyzer is cheaper and fully transparent about exactly why it scored what it did.

## Limitations (read this)

The keyword analyzer has real constraints worth knowing:

- It can only detect words and phrases in its vocabulary. Novel partisan framing that doesn't use recognized terms scores 0.0.
- Its phrase lists reflect the political discourse as of when they were written. Language evolves.
- "Score 0.0" means "no partisan phrases detected," not "this article is neutral." A sophisticated propaganda piece that avoids common partisan language will score near zero.
- The Harvard position weighting assumes standard inverted pyramid article structure. Opinion pieces, long-form essays, and transcripts don't follow this structure.

The AI analysis has different limitations:
- Claude's training data has its own biases that may affect scoring of certain topics.
- Short texts (under ~100 words) get low-confidence scores.
- The LLM cannot verify factual claims — it scores language, not truth.
- Articles over ~2,500 words are truncated before AI analysis. The keyword analyzer still runs on the full text.

**Neither score should be read as ground truth.** The goal is to surface patterns worth looking at, not to render a verdict.

## Bias score reference

```
−1.0 to −0.6   Very high left bias
−0.6 to −0.3   High left bias
−0.3 to −0.1   Low left bias
−0.1 to +0.1   Minimal bias
+0.1 to +0.3   Low right bias
+0.3 to +0.6   High right bias
+0.6 to +1.0   Very high right bias
```

The AI score is calibrated to these anchors:
- AP wire report on a Senate vote → 0.0
- Consistent use of one side's preferred terminology → ±0.3 to ±0.5
- Op-ed with loaded language throughout → ±0.6 to ±0.8
- Fundraising email or propaganda → ±0.9 to ±1.0

## Setup

### Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/) (required for AI analysis; keyword analysis works without it)

### Local development

```bash
git clone https://github.com/yourusername/echo-chamber-explorer.git
cd echo-chamber-explorer

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Copy the example env file and add your API key:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

Initialize the database and start the server:

```bash
python app.py
```

Open `http://localhost:5000`.

If `ANTHROPIC_API_KEY` is not set, the app starts in keyword-only mode. The AI analysis section won't appear in results, and the `/health` endpoint will show `"llm_enabled": false`.

### Docker

```bash
docker-compose up --build
```

The compose file mounts `.env` from the project root. Set your API key there before starting.

## API

### POST /api/analyze

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your article text here",
    "title": "Article Title",
    "source": "Publication Name"
  }'
```

Response:

```json
{
  "llm_enabled": true,
  "llm_analysis": {
    "score": -0.4,
    "confidence": "high",
    "lean": "center-left",
    "reasoning": {
      "word_choice": "Consistent use of terms preferred by the left...",
      "framing": "Story leads with impact on vulnerable groups...",
      "sources": "Three progressive advocacy groups quoted, one industry rep...",
      "headline": "Headline uses 'slash' rather than neutral 'reduce'..."
    },
    "flagged_phrases": ["working families", "corporate interests"],
    "limitations": "Article is primarily opinion; factual claims not verified",
    "model": "claude-haiku-4-5-20251001",
    "truncated": false,
    "error": null
  },
  "keyword_analysis": {
    "bias_score": -0.312,
    "bias_description": "Moderate bias (left-leaning)",
    "methodology": "Integrated analysis: Harvard (40%) + Columbia (35%) + AllSides (20%) + Sentiment (5%)",
    "analysis_details": {
      "methodology_scores": {
        "harvard":  {"score": -0.280},
        "columbia": {"score": -0.500},
        "allsides": {"score": 0.042},
        "sentiment": {"score": -0.018}
      },
      "methodology_weights": {
        "harvard": 0.40,
        "columbia": 0.35,
        "allsides": 0.20,
        "sentiment": 0.05
      }
    }
  }
}
```

### GET /health

Returns service status and whether LLM analysis is active.

### GET /history

Web page showing the last 50 analyses with both scores.

### GET /stats

Aggregate statistics: score distribution, averages, min/max across all stored analyses.

## Cost

AI analysis uses Claude Haiku. A typical analysis call sends roughly 1,800–2,500 input tokens (system prompt + article text) and receives ~400–600 output tokens (the reasoning JSON). At current Haiku pricing that works out to approximately **$0.003–$0.005 per analysis** — around **$3–5 per 1,000 articles**.

Running it on a few hundred articles a day costs about $1/day. At scale (tens of thousands of articles), it's worth looking at caching the system prompt if the API supports it, or batching.

Articles over 12,000 characters (~2,500 words) are truncated before LLM analysis. A warning appears in the UI and in the `truncated` field of the API response. The keyword analyzer always runs on the full text.

## Project structure

```
echo-chamber-explorer/
├── app.py                                # Flask app, routes, DB writes
├── analyzers/
│   ├── llm_bias_analyzer.py              # Claude-based analysis
│   └── integrated_bias_analyzer.py      # Keyword heuristic system
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── analyze.html
│   ├── results.html
│   ├── history.html
│   └── stats.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── tests/
│   └── test_bias_analyzer.py
├── .env.example                          # Copy to .env and fill in key
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Running tests

```bash
python -m pytest
python -m pytest --cov=analyzers --cov-report=term-missing
```

## Research citations

- Kim, Lelkes, McCrain (2022). "Measuring Dynamic Media Bias." *PNAS*.
- Gentzkow, Shapiro (2010). "What Drives Media Slant? Evidence from U.S. Daily Newspapers." *Econometrica*.
- AllSides Media Bias Rating Methodology — [allsides.com/media-bias/media-bias-rating-methods](https://www.allsides.com/media-bias/media-bias-rating-methods)

## License

MIT
