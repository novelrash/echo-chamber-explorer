# Echo Chamber Explorer

A web-based bias analysis tool that helps identify and measure bias in news articles and content using integrated academic research methodologies.

## Features

- **Integrated Multi-Methodology Analysis**: Combines Harvard/PNAS, Columbia, and AllSides research
- **Directional Bias Detection**: -1.000 to +1.000 scale (negative=left, positive=right)
- **Academic Credibility**: Based on peer-reviewed research methodologies
- **Transparent Scoring**: Component breakdown shows how each methodology contributes
- **Web Interface**: Easy-to-use interface for analyzing content
- **Analysis History**: Track and review past analyses
- **Statistics Dashboard**: View system performance and bias distribution

## Methodology

**Integrated Multi-Source Analysis** - Combines three authoritative research methodologies:

### Methodology Weights
- **Harvard/PNAS Study (40%)**: Position and attribution weighting based on Kim, Lelkes, McCrain 2022 research
- **Columbia University (35%)**: Partisan phrase detection from Gentzkow & Shapiro methodology  
- **AllSides Assessment (20%)**: Multi-dimensional bias indicators
- **Sentiment Analysis (5%)**: Overall emotional tone and subjectivity

### Key Components
- **Position Weighting**: Headlines and lead paragraphs weighted more heavily
- **Attribution Weighting**: Direct quotes weighted more than background sources
- **Partisan Phrase Detection**: Identifies left/right-leaning terminology with directional scoring
- **Source Diversity**: Multiple perspectives reduce overall bias score
- **3 Significant Figures**: Precise scoring (e.g., -0.346, +0.128)

## Bias Scoring System

- **-1.000 to -0.600**: Very High Left Bias
- **-0.599 to -0.300**: High Left Bias  
- **-0.299 to -0.100**: Low Left Bias
- **-0.099 to +0.099**: Minimal Bias
- **+0.100 to +0.299**: Low Right Bias
- **+0.300 to +0.599**: High Right Bias
- **+0.600 to +1.000**: Very High Right Bias

## Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/echo-chamber-explorer.git
   cd echo-chamber-explorer
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and go to `http://localhost:5000`

### Using Docker

1. **Build and run with Docker**:
   ```bash
   docker build -t echo-chamber-explorer .
   docker run -p 5000:5000 echo-chamber-explorer
   ```

## Project Structure

```
echo-chamber-explorer/
├── app.py                          # Main Flask application
├── integrated_bias_analyzer.py     # Core bias analysis engine
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Docker Compose for development
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Continuous Integration
│       └── deploy.yml              # Deployment pipeline
├── src/
│   ├── analyzers/                  # Bias analysis modules
│   ├── models/                     # Database models
│   └── utils/                      # Utility functions
├── templates/                      # HTML templates
├── static/                         # CSS, JS, images
├── tests/                          # Test suite
├── docs/                           # Documentation
└── scripts/                        # Deployment and utility scripts
```

## API Usage

### Analyze Content

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your article text here",
    "title": "Article Title (optional)",
    "url": "Article URL (optional)"
  }'
```

### Response Format

```json
{
  "bias_score": -0.346,
  "bias_description": "Moderate bias (left-leaning)",
  "scale_info": "Score range: -1.000 (strong left bias) to +1.000 (strong right bias)",
  "methodology": "Integrated analysis: Harvard (40%) + Columbia (35%) + AllSides (20%) + Sentiment (5%)",
  "analysis_details": {
    "methodology_scores": {
      "harvard": {"score": -0.350},
      "columbia": {"score": -0.500},
      "allsides": {"score": 0.000},
      "sentiment": {"score": 0.043}
    }
  }
}
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_bias_analyzer.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Deployment

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `SECRET_KEY`: Flask secret key for sessions

### Production Deployment

The application includes CI/CD pipelines for:
- **GitHub Actions**: Automated testing and deployment
- **Docker**: Containerized deployment
- **AWS**: Ready for deployment to AWS services

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Research Citations

- Kim, Lelkes, McCrain (2022). "Measuring Dynamic Media Bias." PNAS.
- Gentzkow & Shapiro. "What Drives Media Slant? Evidence from U.S. Daily Newspapers." Columbia University.
- AllSides Media Bias Methodology

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Harvard/PNAS research team for media bias methodology
- Columbia University for partisan phrase research
- AllSides for multi-dimensional bias assessment framework
