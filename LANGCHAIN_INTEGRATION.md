# 🤖 LangChain Integration for Echo Chamber Explorer

## Overview
Your Echo Chamber Explorer now has AI-powered enhancements using LangChain agents that provide:

- **AI Research Context**: Automatically researches topics for balanced perspectives
- **Source Credibility Analysis**: Evaluates website trustworthiness
- **Basic Fact-Checking**: Searches for verification of claims
- **Enhanced Bias Detection**: Identifies manipulation techniques

## Files Added

### Core Integration
- `src/analyzers/langchain_enhanced_analyzer.py` - Enhanced analyzer with AI agents
- `app_enhanced.py` - Enhanced Flask app with agent integration
- `templates/results_enhanced.html` - Enhanced results display
- `start_enhanced.sh` - Startup script for enhanced version

### Demo & Testing
- `demo_enhanced.py` - Demonstration script
- `LANGCHAIN_INTEGRATION.md` - This documentation

## Quick Start

### 1. Run Demo
```bash
cd /mnt/c/Users/User
source langchain-env/bin/activate
cd echo-chamber-explorer
python demo_enhanced.py
```

### 2. Start Enhanced Web App
```bash
./start_enhanced.sh
```
Then visit: http://localhost:5000

### 3. Manual Testing
```bash
cd /mnt/c/Users/User
source langchain-env/bin/activate
cd echo-chamber-explorer
python -c "
from src.analyzers.langchain_enhanced_analyzer import LangChainEnhancedAnalyzer
analyzer = LangChainEnhancedAnalyzer()
results = analyzer.analyze_with_agents('Your text here')
print(results)
"
```

## New Features

### 🔍 AI Research Context
- Automatically extracts key topics from articles
- Searches for different perspectives on those topics
- Provides context to help identify echo chamber effects

### 🏛️ Source Credibility Analysis
- Checks for author attribution
- Verifies publication dates
- Analyzes domain reputation
- Counts external references
- Provides credibility score (0-100%)

### ✅ Basic Fact-Checking
- Identifies factual claims in text
- Searches for verification information
- Flags claims that need verification

### ⚠️ Enhanced Bias Detection
- **Emotional Manipulation**: Detects phrases designed to provoke emotion
- **False Dichotomy**: Identifies "either/or" fallacies
- **Appeal to Fear**: Flags fear-based language
- **Loaded Questions**: Detects leading questions

## Database Enhancements

New columns added to `analysis_results` table:
- `agent_research` (TEXT) - JSON of research results
- `source_credibility` (REAL) - Credibility score 0-1
- `fact_check_results` (TEXT) - JSON of fact-check attempts
- `enhanced_bias_indicators` (TEXT) - JSON of bias indicators

## API Enhancements

### New Endpoint: `/api/quick-analyze`
```bash
curl -X POST http://localhost:5000/api/quick-analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Your article text here"}'
```

Returns:
```json
{
  "bias_score": -0.123,
  "bias_category": "Low Left Bias",
  "agent_research_count": 3,
  "fact_checks": 2,
  "enhanced_indicators": 4
}
```

## Performance Notes

- **Agent Research**: ~2-3 seconds per topic (3 topics max)
- **Source Credibility**: ~1-2 seconds per URL
- **Fact Checking**: ~1-2 seconds per claim (2 claims max)
- **Enhanced Detection**: <1 second (local processing)

## Customization

### Adding New Bias Indicators
Edit `_detect_enhanced_bias()` in `langchain_enhanced_analyzer.py`:

```python
# Add new detection patterns
new_patterns = ['your pattern here']
for pattern in new_patterns:
    if pattern in text_lower:
        indicators['your_category'].append(pattern)
```

### Modifying Research Topics
Edit `_extract_key_topics()` to change topic extraction:

```python
# Customize keyword filtering
custom_stop_words = {'your', 'custom', 'words'}
keywords = [word for word in keywords if word not in custom_stop_words]
```

### Adjusting Credibility Scoring
Edit `_analyze_source_credibility()` to modify scoring:

```python
# Adjust scoring weights
if trusted_domain:
    score += 0.3  # Increase weight for trusted domains
```

## Integration with Existing Features

The enhanced analyzer is fully compatible with:
- ✅ Original bias scoring methodology
- ✅ Manual rating system
- ✅ Statistics dashboard
- ✅ Database structure
- ✅ All existing templates

## Troubleshooting

### Agents Not Available
If you see "Agents available: False":
```bash
cd /mnt/c/Users/User
source langchain-env/bin/activate
pip install ddgs langchain-community
```

### Import Errors
Make sure you're in the correct environment:
```bash
source /mnt/c/Users/User/langchain-env/bin/activate
```

### Database Issues
Reset the database:
```bash
rm bias_analysis.db
python -c "from app_enhanced import init_db; init_db()"
```

## Next Steps

1. **Add OpenAI Integration**: Set `OPENAI_API_KEY` in `.env` for advanced features
2. **Custom Agents**: Create domain-specific agents for your use cases
3. **Batch Processing**: Process multiple articles automatically
4. **API Integration**: Connect to external fact-checking services
5. **Machine Learning**: Train custom bias detection models

## Support

- **LangChain Docs**: https://python.langchain.com/
- **Original Project**: Your existing Echo Chamber Explorer
- **Demo Script**: `python demo_enhanced.py`

---

🎉 **Your Echo Chamber Explorer is now AI-powered!**
