#!/usr/bin/env python3
"""
Enhanced Echo Chamber Explorer - Simplified Version
Copies working routes from original app and adds LangChain features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append('/mnt/c/Users/User')

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime

# Try to import enhanced analyzer, fallback to original
try:
    from analyzers.langchain_enhanced_analyzer import LangChainEnhancedAnalyzer
    analyzer = LangChainEnhancedAnalyzer()
    print("✅ LangChain agents loaded")
except Exception as e:
    print(f"⚠️ LangChain agents not available: {e}")
    from analyzers.integrated_bias_analyzer import IntegratedBiasAnalyzer
    analyzer = IntegratedBiasAnalyzer()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

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
    
    # Analysis results table with enhanced columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            bias_score REAL,
            sentiment_polarity REAL,
            sentiment_subjectivity REAL,
            emotional_density REAL,
            certainty_ratio REAL,
            manual_rating INTEGER,
            agent_research TEXT,
            source_credibility REAL,
            fact_check_results TEXT,
            enhanced_bias_indicators TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    ''')
    
    conn.commit()
    conn.close()

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
            return render_template('analyze.html', error="Content is required")
        
        try:
            # Store article
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO articles (title, content, url, source_name)
                VALUES (?, ?, ?, ?)
            ''', (title, content, url, source_name))
            article_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Run analysis (enhanced if available, otherwise original)
            if hasattr(analyzer, 'analyze_with_agents'):
                results = analyzer.analyze_with_agents(content, url, title)
            else:
                results = analyzer.analyze_bias(content, title, url)
            
            # Store results
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results (
                    article_id, bias_score, sentiment_polarity, sentiment_subjectivity,
                    emotional_density, certainty_ratio, agent_research, source_credibility,
                    fact_check_results, enhanced_bias_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_id,
                results.get('bias_score', 0),
                results.get('sentiment_polarity', 0),
                results.get('sentiment_subjectivity', 0),
                results.get('emotional_density', 0),
                results.get('certainty_ratio', 0),
                json.dumps(results.get('agent_research', [])),
                results.get('source_credibility', {}).get('score') if results.get('source_credibility') else None,
                json.dumps(results.get('fact_check', [])),
                json.dumps(results.get('enhanced_bias_indicators', {}))
            ))
            conn.commit()
            conn.close()
            
            # Use enhanced template if we have enhanced results, otherwise original
            if results.get('agent_research') or results.get('source_credibility'):
                return render_template('results_enhanced.html', 
                                     results=results, 
                                     article_id=article_id,
                                     title=title,
                                     url=url)
            else:
                return render_template('results.html', 
                                     results=results, 
                                     article_id=article_id,
                                     title=title,
                                     url=url,
                                     source_name=source_name)
            
        except Exception as e:
            return render_template('analyze.html', error=f"Analysis error: {str(e)}")

@app.route('/history')
def history():
    """View analysis history"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.title, a.url, a.source_name, a.created_at,
               r.bias_score
        FROM articles a
        LEFT JOIN analysis_results r ON a.id = r.article_id
        ORDER BY a.created_at DESC
        LIMIT 50
    ''')
    
    articles = []
    for row in cursor.fetchall():
        articles.append({
            'id': row[0],
            'title': row[1] or 'Untitled',
            'url': row[2],
            'source_name': row[3],
            'created_at': row[4],
            'bias_score': row[5]
        })
    
    conn.close()
    return render_template('history.html', articles=articles)

@app.route('/stats')
def stats():
    """View analysis statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Basic stats
    cursor.execute('SELECT COUNT(*) FROM articles')
    total_articles = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(bias_score) FROM analysis_results WHERE bias_score IS NOT NULL')
    avg_bias = cursor.fetchone()[0]
    
    # Enhanced stats if available
    cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE agent_research IS NOT NULL AND agent_research != "[]"')
    agent_analyses = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(source_credibility) FROM analysis_results WHERE source_credibility IS NOT NULL')
    avg_credibility = cursor.fetchone()[0]
    
    conn.close()
    
    # Structure data to match template expectations
    bias_stats = {
        'avg_bias': avg_bias,
        'total_articles': total_articles
    }
    
    return render_template('stats.html', 
                         total_articles=total_articles,
                         bias_stats=bias_stats,
                         agent_analyses=agent_analyses,
                         avg_credibility=avg_credibility)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for bias analysis"""
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        if hasattr(analyzer, 'analyze_with_agents'):
            results = analyzer.analyze_with_agents(content)
        else:
            results = analyzer.analyze_bias(content)
        
        return jsonify({
            'bias_score': results.get('bias_score', 0),
            'sentiment_polarity': results.get('sentiment_polarity', 0),
            'sentiment_subjectivity': results.get('sentiment_subjectivity', 0),
            'enhanced_features': bool(results.get('agent_research'))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Starting Enhanced Echo Chamber Explorer...")
    print(f"🤖 AI agents available: {hasattr(analyzer, 'analyze_with_agents')}")
    app.run(debug=True, host='0.0.0.0', port=5000)
