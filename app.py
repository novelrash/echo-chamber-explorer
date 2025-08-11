#!/usr/bin/env python3
"""
Echo Chamber Explorer - Bias Analysis Web Interface
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
from analyzers.integrated_bias_analyzer import IntegratedBiasAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize integrated bias analyzer (Harvard 40% + Columbia 35% + AllSides 20% + Sentiment 5%)
analyzer = IntegratedBiasAnalyzer()

# Database setup
DATABASE = 'bias_analysis.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            url TEXT,
            source_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            bias_score REAL,
            sentiment_polarity REAL,
            sentiment_subjectivity REAL,
            emotional_density REAL,
            certainty_ratio REAL,
            citation_count INTEGER,
            manual_bias_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    """Health check endpoint for deployment"""
    return jsonify({'status': 'healthy', 'service': 'echo-chamber-explorer'})

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Analyze content for bias"""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    if request.method == 'POST':
        # Get form data
        content = request.form.get('content', '').strip()
        title = request.form.get('title', '').strip()
        url = request.form.get('url', '').strip()
        source_name = request.form.get('source_name', '').strip()
        
        if not content:
            return render_template('analyze.html', error="Please enter some content to analyze")
        
        # Perform bias analysis
        results = analyzer.analyze_bias(content, title, url)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert article
        cursor.execute('''
            INSERT INTO articles (title, content, url, source_name)
            VALUES (?, ?, ?, ?)
        ''', (title, content, url, source_name))
        
        article_id = cursor.lastrowid
        
        # Insert analysis results
        cursor.execute('''
            INSERT INTO analysis_results 
            (article_id, bias_score, sentiment_polarity, sentiment_subjectivity, 
             emotional_density, certainty_ratio, citation_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            results['bias_score'],
            results.get('analysis_details', {}).get('sentiment_analysis', {}).get('polarity', 0.0),
            results.get('analysis_details', {}).get('sentiment_analysis', {}).get('subjectivity', 0.0),
            len(results.get('analysis_details', {}).get('bias_indicators_found', {})) / 100.0,  # Approximate emotional density
            0.5,  # Default certainty ratio - not directly available in integrated analyzer
            results.get('analysis_details', {}).get('source_diversity', {}).get('total_sources', 0)
        ))
        
        conn.commit()
        conn.close()
        
        return render_template('results.html', 
                             results=results, 
                             content=content,
                             title=title,
                             url=url,
                             source_name=source_name)

@app.route('/history')
def history():
    """View analysis history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.title, a.source_name, a.created_at,
               ar.bias_score, ar.sentiment_polarity, ar.manual_bias_rating
        FROM articles a
        LEFT JOIN analysis_results ar ON a.id = ar.article_id
        ORDER BY a.created_at DESC
        LIMIT 50
    ''')
    
    articles = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', articles=articles)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for bias analysis"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    results = analyzer.analyze_bias(data['content'], data.get('title', ''), data.get('url', ''))
    return jsonify(results)

@app.route('/stats')
def stats():
    """View analysis statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total articles
    cursor.execute('SELECT COUNT(*) as total_articles FROM articles')
    total_articles = cursor.fetchone()['total_articles']
    
    cursor.execute('''
        SELECT AVG(bias_score) as avg_bias, 
               MIN(bias_score) as min_bias,
               MAX(bias_score) as max_bias
        FROM analysis_results
    ''')
    bias_stats = cursor.fetchone()
    
    # Get bias distribution
    cursor.execute('''
        SELECT 
            CASE 
                WHEN bias_score < -0.6 THEN 'Very High Left'
                WHEN bias_score < -0.3 THEN 'High Left'
                WHEN bias_score < -0.1 THEN 'Low Left'
                WHEN bias_score < 0.1 THEN 'Minimal'
                WHEN bias_score < 0.3 THEN 'Low Right'
                WHEN bias_score < 0.6 THEN 'High Right'
                ELSE 'Very High Right'
            END as bias_category,
            COUNT(*) as count
        FROM analysis_results
        GROUP BY bias_category
        ORDER BY bias_score
    ''')
    
    bias_distribution = cursor.fetchall()
    conn.close()
    
    return render_template('stats.html', 
                         total_articles=total_articles,
                         bias_stats=bias_stats,
                         bias_distribution=bias_distribution)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
