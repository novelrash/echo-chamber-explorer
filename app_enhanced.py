#!/usr/bin/env python3
"""
Enhanced Echo Chamber Explorer with LangChain Agents
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append('/mnt/c/Users/User')

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime
from analyzers.langchain_enhanced_analyzer import LangChainEnhancedAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize enhanced analyzer with LangChain agents
analyzer = LangChainEnhancedAnalyzer()

DATABASE = 'bias_analysis.db'

def init_db():
    """Initialize database with enhanced columns"""
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
    
    # Enhanced analysis results table
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
    """Enhanced analysis page with AI agents"""
    if request.method == 'POST':
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
            
            # Enhanced analysis with agents
            results = analyzer.analyze_with_agents(content, url, title)
            
            # Store enhanced results
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
            
            return render_template('results_enhanced.html', 
                                 results=results, 
                                 article_id=article_id,
                                 title=title,
                                 url=url)
            
        except Exception as e:
            return render_template('analyze.html', error=f"Analysis error: {str(e)}")
    
    return render_template('analyze.html')

@app.route('/results/<int:article_id>')
def view_results(article_id):
    """View enhanced analysis results"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get article and results
    cursor.execute('''
        SELECT a.*, r.* FROM articles a
        LEFT JOIN analysis_results r ON a.id = r.article_id
        WHERE a.id = ?
    ''', (article_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Article not found", 404
    
    # Parse enhanced results
    results = {
        'bias_score': row[11],
        'sentiment_polarity': row[12],
        'sentiment_subjectivity': row[13],
        'emotional_density': row[14],
        'certainty_ratio': row[15],
        'agent_research': json.loads(row[17]) if row[17] else [],
        'source_credibility': {'score': row[18]} if row[18] else None,
        'fact_check': json.loads(row[19]) if row[19] else [],
        'enhanced_bias_indicators': json.loads(row[20]) if row[20] else {}
    }
    
    return render_template('results_enhanced.html',
                         results=results,
                         article_id=article_id,
                         title=row[1],
                         url=row[3])

@app.route('/history')
def history():
    """View analysis history"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.title, a.url, a.source_name, a.created_at,
               r.bias_score, r.source_credibility
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
            'bias_score': row[5],
            'source_credibility': row[6]
        })
    
    conn.close()
    return render_template('history.html', articles=articles)

@app.route('/stats')
def stats():
    """Enhanced statistics page"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Basic stats
    cursor.execute('SELECT COUNT(*) FROM articles')
    total_articles = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(bias_score), AVG(source_credibility) FROM analysis_results')
    avg_bias, avg_credibility = cursor.fetchone()
    
    # Agent usage stats
    cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE agent_research IS NOT NULL')
    agent_analyses = cursor.fetchone()[0]
    
    conn.close()
    
    stats_data = {
        'total_articles': total_articles,
        'average_bias_score': round(avg_bias or 0, 3),
        'average_credibility': round(avg_credibility or 0, 3),
        'agent_enhanced_analyses': agent_analyses
    }
    
    return render_template('stats.html', stats=stats_data)

@app.route('/api/quick-analyze', methods=['POST'])
def quick_analyze():
    """API endpoint for quick analysis"""
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        results = analyzer.analyze_with_agents(content)
        return jsonify({
            'bias_score': results.get('bias_score', 0),
            'bias_category': analyzer.get_bias_category(results.get('bias_score', 0)),
            'agent_research_count': len(results.get('agent_research', [])),
            'fact_checks': len(results.get('fact_check', [])),
            'enhanced_indicators': len([v for v in results.get('enhanced_bias_indicators', {}).values() if v])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Starting Enhanced Echo Chamber Explorer with LangChain Agents...")
    print("🤖 AI agents available:", analyzer.agents_available)
    app.run(debug=True, host='0.0.0.0', port=5000)
