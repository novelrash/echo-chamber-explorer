#!/usr/bin/env python3
"""
Echo Chamber Explorer - Bias Analysis Web Interface
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
import hashlib
from datetime import datetime
from analyzers.integrated_bias_analyzer import IntegratedBiasAnalyzer
from analyzers.llm_bias_analyzer import LLMBiasAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Keyword analyzer — always available
keyword_analyzer = IntegratedBiasAnalyzer()

# LLM analyzer — optional, requires ANTHROPIC_API_KEY
try:
    llm_analyzer = LLMBiasAnalyzer()
    print("LLM analyzer initialized (Claude Haiku)")
except ValueError:
    llm_analyzer = None
    print("LLM analyzer disabled — set ANTHROPIC_API_KEY to enable")

DATABASE = 'bias_analysis.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            url TEXT,
            source_name TEXT,
            content_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            bias_score REAL,
            sentiment_polarity REAL,
            sentiment_subjectivity REAL,
            manual_bias_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            llm_score REAL,
            confidence TEXT,
            lean TEXT,
            word_choice_analysis TEXT,
            framing_analysis TEXT,
            sources_analysis TEXT,
            headline_analysis TEXT,
            flagged_phrases TEXT,
            limitations TEXT,
            model TEXT,
            error TEXT,
            truncated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    ''')

    # Migrate existing databases that predate these columns
    for table, column, definition in [
        ('articles', 'content_hash', 'TEXT'),
        ('llm_analysis_results', 'truncated', 'INTEGER DEFAULT 0'),
    ]:
        try:
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
        except sqlite3.OperationalError:
            pass  # column already exists

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _llm_row_to_dict(row) -> dict:
    """Reconstruct an llm_results dict from a cached DB row."""
    flagged = json.loads(row['flagged_phrases']) if row['flagged_phrases'] else []
    reasoning = None
    if any([row['word_choice_analysis'], row['framing_analysis'],
            row['sources_analysis'], row['headline_analysis']]):
        reasoning = {
            'word_choice': row['word_choice_analysis'],
            'framing': row['framing_analysis'],
            'sources': row['sources_analysis'],
            'headline': row['headline_analysis'],
        }
    truncated = bool(row['truncated']) if 'truncated' in row.keys() else False
    return {
        'score': row['llm_score'],
        'confidence': row['confidence'],
        'lean': row['lean'],
        'reasoning': reasoning,
        'flagged_phrases': flagged,
        'limitations': row['limitations'],
        'model': row['model'],
        'truncated': truncated,
        'error': row['error'],
    }


def _get_cached_llm_result(content_hash: str) -> dict | None:
    """Return the most recent successful LLM result for this content hash, or None."""
    conn = get_db_connection()
    row = conn.execute(
        '''SELECT l.* FROM llm_analysis_results l
           JOIN articles a ON a.id = l.article_id
           WHERE a.content_hash = ? AND l.error IS NULL
           ORDER BY l.created_at DESC LIMIT 1''',
        (content_hash,)
    ).fetchone()
    conn.close()
    return _llm_row_to_dict(row) if row else None


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'echo-chamber-explorer',
        'llm_enabled': llm_analyzer is not None
    })


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'GET':
        return render_template('analyze.html')

    content = request.form.get('content', '').strip()
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    source_name = request.form.get('source_name', '').strip()

    if not content:
        return render_template('analyze.html', error="Please enter some content to analyze")

    content_hash = _content_hash(content)

    # Run keyword analysis (always, no API cost)
    keyword_results = keyword_analyzer.analyze_bias(content, title, url)

    # LLM analysis — check cache first to avoid redundant API calls
    llm_results = None
    if llm_analyzer:
        llm_results = _get_cached_llm_result(content_hash)
        if llm_results is None:
            llm_results = llm_analyzer.analyze(
                content,
                title=title or None,
                source=source_name or None
            )

    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO articles (title, content, url, source_name, content_hash) VALUES (?, ?, ?, ?, ?)',
        (title, content, url, source_name, content_hash)
    )
    article_id = cursor.lastrowid

    cursor.execute(
        '''INSERT INTO analysis_results
           (article_id, bias_score, sentiment_polarity, sentiment_subjectivity)
           VALUES (?, ?, ?, ?)''',
        (
            article_id,
            keyword_results['bias_score'],
            keyword_results.get('analysis_details', {})
                           .get('methodology_scores', {})
                           .get('sentiment', {})
                           .get('details', {})
                           .get('polarity', 0.0),
            keyword_results.get('analysis_details', {})
                           .get('methodology_scores', {})
                           .get('sentiment', {})
                           .get('details', {})
                           .get('subjectivity', 0.0),
        )
    )

    if llm_results:
        reasoning = llm_results.get('reasoning') or {}
        cursor.execute(
            '''INSERT INTO llm_analysis_results
               (article_id, llm_score, confidence, lean,
                word_choice_analysis, framing_analysis,
                sources_analysis, headline_analysis,
                flagged_phrases, limitations, model, error, truncated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                article_id,
                llm_results.get('score'),
                llm_results.get('confidence'),
                llm_results.get('lean'),
                reasoning.get('word_choice'),
                reasoning.get('framing'),
                reasoning.get('sources'),
                reasoning.get('headline'),
                json.dumps(llm_results.get('flagged_phrases', [])),
                llm_results.get('limitations'),
                llm_results.get('model'),
                llm_results.get('error'),
                int(llm_results.get('truncated', False)),
            )
        )

    conn.commit()
    conn.close()

    return render_template(
        'results.html',
        keyword_results=keyword_results,
        llm_results=llm_results,
        content=content,
        title=title,
        url=url,
        source_name=source_name
    )


@app.route('/history')
def history():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.title, a.source_name, a.created_at,
               ar.bias_score,
               lr.llm_score, lr.confidence, lr.lean
        FROM articles a
        LEFT JOIN analysis_results ar ON a.id = ar.article_id
        LEFT JOIN llm_analysis_results lr ON a.id = lr.article_id
        ORDER BY a.created_at DESC
        LIMIT 50
    ''')

    articles = cursor.fetchall()
    conn.close()
    return render_template('history.html', articles=articles)


@app.route('/stats')
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM articles')
    total_articles = cursor.fetchone()['total']

    cursor.execute('''
        SELECT AVG(bias_score) as avg_bias,
               MIN(bias_score) as min_bias,
               MAX(bias_score) as max_bias
        FROM analysis_results
    ''')
    keyword_stats = cursor.fetchone()

    cursor.execute('''
        SELECT AVG(llm_score) as avg_bias,
               MIN(llm_score) as min_bias,
               MAX(llm_score) as max_bias
        FROM llm_analysis_results
        WHERE llm_score IS NOT NULL
    ''')
    llm_stats = cursor.fetchone()

    cursor.execute('''
        SELECT
            CASE
                WHEN bias_score < -0.6 THEN 'Very High Left'
                WHEN bias_score < -0.3 THEN 'High Left'
                WHEN bias_score < -0.1 THEN 'Low Left'
                WHEN bias_score < 0.1  THEN 'Minimal'
                WHEN bias_score < 0.3  THEN 'Low Right'
                WHEN bias_score < 0.6  THEN 'High Right'
                ELSE 'Very High Right'
            END as bias_category,
            COUNT(*) as count
        FROM analysis_results
        GROUP BY bias_category
    ''')
    bias_distribution = cursor.fetchall()

    conn.close()

    return render_template(
        'stats.html',
        total_articles=total_articles,
        keyword_stats=keyword_stats,
        llm_stats=llm_stats,
        bias_distribution=bias_distribution
    )


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'content field is required'}), 400

    content = data['content']
    title = data.get('title', '')
    url = data.get('url', '')
    source = data.get('source', '')

    keyword_results = keyword_analyzer.analyze_bias(content, title, url)

    llm_results = None
    if llm_analyzer:
        llm_results = _get_cached_llm_result(_content_hash(content))
        if llm_results is None:
            llm_results = llm_analyzer.analyze(content, title=title or None, source=source or None)

    return jsonify({
        'keyword_analysis': keyword_results,
        'llm_analysis': llm_results,
        'llm_enabled': llm_analyzer is not None
    })


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
