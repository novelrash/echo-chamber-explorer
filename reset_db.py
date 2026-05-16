#!/usr/bin/env python3
"""
Reset database with correct schema
"""
import sqlite3
import os

DATABASE = 'bias_analysis.db'

def reset_database():
    # Remove old database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("🗑️ Removed old database")
    
    # Create new database with correct schema
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            url TEXT,
            source_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analysis results table (matching original app expectations)
    cursor.execute('''
        CREATE TABLE analysis_results (
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
    print("✅ Database reset with correct schema")

if __name__ == "__main__":
    reset_database()
